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
    bio = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"


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
    tags = models.ManyToManyField('tags.Tag', related_name='posts', blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug from title
        and set published_at when post is published for the first time.
        If slug already exists, append a number to make it unique.
        """
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            # If slug already exists, add a number
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Set published_at when post is published for the first time
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

