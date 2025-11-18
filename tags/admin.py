from django.contrib import admin
from .models import Tag


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

