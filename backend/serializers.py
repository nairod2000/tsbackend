from rest_framework import serializers
from .models import Topic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        print("Starting validation")
        username = attrs.get('username')
        password = attrs.get('password')
        print(f"Username: {username}, Password: {password}")

        if username is None or password is None:
            raise serializers.ValidationError('Username and password are required')

        user = authenticate(username=username, password=password)
        print(f"User: {user}")

        if user is None:
            raise serializers.ValidationError('Invalid credentials')

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        print(f"Token Data: {data}")

        return data
    

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
    

    