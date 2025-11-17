from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from blog.models import Blog
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer
from .permissions import IsSuperuserOrReadOnly


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user management with registration and login endpoints.
    Only superusers can see all users, regular users can only see themselves.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperuserOrReadOnly]
    
    def get_queryset(self):
        # Superusers can see all users, regular users only see themselves
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        Register new users with automatic blog creation.
        Blog title is provided in the registration data.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create blog for new user with the provided title
            blog_title = getattr(user, '_blog_title', f"Blog de {user.username}")
            Blog.objects.create(
                user=user,
                title=blog_title
            )
            # Create token for user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        User login with token generation.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

