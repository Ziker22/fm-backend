from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView

from family_map.schema import schema
from auth_api.middleware import JWTAuthMiddleware

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', JWTAuthMiddleware(csrf_exempt(GraphQLView.as_view(
        schema=schema,
        graphiql=settings.DEBUG))

    ), name='graphql'),
]

# Add media URL configuration for handling user-uploaded files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
