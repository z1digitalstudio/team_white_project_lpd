# core/admin.py
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from tinymce.widgets import TinyMCE
from tinymce.models import HTMLField
from django.db import models
from .models import Blog, Post, Tag

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """
    Admin configuration for Blog model with user-based permissions.
    """
    list_display = ('title', 'user')
    search_fields = ('title', 'user__username')
    
    def save_model(self, request, obj, form, change):
        # Automatically assign user to blog if creating new blog
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        # Superusers can see all blogs, others only their own
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    """
    Admin configuration for Post model with import/export functionality.
    """
    list_display = ('title', 'blog', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at', 'tags', 'blog')
    search_fields = ('title', 'content', 'excerpt')
    list_editable = ('is_published',)
    filter_horizontal = ('tags',)
    
    # Configure TinyMCE for HTML content
    formfield_overrides = {
        HTMLField: {'widget': TinyMCE()},
    }
    
    def save_model(self, request, obj, form, change):
        # Automatically assign user's blog if not superuser
        if not request.user.is_superuser:
            obj.blog = Blog.objects.filter(user=request.user).first()
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        # Filter posts based on user permissions
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(blog__user=request.user)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tag model.
    """
    list_display = ('name', 'posts_count')
    search_fields = ('name',)
    
    def posts_count(self, obj):
        """Display number of posts using this tag"""
        return obj.posts.count()
    posts_count.short_description = 'Posts'