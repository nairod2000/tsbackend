from .models import Topic
from .serializers import TopicSerializer
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

import logging

logger = logging.getLogger(__name__)


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
