from rest_framework import permissions
from users.permissions import IsSuperuserOrReadOnly

# Reuse the same permission class for tags
__all__ = ['IsSuperuserOrReadOnly']

