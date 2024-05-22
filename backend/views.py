from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from channels.generic.websocket import AsyncWebsocketConsumer
import json

from .models import Topic
from .serializers import TopicSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=data['access'],
            httponly=True,
            secure=False,  # Set to True in production
            samesite='Lax',
        )
        response.set_cookie(
            key='refresh_token',
            value=data['refresh'],
            httponly=True,
            secure=False,  # Set to True in production
            samesite='Lax',
        )
        return response

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'Refresh token not found in cookies'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'refresh': refresh_token})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=data['access'],
            httponly=True,
            secure=False,  # Set to True in production
            samesite='Lax',
        )
        return response


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



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass
    
    def _build_chain(self, history):
        converter = {
            'User': 'user',
            'LLM' : 'ai'
        }
        prompt = ChatPromptTemplate.from_messages([
          ("system", "You are a helpful assistant."),
          *[(converter[h['sender']], h['message']) for h in history],
          ("user", "{input}"),
        ])

        llm = ChatOpenAI(model="gpt-4o")

        output_parser = StrOutputParser()
        # Chain
        chain = prompt | llm.with_config({"run_name": "model"}) | output_parser.with_config({"run_name": "Assistant"})

        return chain

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        history = text_data_json.get("history", [])
        print(history)
        
        chain = self._build_chain(history[0]['messages'])

        try:
            # Stream the response
            async for chunk in chain.astream_events({'input': message}, version="v1", include_names=["Assistant"]):
                if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
                    await self.send(text_data=json.dumps(chunk))

        except Exception as e:
            print(e)