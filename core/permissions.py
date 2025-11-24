from rest_framework import permissions



class BaseOwnerPermission(permissions.BasePermission):
    """
    Base permission class for owner-based permissions.
    Any authenticated user can view, but only owners or superusers can modify/delete.
    
    Subclasses must implement `get_owner(obj)` to specify how to get the owner from the object.
    """
    
    def has_permission(self, request, view):
        """All operations require authentication"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user can access the object"""
        # Authenticated users can view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Only owner or superuser can modify/delete
        if request.user.is_superuser:
            return True
        
        # Check if user is the owner
        owner = self.get_owner(obj)
        return owner == request.user
    
    def get_owner(self, obj):
        """
        Get the owner of the object.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_owner()")


class HasPostPermission(BaseOwnerPermission):
    """
    Permission for posts.
    Any authenticated user can view, but only owners (blog owners) or superusers can modify/delete.
    """
    
    def get_owner(self, obj):
        """Get the owner of the post (the blog owner)"""
        return obj.blog.user


class HasBlogPermission(BaseOwnerPermission):
    """
    Permission for blogs.
    Any authenticated user can view, but only owners or superusers can modify/delete.
    """
    
    def get_owner(self, obj):
        """Get the owner of the blog"""
        return obj.user


class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Permission to allow only superusers to modify objects.
    Regular users can only view.
    """
    
    def has_permission(self, request, view):
        """Check if user has permission for the view"""
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        
        # Regular users can only view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user has permission for the object"""
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
