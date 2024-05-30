#from langchain_openai import ChatOpenAI
#from langchain_core.prompts import ChatPromptTemplate
#from langchain_core.output_parsers import StrOutputParser
#from channels.generic.websocket import AsyncWebsocketConsumer
#import json
#from django.conf import settings
#from rest_framework_simplejwt.tokens import UntypedToken
#from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
#from django.contrib.auth.models import User
#from urllib.parse import parse_qs
#import logging
#
#logger = logging.getLogger(__name__)
#
#class ChatConsumer(AsyncWebsocketConsumer):
#
#    async def connect(self):
#        self.user = await self.authenticate(self.scope)
#        if self.user:
#            await self.accept()
#        else:
#            await self.close()
#
#    async def disconnect(self, close_code):
#        pass
#
#    def _build_chain(self, history):
#        converter = {
#            'User': 'user',
#            'LLM': 'ai'
#        }
#        prompt = ChatPromptTemplate.from_messages([
#            ("system", "You are a helpful assistant."),
#            *[(converter[h['sender']], h['message']) for h in history],
#            ("user", "{input}"),
#        ])
#
#        llm = ChatOpenAI(model="gpt-4o")
#
#        output_parser = StrOutputParser()
#        # Chain
#        chain = prompt | llm.with_config({"run_name": "model"}) | output_parser.with_config({"run_name": "Assistant"})
#
#        return chain
#
#    async def receive(self, text_data):
#        text_data_json = json.loads(text_data)
#        message = text_data_json["message"]
#        history = text_data_json.get("history", [])
#        print(history)
#
#        chain = self._build_chain(history[0]['messages'])
#
#        try:
#            # Stream the response
#            async for chunk in chain.astream_events({'input': message}, version="v1", include_names=["Assistant"]):
#                if chunk["event"] in ["on_parser_start", "on_parser_stream"]:
#                    await self.send(text_data=json.dumps(chunk))
#
#        except Exception as e:
#            print(e)
#
#    @staticmethod
#    async def authenticate(scope):
#        query_string = scope["query_string"].decode()
#        params = parse_qs(query_string)
#        token = params.get("token", [None])[0]
#        logger.warning(params)
#
#        if token is None:
#            return None
#
#        try:
#            UntypedToken(token)
#        except (InvalidToken, TokenError) as e:
#            logger.error(f"Token validation error: {e}")
#            return None
#
#        try:
#            user = User.objects.get(id=UntypedToken(token)["user_id"])
#            return user
#        except User.DoesNotExist:
#            return None
#