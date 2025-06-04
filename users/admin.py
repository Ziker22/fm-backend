from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from users.models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile that will be displayed on the User admin page.
    This allows editing profile information along with the user.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """
    Custom User admin that includes the UserProfile inline.
    """
    inlines = (UserProfileInline,)
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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    """
    list_display = ('user', 'phone_number', 'default_location')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('user',)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
