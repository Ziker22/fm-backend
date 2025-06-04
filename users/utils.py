from django.contrib.auth.models import User
from django.db import transaction
from typing import Optional, Tuple, Union

from users.models import UserRole


def create_admin_user(
    username: str, 
    email: str, 
    password: str, 
    first_name: str = "", 
    last_name: str = ""
) -> Tuple[User, bool, str]:
    """
    Creates a new user with admin role.
    
    Args:
        username: The username for the new admin user
        email: The email address for the new admin user
        password: The password for the new admin user
        first_name: Optional first name for the user
        last_name: Optional last name for the user
        
    Returns:
        Tuple containing:
        - User object (or None if creation failed)
        - Success status (boolean)
        - Message describing the result
    """
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return None, False, f"User with username '{username}' already exists"
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return None, False, f"User with email '{email}' already exists"
    
    try:
        with transaction.atomic():
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Set admin role
            profile = user.profile
            profile.role = UserRole.ADMIN
            profile.save()
            
            return user, True, "Admin user created successfully"
    except Exception as e:
        return None, False, f"Failed to create admin user: {str(e)}"


def promote_to_admin(user_identifier: Union[str, int]) -> Tuple[User, bool, str]:
    """
    Promotes an existing user to admin role.
    
    Args:
        user_identifier: Either a username (string) or user ID (int)
        
    Returns:
        Tuple containing:
        - User object (or None if promotion failed)
        - Success status (boolean)
        - Message describing the result
    """
    user = None
    
    # Find the user based on the identifier type
    try:
        if isinstance(user_identifier, int) or user_identifier.isdigit():
            user = User.objects.get(id=user_identifier)
        else:
            user = User.objects.get(username=user_identifier)
    except User.DoesNotExist:
        return None, False, f"User not found with identifier: {user_identifier}"
    
    # Check if user is already an admin
    if hasattr(user, 'profile') and user.profile.is_admin:
        return user, False, f"User '{user.username}' is already an admin"
    
    try:
        # Update user role to admin
        profile = user.profile
        profile.role = UserRole.ADMIN
        profile.save()
        
        return user, True, f"User '{user.username}' has been promoted to admin"
    except Exception as e:
        return None, False, f"Failed to promote user to admin: {str(e)}"


def is_admin(user: User) -> bool:
    """
    Checks if a user has admin role.
    
    Args:
        user: The User object to check
        
    Returns:
        Boolean indicating whether the user is an admin
    """
    if not user or not user.is_authenticated:
        return False
    
    return hasattr(user, 'profile') and user.profile.is_admin


def demote_from_admin(user_identifier: Union[str, int]) -> Tuple[User, bool, str]:
    """
    Demotes an admin user to regular freemium user.
    
    Args:
        user_identifier: Either a username (string) or user ID (int)
        
    Returns:
        Tuple containing:
        - User object (or None if demotion failed)
        - Success status (boolean)
        - Message describing the result
    """
    user = None
    
    # Find the user based on the identifier type
    try:
        if isinstance(user_identifier, int) or user_identifier.isdigit():
            user = User.objects.get(id=user_identifier)
        else:
            user = User.objects.get(username=user_identifier)
    except User.DoesNotExist:
        return None, False, f"User not found with identifier: {user_identifier}"
    
    # Check if user is not an admin
    if not hasattr(user, 'profile') or not user.profile.is_admin:
        return user, False, f"User '{user.username}' is not an admin"
    
    try:
        # Update user role to freemium user
        profile = user.profile
        profile.role = UserRole.FREEMIUM_USER
        profile.save()
        
        return user, True, f"User '{user.username}' has been demoted from admin"
    except Exception as e:
        return None, False, f"Failed to demote user from admin: {str(e)}"


def get_all_admins() -> list:
    """
    Returns a list of all admin users in the system.
    
    Returns:
        List of User objects with admin role
    """
    return User.objects.filter(profile__role=UserRole.ADMIN)
