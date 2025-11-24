from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse
from .models import Blog, Post
from .serializers import BlogSerializer, PostSerializer, PostCreateSerializer
from .permissions import IsOwnerOrSuperuser, IsOwnerOrSuperuserForBlog


class PostPagination(PageNumberPagination):
    """
    Custom pagination for posts - 5 items per page.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100


class BlogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for blog management with owner-based permissions.
    """
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperuserForBlog]
    
    def get_queryset(self):
        # Superusers can see all blogs, others only their own
        if self.request.user.is_superuser:
            return Blog.objects.all()
        return Blog.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a blog. Each user can only have one blog.
        """
        # Check if user already has a blog
        if hasattr(request.user, 'blog'):
            return Response(
                {
                    'error': 'User already has a blog',
                    'message': 'Each user can only have one blog. Use PUT or PATCH to update your existing blog.',
                    'existing_blog_id': request.user.blog.id,
                    'existing_blog_url': request.build_absolute_uri(
                        reverse('blog-detail', kwargs={'pk': request.user.blog.id})
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        # Automatically assign user to blog
        serializer.save(user=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for post management with custom permissions and actions.
    Posts are paginated with 5 items per page.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperuser]
    pagination_class = PostPagination
    
    def get_queryset(self):
        # Any authenticated user can see all posts
        return Post.objects.all()
    
    def get_serializer_class(self):
        # Use different serializer for create/update operations
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_blog = Blog.objects.filter(user=request.user).first()
        if not user_blog:
            blog = Blog.objects.create(
                user=request.user,
                title=f"Blog de {request.user.username}",
                bio=f"Blog personal de {request.user.username}"
            )
            user_blog = blog
        
        post = serializer.save(blog=user_blog)
        
        # Return response using PostSerializer to show tag names
        response_serializer = PostSerializer(post)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        
        # Return response using PostSerializer to show tag names
        response_serializer = PostSerializer(post)
        return Response(response_serializer.data)
    
    def perform_create(self, serializer):
        # This method is no longer used, but kept for compatibility
        pass
    
    @action(detail=False, methods=['get'])
    def published(self, request):
        """
        Endpoint to get only published posts (paginated, 5 per page).
        """
        posts = self.get_queryset().filter(is_published=True)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """
        Endpoint to filter posts by tag name (paginated, 5 per page).
        """
        tag_name = request.query_params.get('tag', None)
        if tag_name:
            posts = self.get_queryset().filter(tags__name__icontains=tag_name)
        else:
            posts = self.get_queryset()
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

