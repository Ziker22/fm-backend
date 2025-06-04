import strawberry
import typing
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from strawberry.django import auth
from strawberry import auto
from strawberry.types import Info
from strawberry.permission import BasePermission

from users.models import UserProfile, UserRole


class IsAdmin(BasePermission):
    """
    Permission class that only allows users with admin role to access the field.
    """
    message = "User is not authorized to access this resource"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        user = info.context.request.user
        if not user.is_authenticated:
            return False
        return hasattr(user, 'profile') and user.profile.is_admin


# Define User type
@strawberry.django.type(User)
class UserType:
    id: auto
    username: auto
    email: auto
    first_name: auto
    last_name: auto
    date_joined: auto
    is_active: auto
    profile: "UserProfileType"


# Define UserProfile type
@strawberry.django.type(UserProfile)
class UserProfileType:
    id: auto
    bio: auto
    phone_number: auto
    default_location: auto
    role: auto
    profile_picture: typing.Optional[str] = None

    @strawberry.field
    def profile_picture_url(self, root: UserProfile) -> typing.Optional[str]:
        if root.profile_picture:
            return root.profile_picture.url
        return None


# Input type for user registration
@strawberry.input
class UserRegistrationInput:
    username: str
    email: str
    password: str
    first_name: typing.Optional[str] = ""
    last_name: typing.Optional[str] = ""
    bio: typing.Optional[str] = ""
    phone_number: typing.Optional[str] = ""
    default_location: typing.Optional[str] = ""
    role: typing.Optional[str] = UserRole.FREEMIUM_USER


# Registration result type
@strawberry.type
class UserRegistrationResult:
    success: bool
    message: str
    user: typing.Optional[UserType] = None


# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, info: Info, input: UserRegistrationInput) -> UserRegistrationResult:
        # Check if username already exists
        if User.objects.filter(username=input.username).exists():
            return UserRegistrationResult(
                success=False,
                message="Username already exists"
            )
        
        # Check if email already exists
        if User.objects.filter(email=input.email).exists():
            return UserRegistrationResult(
                success=False,
                message="Email already exists"
            )
        
        try:
            # Create the user
            user = User.objects.create_user(
                username=input.username,
                email=input.email,
                password=input.password,
                first_name=input.first_name,
                last_name=input.last_name
            )
            
            # Update profile information
            profile = user.profile
            profile.bio = input.bio
            profile.phone_number = input.phone_number
            profile.default_location = input.default_location
            profile.role = input.role
            profile.save()
            
            return UserRegistrationResult(
                success=True,
                message="User registered successfully",
                user=user
            )
        except Exception as e:
            return UserRegistrationResult(
                success=False,
                message=f"Registration failed: {str(e)}"
            )


# Queries
@strawberry.type
class Query:
    @strawberry.field
    def me(self, info: Info) -> typing.Optional[UserType]:
        user = info.context.request.user
        if user.is_authenticated:
            return user
        return None
    
    @strawberry.django.field(permission_classes=[IsAdmin])
    def user(self, info: Info, id: strawberry.ID) -> typing.Optional[UserType]:
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
    
    @strawberry.django.field(permission_classes=[IsAdmin])
    def users(
        self, 
        info: Info, 
        username: typing.Optional[str] = None,
        role: typing.Optional[str] = None
    ) -> typing.List[UserType]:
        """
        Returns a list of all users. Only accessible by admins.
        Optional filters for username and role.
        """
        queryset = User.objects.all()
        
        # Apply filters if provided
        if username:
            queryset = queryset.filter(username__icontains=username)
        
        if role:
            queryset = queryset.filter(profile__role=role)
            
        return queryset


# Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
