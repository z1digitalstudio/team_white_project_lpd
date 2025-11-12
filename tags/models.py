from django.db import models


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

