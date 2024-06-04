from .models import Topic, UserMaterial, Prompt, Material, Chat, ChatMessage
from .serializers import TopicSerializer, UserMaterialSerializer, UpdateReviewSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from rest_framework.response import Response
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
import urllib

import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_materials_sm2(request):
    user = request.user
    topic_name = request.query_params.get('topic', '')
    
    if topic_name:
        topic_name = urllib.parse.unquote(topic_name)

    now = timezone.now()

    # Get materials filtered by user and topic
    user_materials = UserMaterial.objects.filter(user=user, material__topic__name=topic_name).order_by('next_review')
    print(user_materials)
    
    due_materials = [um for um in user_materials if um.next_review <= now]
    not_due_materials = [um for um in user_materials if um.next_review > now]
    sorted_user_materials = due_materials + not_due_materials
    
    serializer = UserMaterialSerializer(sorted_user_materials, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def eval_material(request):
    # turn this into the eval endpoint
    user = request.user
    serializer = UpdateReviewSerializer(data=request.data)
    if serializer.is_valid():
        material_id = serializer.validated_data['material_id']
        correct = serializer.validated_data['correct']
        user_material = get_object_or_404(UserMaterial, user=user, material_id=material_id)
        
        if correct:
            user_material.ccount += 1
            user_material.repetition += 1
            if user_material.repetition == 1:
                user_material.interval = 1  # 1 day
                user_material.next_review = timezone.now() + timedelta(days=1)
            elif user_material.repetition == 2:
                user_material.interval = 3  # 3 days
                user_material.next_review = timezone.now() + timedelta(days=3)
            else:
                user_material.interval *= user_material.easiness
                user_material.next_review = timezone.now() + timedelta(days=user_material.interval)
                user_material.easiness = max(1.3, user_material.easiness + 0.1)
        else:
            user_material.icount += 1
            user_material.repetition = 0
            user_material.interval = 0
            user_material.next_review = timezone.now() + timedelta(minutes=15)
            user_material.easiness = max(1.3, user_material.easiness - 0.2)
        
        user_material.last_reviewed = timezone.now()
        user_material.save()
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([permissions.IsAuthenticated])
def chat_view(request):
    '''The endpoint for continuing a chat.'''
    # need to get the id of the chat from the frontend
    # that chat needs to belong to the user

    # 1) get the chat
    # 2) create save the ChatMessage
    data = request.GET.get('data', '')
    data = json.loads(data)

    chat = Chat.objects.get()
    chat_message = ChatMessage.objects.create()

    response = StreamingHttpResponse(
        generate_chat_message(chat), 
        content_type='text/event-stream'
    )
    return response


@permission_classes([permissions.IsAuthenticated])
def chat_start_view(request):
    '''Begins a new chat.'''
    # ToDo: params need to be required (material)
    user_material = request.GET.get('material', '')
    user_material = json.loads(user_material)['material']

    material = Material.objects.get(pk=user_material['material'])

    # I dont think this is normalized
    # also, it will probably be better to have these saved to user_material
    # this is going to require a more through examination of how and where 
    # user materials are created and used.
    chat = Chat.objects.create(
        mode='eval' if user_material['learned'] else 'teach',
        topic=material.topic,
        material=material
    ).save()

    if chat.mode == 'eval':
        system_prompt_content = Prompt.objects.get(name='eval_system').content
        init_message_content = Prompt.objects.get(name='eval').content
    elif chat.mode == 'teach':
        system_prompt_content = Prompt.objects.get(name='learn_system').content
        init_message_content = Prompt.objects.get(name='learn').content

    # makes the system message loadable in build chain
    system_message = ChatMessage.objects.create(
        chat=chat,
        role='system',
        content=system_prompt_content,
        sequence=0
    )
    system_message.save()

    # makes the init message loadable in build chain
    init_message = ChatMessage.objects.create(
        chat=chat,
        role='user',
        content=init_message_content.format(material=material),
        sequence=1
    )
    init_message.save()

    response = StreamingHttpResponse(
       generate_chat_message(chat), 
       content_type="text/event-stream"
    )
    return response


def generate_chat_message(chat):
    chain = _build_chain(chat)
    chunks = list()

    for chunk in chain.stream():
        chunks.append(chunk)
        yield f"data: {json.dumps(chunk)}\n\n"

    chat_message = ChatMessage.objects.create(
        chat=chat,
        role='ai',
        content=''.join(chunks),
        sequence=len(ChatMessage.objects.get(chat=chat)) - 1 # strong feeling this will not work
    )
    chat_message.save()

    yield "data: {\"end\": true}\n\n"


def _build_chain(chat):
    
    message_qs = ChatMessage.objects.filter(chat=chat).order_by('sequence')

    prompt = ChatPromptTemplate.from_messages([
        *[(m.role, m.content) for m in message_qs],
    ])

    llm = ChatOpenAI(model="gpt-4o")
    output_parser = StrOutputParser()

    chain = prompt | llm.with_config({"run_name": "model"}) | output_parser.with_config({"run_name": "Assistant"})
    return chain


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_view(request):
    data = request.data
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email is already in use'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        username=data['email'],  # Using email as the username
        password=data['password']
    )
    user.save()
    
    response = Response(
        {'success': 'Account created successfully'}, 
        status=status.HTTP_201_CREATED
    )
    return response


# remove this
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    response = JsonResponse({'detail': 'Successfully logged out'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


class TopicListCreateView(generics.ListCreateAPIView):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Topic.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TopicRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Topic.objects.filter(created_by=self.request.user)
