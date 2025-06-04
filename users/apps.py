from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """
        Connect signals when the app is ready.
        This ensures that the signal handlers in models.py are properly registered.
        """
        import users.models  # Import the models module to connect signals
