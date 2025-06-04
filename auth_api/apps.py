from django.apps import AppConfig


class AuthApiConfig(AppConfig):
    """
    Configuration for the auth_api application.
    
    This app provides JWT-based authentication services for the Family Map backend,
    including login, token refresh, and logout functionality. It also includes
    reusable permission classes and middleware for securing GraphQL endpoints.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_api'
    verbose_name = 'Authentication API'
