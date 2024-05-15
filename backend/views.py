from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from rest_framework import generics
from .models import Topic
from .serializers import TopicSerializer

import logging

logger = logging.getLogger(__name__)


class TopicListCreateView(generics.ListCreateAPIView):
    serializer_class = TopicSerializer

    def get_queryset(self):
        # Here we can add filters based on the logged-in user in the future
        return Topic.objects.all()
    
    def create(self, request, *args, **kwargs):
        print('got in here')
        print(request.data)
        logger.info(request.data)  # Log the request data for debugging
        return super().create(request, *args, **kwargs)

class TopicRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer



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