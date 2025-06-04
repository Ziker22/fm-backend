"""
URL configuration for family_map project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Main URL patterns:
- admin/: Django admin interface
- graphql/: GraphQL API endpoint for all API interactions including user registration
- media/: Serves user-uploaded files like profile pictures

The GraphQL endpoint provides access to all API operations including:
- User registration and authentication
- User profile management
- Place-related operations
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from strawberry.django.views import GraphQLView

from family_map.schema import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', GraphQLView.as_view(schema=schema), name='graphql'),
]

# Add media URL configuration for handling user-uploaded files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
