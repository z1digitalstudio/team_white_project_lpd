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
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='blog',
        help_text="The user who owns this blog. Each user can have only one blog."
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Blog Title",
        help_text="The title of the blog"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Biography",
        help_text="A brief description or biography of the blog"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The date and time when the blog was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="The date and time when the blog was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Tag(models.Model):
    """
    Tag model for categorizing posts.
    Tags can be shared across multiple posts (ManyToMany relationship).
    """
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name="Tag Name",
        help_text="The name of the tag. Must be unique."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The date and time when the tag was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="The date and time when the tag was last updated"
    )

    class Meta:
        ordering = ['-created_at', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-created_at', 'name']),
        ]

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Post model representing a blog post.
    Each post belongs to a blog and can have multiple tags.
    
    Publishing behavior:
    - is_published: Boolean flag indicating if the post is published and visible.
    - published_at: DateTime automatically set when is_published changes to True
                    for the first time. Maintains the original publication date
                    if the post is unpublished and republished later.
    """
    blog = models.ForeignKey(
        Blog, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name="Blog",
        help_text="The blog this post belongs to"
    )
    title = models.CharField(
        max_length=250,
        verbose_name="Post Title",
        help_text="The title of the post"
    )
    slug = models.SlugField(
        max_length=260, 
        unique=True, 
        blank=True,
        verbose_name="URL Slug",
        help_text="URL-friendly version of the title. Auto-generated if not provided."
    )
    content = HTMLField(
        verbose_name="Content",
        help_text="The main content of the post (HTML format)"
    )
    excerpt = models.TextField(
        blank=True,
        verbose_name="Excerpt",
        help_text="A short summary or excerpt of the post"
    )
    cover = models.ImageField(
        upload_to='posts/covers/', 
        null=True, 
        blank=True,
        verbose_name="Cover Image",
        help_text="Cover image for the post"
    )
    tags = models.ManyToManyField(
        Tag, 
        related_name='posts', 
        blank=True,
        verbose_name="Tags",
        help_text="Tags associated with this post"
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name="Is Published",
        help_text="Whether the post is published and visible to the public"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="The date and time when the post was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="The date and time when the post was last updated"
    )
    published_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Published At",
        help_text="The date and time when the post was published"
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['blog']),
            models.Index(fields=['is_published']),
            models.Index(fields=['slug']),
            models.Index(fields=['-published_at', '-created_at']),
        ]

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
        Override save method to automatically generate slug from title
        and update published_at when post is published for the first time.
        Uses timestamp-based approach to avoid race conditions.
        """
        # Generate slug if not provided
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:  # Handle empty slug case
                base_slug = f"post-{int(timezone.now().timestamp())}"
            self.slug = self._generate_unique_slug(base_slug)
        
        # Update published_at when post is published for the first time
        if self.is_published and not self.published_at:
            # If publishing for the first time, set published_at to now
            self.published_at = timezone.now()
        # If unpublishing, keep published_at (maintains publication history)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title