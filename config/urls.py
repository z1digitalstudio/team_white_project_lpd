from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    """
    API Root view that shows all available endpoints.
    """
    return Response({
        'users': request.build_absolute_uri(reverse('user-list')),
        'blogs': request.build_absolute_uri(reverse('blog-list')),
        'posts': request.build_absolute_uri(reverse('post-list')),
        'tags': request.build_absolute_uri(reverse('tag-list')),
    })


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