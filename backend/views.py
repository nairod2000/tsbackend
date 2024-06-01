from .models import Topic, Material, UserMaterial
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
from .models import Material
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
def update_review_count(request):
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
    data = request.GET.get('data', '')
    data = json.loads(data)
    response = StreamingHttpResponse(generate_chat(data['message'], data['history']), content_type='text/event-stream')
    return response


def generate_chat(message, history):
    chain = _build_chain(history)
    chunks = list()
    for chunk in chain.stream(message):
        chunks.append(chunk)
        yield f"data: {json.dumps(chunk)}\n\n"
    # save message here
    yield "data: {\"end\": true}\n\n"


def _build_chain(history):
    converter = {
        'User': 'user',
        'LLM': 'ai'
    }
    print('building chain...')
    print(history)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        *[(converter[h['sender']], h['message']) for h in history[0]['messages']],
        ("user", "{input}"),
    ])

    llm = ChatOpenAI(model="gpt-4o")
    output_parser = StrOutputParser()

    # Chain
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
