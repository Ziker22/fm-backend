"""
JWT Authentication middleware for GraphQL requests.

This module provides a middleware for authenticating GraphQL requests using JWT tokens.
It extracts and verifies JWT tokens from the Authorization header and authenticates
users for GraphQL requests.

This middleware is designed to be used with Strawberry GraphQL, but can be adapted
for other GraphQL implementations as needed.
"""
from typing import Any, Optional, Callable, Dict

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from strawberry.django.context import StrawberryDjangoContext


class JWTAuthMiddleware:
    """
    Middleware for authenticating GraphQL requests using JWT tokens.
    
    This middleware extracts the JWT token from the Authorization header,
    verifies it using djangorestframework-simplejwt, and authenticates
    the user for the GraphQL context.
    
    Usage:
        # In your GraphQL view configuration
        from strawberry.django.views import GraphQLView
        from auth_api.middleware import JWTAuthMiddleware
        
        urlpatterns = [
            path('graphql/', GraphQLView.as_view(
                schema=schema,
                get_context=JWTAuthMiddleware(GraphQLView.get_context)
            ), name='graphql'),
        ]
    """
    
    def __init__(self, get_context: Callable[[HttpRequest, Dict[str, Any]], StrawberryDjangoContext]):
        """
        Initialize the middleware with a context builder function.
        
        Args:
            get_context: Function that builds the context for GraphQL requests
        """
        self.get_context = get_context
        self.jwt_auth = JWTAuthentication()
    
    def __call__(self, request: HttpRequest, context_value: Optional[Dict[str, Any]] = None, **kwargs) -> StrawberryDjangoContext:
        """
        Process the request, authenticate the user, and build the context.
        
        Args:
            request: The HTTP request
            context_value: Optional additional context values
            **kwargs: Additional keyword arguments (including response in test environment)
            
        Returns:
            StrawberryDjangoContext: The GraphQL context with authenticated user
        """
        # Ensure the user is set to AnonymousUser by default
        if not hasattr(request, 'user') or request.user is None:
            request.user = AnonymousUser()
        
        # Try to authenticate with JWT token
        if 'HTTP_AUTHORIZATION' in request.META:
            try:
                # Extract and verify the token
                validated_token = self.get_validated_token(request)
                if validated_token:
                    # Get the user from the validated token
                    # Handle both tuple return (user, auth) or direct user return
                    user_auth = self.jwt_auth.get_user(validated_token)
                    if isinstance(user_auth, tuple):
                        # If it returns a tuple (user, auth) as per documentation
                        request.user = user_auth[0]
                    else:
                        # If it directly returns the user object
                        request.user = user_auth
            except (InvalidToken, TokenError):
                # If token is invalid, keep the user as AnonymousUser
                pass
        
        # Build and return the context
        context_kwargs = context_value or {}
        # Pass response to get_context if it's provided (needed for tests)
        if 'response' in kwargs:
            context = self.get_context(request, context_kwargs, response=kwargs['response'])
        else:
            context = self.get_context(request, context_kwargs)
        return context
    
    def get_validated_token(self, request: HttpRequest) -> Optional[Any]:
        """
        Extract and validate the JWT token from the request.
        
        Args:
            request: The HTTP request
            
        Returns:
            Optional[Any]: The validated token or None if validation fails
            
        Raises:
            InvalidToken: If the token is invalid
            TokenError: If there's an error processing the token
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extract the raw token
        raw_token = auth_header.split(' ')[1]
        
        # Validate the token
        return self.jwt_auth.get_validated_token(raw_token)
