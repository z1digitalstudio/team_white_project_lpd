from django.db import models
from django.conf import settings
from django.utils.text import slugify
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
        ordering = ['-created_at']  # Ordenar por fecha de creación descendente
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
        ordering = ['-created_at', 'name']  # Ordenar por fecha de creación descendente y nombre alfabéticamente
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
        ordering = ['-published_at', '-created_at']  # Ordenar por fecha de publicación
        indexes = [
            models.Index(fields=['blog']),
            models.Index(fields=['is_published']),
            models.Index(fields=['slug']),
            models.Index(fields=['-published_at', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        """
        Override save method to automatically generate slug from title.
        If slug already exists, append a number to make it unique.
        """
        if not self.slug:
            self.slug = slugify(self.title)
            # If slug already exists, add a number
            original_slug = self.slug
            counter = 1
            while Post.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title