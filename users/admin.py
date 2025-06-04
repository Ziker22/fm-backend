from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User




class UserAdmin(BaseUserAdmin):
    """
    Custom User admin that includes the UserProfile inline.
    """

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number')
    list_select_related = ('profile',)
    
    def get_phone_number(self, instance):
        """
        Return the phone number from the user's profile.
        """
        return instance.profile.phone_number if hasattr(instance, 'profile') else ''
    
    get_phone_number.short_description = 'Phone Number'
    
    def get_inline_instances(self, request, obj=None):
        """
        Only show the profile inline when editing an existing user.
        """
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    """
    list_display = ( 'phone_number', 'default_location')
    search_fields = ('phone_number',)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
