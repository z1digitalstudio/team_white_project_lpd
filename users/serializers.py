from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


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
                    raise serializers.ValidationError("User account is disabled")
            else:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must provide username and password")

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password confirmation.
    All fields have length validations:
    - Username: 3-30 characters (letters and numbers only)
    - Password: 8-128 characters
    - First name: 2-150 characters (required)
    - Last name: 2-150 characters (optional)
    - Email: 5-150 characters (required)
    """
    password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=8,
        max_length=128,
        style={'input_type': 'password'},
        help_text="Password must be between 8 and 128 characters"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    email = serializers.EmailField(
        required=True, 
        allow_blank=False,
        min_length=5,
        max_length=150
    )
    first_name = serializers.CharField(
        required=True, 
        allow_blank=False, 
        min_length=2,
        max_length=150
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        min_length=2,
        max_length=150
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'username': {'min_length': 3, 'max_length': 30, 'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'password': {'write_only': True, 'required': True},
            'password_confirm': {'write_only': True, 'required': True}
        }
    
    def validate_username(self, value):
        """
        Validate that username contains only letters and numbers and has valid length.
        """
        import re
        if not value or not value.strip():
            raise serializers.ValidationError("Username is required and cannot be empty.")
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if len(value) > 30:
            raise serializers.ValidationError("Username cannot exceed 30 characters.")
        # Only allow alphanumeric characters (letters and numbers)
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters and numbers. No special characters allowed."
            )
        return value
    
    def validate_email(self, value):
        """
        Validate that email is provided, not empty, and has valid length.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Email is required and cannot be empty.")
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError("Email must be at least 5 characters long.")
        if len(value) > 150:
            raise serializers.ValidationError("Email cannot exceed 150 characters.")
        return value
    
    def validate_first_name(self, value):
        """
        Validate that first_name is provided, not empty, and has valid length.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required and cannot be empty.")
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        if len(value) > 150:
            raise serializers.ValidationError("First name cannot exceed 150 characters.")
        return value
    
    def validate_last_name(self, value):
        """
        Validate that last_name has valid length if provided.
        """
        if value:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError("Last name must be at least 2 characters long if provided.")
            if len(value) > 150:
                raise serializers.ValidationError("Last name cannot exceed 150 characters.")
        return value
    
    def validate_password(self, value):
        """
        Validate password length.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if len(value) > 128:
            raise serializers.ValidationError("Password cannot exceed 128 characters.")
        return value
    
    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
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

