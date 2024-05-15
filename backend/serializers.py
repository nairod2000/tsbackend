from rest_framework import serializers
from .models import Topic

class TopicSerializer(serializers.ModelSerializer):
    subtopics = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'name', 'parent', 'created_by', 'created_at', 'updated_at', 'subtopics']
