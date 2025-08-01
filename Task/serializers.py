from rest_framework import serializers
from .models import Task, Comment
from .serializers import CommentSerializer

class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True) 
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
        
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'username', 'body', 'created', 'updated']
        read_only_fields = ['id', 'task', 'username', 'created', 'updated']