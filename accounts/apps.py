from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """Import extensions when app is ready"""
        # Import OpenAPI extensions for drf-spectacular
        try:
            from . import spectacular_extensions  # noqa: F401
        except ImportError:
            pass  # drf-spectacular might not be installed
