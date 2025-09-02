from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information"""
    class Meta:
        model = User
        fields = ['username']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with author information"""
    author = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'text', 'timestamp', 'author']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts with author, comment count, and latest comments"""
    author = UserSerializer(source='user', read_only=True)
    comment_count = serializers.SerializerMethodField()
    latest_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'text', 'timestamp', 'author', 'comment_count', 'latest_comments']
    
    def get_comment_count(self, obj):
        """Get total number of comments for this post"""
        return obj.comments.count()
    
    def get_latest_comments(self, obj):
        """Get up to 3 latest comments for this post"""
        latest_comments = obj.comments.select_related('user').order_by('-timestamp')[:3]
        return CommentSerializer(latest_comments, many=True).data