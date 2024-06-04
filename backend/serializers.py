from rest_framework import serializers
from .models import Topic, UserMaterial
from django.contrib.auth.models import User
    

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