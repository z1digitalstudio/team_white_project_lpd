from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """
    API Root view that shows all available endpoints.
    Public endpoint - no authentication required.
    """
    base_url = request.build_absolute_uri('/api')
    response_data = {
        'message': 'Welcome to the Blog CMS API',
        'version': '1.0.0',
        'endpoints': {
            'users': f"{base_url}/users/",
            'blogs': f"{base_url}/blogs/",
            'posts': f"{base_url}/posts/",
            'tags': f"{base_url}/tags/",
        },
        'documentation': {
            'swagger': request.build_absolute_uri('/swagger/'),
            'redoc': request.build_absolute_uri('/redoc/'),
            'schema': f"{base_url}/schema/",
        }
    }
    
    # Only show authentication endpoints if user is not authenticated
    if not request.user.is_authenticated:
        response_data['authentication'] = {
            'register': f"{base_url}/users/register/",
            'login': f"{base_url}/users/login/",
        }
    
    return Response(response_data)


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('blog.urls')),
    path('api/', include('tags.urls')),
    path('api/api-auth/', include('rest_framework.urls')),
    
    # drf-spectacular URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)