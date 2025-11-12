from rest_framework import permissions


class IsOwnerOrSuperuser(permissions.BasePermission):
    """
    Custom permission to allow only owners or superusers to manage objects.
    Any authenticated user can view, but only owners can modify/delete.
    """
    def has_permission(self, request, view):
        # All operations require authentication
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Authenticated users can view (GET)
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Only owner or superuser can modify/delete
        if request.user.is_superuser:
            return True
        
        return obj.blog.user == request.user


class IsOwnerOrSuperuserForBlog(permissions.BasePermission):
    """
    Custom permission for blogs.
    Any authenticated user can view, but only owners can modify/delete.
    """
    def has_permission(self, request, view):
        # All operations require authentication
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Authenticated users can view (GET)
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Only owner or superuser can modify/delete
        if request.user.is_superuser:
            return True
        
        return obj.user == request.user

