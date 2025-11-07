from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Blog, Post, Tag
from .constants import (
    USER_ACCOUNT_DISABLED,
    INVALID_CREDENTIALS,
    MUST_PROVIDE_CREDENTIALS,
    USERNAME_ALPHANUMERIC_ONLY,
    PASSWORDS_DO_NOT_MATCH,
)


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.
    """
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError(USER_ACCOUNT_DISABLED)
            else:
                raise serializers.ValidationError(INVALID_CREDENTIALS)
        else:
            raise serializers.ValidationError(MUST_PROVIDE_CREDENTIALS)

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password confirmation.
    Username can only contain letters and numbers (no special characters).
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate_username(self, value):
        """
        Validate that username contains only letters and numbers.
        """
        import re
        # Only allow alphanumeric characters (letters and numbers)
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError(USERNAME_ALPHANUMERIC_ONLY)
        return value
    
    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(PASSWORDS_DO_NOT_MATCH)
        return data
    
    def create(self, validated_data):
        # Remove password_confirm before creating user
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (read-only fields).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tag data.
    """
    class Meta:
        model = Tag
        fields = ['id', 'name']

class BlogSerializer(serializers.ModelSerializer):
    """
    Serializer for blog data with nested user information.
    """
    user = UserSerializer(read_only=True)
    
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