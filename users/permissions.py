from rest_framework import permissions


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only superusers to modify objects.
    Regular users can only view.
    """
    def has_permission(self, request, view):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        
        # Regular users can only view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        
        # Regular users can only view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return False


class IsNotAuthenticated(permissions.BasePermission):
    """
    Permission to allow access only to unauthenticated users.
    Used for registration and login endpoints.
    """
    
    def has_permission(self, request, view):
        """Only allow access if user is NOT authenticated"""
        return not request.user.is_authenticated

