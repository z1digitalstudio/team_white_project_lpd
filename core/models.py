import random
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from tinymce.models import HTMLField

User = settings.AUTH_USER_MODEL

class Blog(models.Model):
    """
    Blog model representing a user's personal blog.
    Each user can have only one blog (OneToOne relationship).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='blog')
    title = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Ordenar por fecha de creación descendente

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Tag(models.Model):
    """
    Tag model for categorizing posts.
    Tags can be shared across multiple posts (ManyToMany relationship).
    """
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', 'name']  # Ordenar por fecha de creación descendente y nombre alfabéticamente

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Post model representing a blog post.
    Each post belongs to a blog and can have multiple tags.
    """
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    content = HTMLField()
    excerpt = models.TextField(blank=True)
    cover = models.ImageField(upload_to='posts/covers/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']  # Ordenar por fecha de publicación

    def _generate_unique_slug(self, base_slug):
        """
        Generate a unique slug using timestamp to avoid race conditions.
        Uses timestamp instead of counter to prevent conflicts in concurrent scenarios.
        
        Args:
            base_slug: The base slug generated from the title
            
        Returns:
            A unique slug that doesn't exist in the database
        """
        MAX_ATTEMPTS = 10  # Maximum number of attempts to generate unique slug
        
        # First try the base slug
        if not Post.objects.filter(slug=base_slug).exists():
            return base_slug
        
        # If base slug exists, append timestamp to make it unique
        timestamp = int(timezone.now().timestamp())
        unique_slug = f"{base_slug}-{timestamp}"
        
        # Check if timestamp-based slug is unique (should be very rare collision)
        attempts = 0
        while Post.objects.filter(slug=unique_slug).exists() and attempts < MAX_ATTEMPTS:
            # If collision occurs (extremely rare), add microseconds
            timestamp = int(timezone.now().timestamp() * 1000000)  # Include microseconds
            unique_slug = f"{base_slug}-{timestamp}"
            attempts += 1
        
        if attempts >= MAX_ATTEMPTS:
            # Fallback: use a combination of timestamp and random component
            # This should never happen in practice, but provides safety
            unique_slug = f"{base_slug}-{timestamp}-{random.randint(1000, 9999)}"
        
        return unique_slug
    
    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug from title.
        Uses timestamp-based approach to avoid race conditions.
        """
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:  # Handle empty slug case
                base_slug = f"post-{int(timezone.now().timestamp())}"
            self.slug = self._generate_unique_slug(base_slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title