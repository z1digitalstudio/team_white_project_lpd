from rest_framework import viewsets, permissions
from .models import Tag
from .serializers import TagSerializer
from users.permissions import IsSuperuserOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tag management.
    Any authenticated user can create tags, but only superusers can modify/delete.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperuserOrReadOnly]

