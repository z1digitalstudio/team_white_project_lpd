from rest_framework import serializers
from .models import Blog, Post
from users.serializers import UserSerializer
from tags.serializers import TagSerializer


class BlogSerializer(serializers.ModelSerializer):
    """
    Serializer for blog data with nested user information.
    """
    user = UserSerializer(read_only=True)
    bio = serializers.CharField(required=True, allow_blank=False, min_length=1)
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'bio', 'user', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for post data with nested blog and tags information.
    """
    blog = BlogSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 
            'cover', 'tags', 'is_published', 'created_at', 
            'updated_at', 'published_at', 'blog'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating posts (simplified fields).
    """
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'cover', 
            'tags', 'is_published'
        ]

