from rest_framework import serializers
from .models import Topic, UserMaterial, ChatMessage, Chat
from django.contrib.auth.models import User
import urllib
    

class TopicSerializer(serializers.ModelSerializer):
    subtopics = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'parent', 'created_by', 'created_at', 'updated_at', 'subtopics']

        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            username=validated_data['email'],  # Using email as the username
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMaterial
        fields = ['material', 'ccount', 'icount', 'last_reviewed', 'interval', 'repetition', 'easiness', 'next_review', 'learned', 'id']


class UpdateReviewSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    correct = serializers.BooleanField()


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'content']


class ChatSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'messages']

    def get_messages(self, obj):
        messages = ChatMessage.objects.filter(chat=obj, sequence__gte=2)
        return ChatMessageSerializer(messages, many=True).data
    

class ChatCreateSerializer(serializers.ModelSerializer):
    topic = serializers.CharField()

    class Meta:
        model = Chat
        fields = ['id', 'mode', 'topic', 'user_material', 'starred']

    def create(self, validated_data):
        topic_name = validated_data.pop('topic')
        topic_name = urllib.parse.unquote(topic_name)
        topic = Topic.objects.get(name=topic_name)
        chat = Chat.objects.create(topic=topic, **validated_data)
        return chat
