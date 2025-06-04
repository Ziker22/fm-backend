import strawberry
import typing
from strawberry.django import auth
from strawberry import auto
from strawberry.types import Info

from users.models import User, UserRole
from auth_api.graphql.permissions import IsAuthenticated, IsAdmin


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
            user.bio = input.bio
            user.phone_number = input.phone_number
            user.default_location = input.default_location
            user.role = input.role
            user.save()
            
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
    @strawberry.field(permission_classes=[IsAuthenticated])
    def me(self, info: Info) -> typing.Optional[UserType]:
        try:
            return User.objects.get(id=info.context.request.user.id)
        except User.DoesNotExist:
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
            queryset = queryset.filter(role=role)
            
        return queryset
