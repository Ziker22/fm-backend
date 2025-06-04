import strawberry
import typing
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from strawberry.django import auth
from strawberry import auto
from strawberry.types import Info

from users.models import UserProfile


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
    
    @strawberry.django.field
    def user(self, info: Info, id: strawberry.ID) -> typing.Optional[UserType]:
        if not info.context.request.user.is_authenticated:
            return None
        
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None


# Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
