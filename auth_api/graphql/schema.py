"""
GraphQL schema for authentication-related operations.

This module defines GraphQL types and mutations for JWT-based authentication,
including login, token refresh, and logout operations. It provides a clean
separation between authentication logic and user management.
"""
import strawberry
import typing

from django.conf import settings
from django.contrib.auth import authenticate
from strawberry.types import Info
from rest_framework_simplejwt.tokens import RefreshToken

# JWT Token types
@strawberry.type
class JWTToken:
    """Represents a JWT token with its type and value."""
    token: str
    token_type: str = "access"
    expires_at: typing.Optional[str] = None


@strawberry.type
class TokenPair:
    """Represents a pair of access and refresh tokens."""
    access: JWTToken
    refresh: JWTToken


# Login input type
@strawberry.input
class LoginInput:
    """Input for the login mutation."""
    username: str
    password: str


# Define minimal User type for auth responses - renamed to AuthUserType
@strawberry.type
class AuthUserType:
    """Minimal user information returned in authentication responses."""
    id: strawberry.ID
    username: str
    email: typing.Optional[str] = None


# Login result type
@strawberry.type
class LoginResult:
    """Result of a login attempt."""
    success: bool
    message: str
    tokens: typing.Optional[TokenPair] = None
    user: typing.Optional[AuthUserType] = None


# Token refresh input
@strawberry.input
class RefreshTokenInput:
    """Input for the token refresh mutation."""
    refresh_token: str


# Token refresh result
@strawberry.type
class RefreshTokenResult:
    """Result of a token refresh attempt."""
    success: bool
    message: str
    tokens: typing.Optional[TokenPair] = None


# Logout input
@strawberry.input
class LogoutInput:
    """Input for the logout mutation."""
    refresh_token: str


# Logout result
@strawberry.type
class LogoutResult:
    """Result of a logout attempt."""
    success: bool
    message: str


# Auth mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> LoginResult:
        """
        Authenticate a user and return JWT tokens if successful.
        
        Args:
            info: GraphQL request info
            input: Login credentials
            
        Returns:
            LoginResult containing success status, message, tokens (if successful), and user info
        """
        user = authenticate(username=input.username, password=input.password)
        
        if user is None:
            return LoginResult(
                success=False,
                message="Invalid username or password"
            )
        
        if not user.is_active:
            return LoginResult(
                success=False,
                message="User account is disabled"
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Create token objects
        access = JWTToken(token=access_token, token_type="access")
        refresh = JWTToken(token=refresh_token, token_type="refresh")
        
        # Create a minimal UserType for the response - updated to use AuthUserType
        user_type = AuthUserType(
            id=strawberry.ID(str(user.id)),
            username=user.username,
            email=user.email
        )
        
        return LoginResult(
            success=True,
            message="Login successful",
            tokens=TokenPair(access=access, refresh=refresh),
            user=user_type
        )
    
    @strawberry.mutation
    def refresh_token(self, info: Info, input: RefreshTokenInput) -> RefreshTokenResult:
        """
        Refresh an access token using a valid refresh token.
        
        Args:
            info: GraphQL request info
            input: Refresh token input
            
        Returns:
            RefreshTokenResult containing success status, message, and new tokens if successful
        """
        try:
            refresh = RefreshToken(input.refresh_token)
            
            # Get new tokens
            access_token = str(refresh.access_token)
            
            # If ROTATE_REFRESH_TOKENS is True, we'll get a new refresh token
            if hasattr(refresh, 'get_token_backend'):
                if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                    refresh.set_jti()
                    refresh.set_exp()
                    refresh.set_iat()
                    
            refresh_token = str(refresh)
            
            # Create token objects
            access = JWTToken(token=access_token, token_type="access")
            refresh = JWTToken(token=refresh_token, token_type="refresh")
            
            return RefreshTokenResult(
                success=True,
                message="Token refreshed successfully",
                tokens=TokenPair(access=access, refresh=refresh)
            )
        except Exception as e:
            return RefreshTokenResult(
                success=False,
                message=f"Token refresh failed: {str(e)}"
            )
    
    @strawberry.mutation
    def logout(self, info: Info, input: LogoutInput) -> LogoutResult:
        """
        Logout a user by blacklisting their refresh token.
        
        Args:
            info: GraphQL request info
            input: Logout input containing the refresh token to blacklist
            
        Returns:
            LogoutResult containing success status and message
        """
        try:
            # Parse the token
            token = RefreshToken(input.refresh_token)
            
            # Blacklist the token
            token.blacklist()
            
            return LogoutResult(
                success=True,
                message="Logout successful"
            )
        except Exception as e:
            return LogoutResult(
                success=False,
                message=f"Logout failed: {str(e)}"
            )


# Empty Query type to satisfy Strawberry schema requirements
@strawberry.type
class Query:
    @strawberry.field
    def auth_service_info(self) -> str:
        """
        Provides information about the authentication service.
        This is a placeholder query to satisfy Strawberry schema requirements.
        
        Returns:
            String with service information
        """
        return "JWT Authentication Service"
