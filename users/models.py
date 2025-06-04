from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole:
    """
    Enum-like class defining user roles in the application.
    """
    ADMIN = 'admin'
    FREEMIUM_USER = 'freemium_user'
    
    CHOICES = [
        (ADMIN, 'Administrator'),
        (FREEMIUM_USER, 'Freemium User'),
    ]


class UserProfile(models.Model):
    """
    User profile model that extends Django's built-in User model.
    Contains additional user information specific to the family map application.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    default_location = models.CharField(max_length=255, blank=True, help_text="Default map center location")
    role = models.CharField(
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.FREEMIUM_USER,
        help_text="User's role in the application"
    )
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def is_admin(self):
        """
        Check if the user has admin role.
        """
        return self.role == UserRole.ADMIN


# Signal to create or update user profile when a user is created or updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update user profile when a user is created or updated.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
