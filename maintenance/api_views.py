from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer
# Swagger documentation - using drf-spectacular (auto-discovery)
# Provide no-op decorator for backward compatibility with existing @swagger_auto_schema decorators
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
except ImportError:
    # drf-yasg not installed, use drf-spectacular instead
    # Decorators will be ignored - drf-spectacular auto-discovers endpoints
    def swagger_auto_schema(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class openapi:
        class Response:
            def __init__(self, *args, **kwargs):
                pass
        class Schema:
            def __init__(self, *args, **kwargs):
                pass
        class Items:
            def __init__(self, *args, **kwargs):
                pass
        class Contact:
            def __init__(self, *args, **kwargs):
                pass
        class License:
            def __init__(self, *args, **kwargs):
                pass
        class Info:
            def __init__(self, *args, **kwargs):
                pass
        TYPE_OBJECT = 'object'
        TYPE_STRING = 'string'
        TYPE_INTEGER = 'integer'
        TYPE_NUMBER = 'number'
        TYPE_BOOLEAN = 'boolean'
        TYPE_ARRAY = 'array'
        FORMAT_EMAIL = 'email'
        FORMAT_DATE = 'date'
        FORMAT_DATETIME = 'date-time'
        FORMAT_DECIMAL = 'decimal'
        FORMAT_URI = 'uri'
        FORMAT_UUID = 'uuid'
        IN_QUERY = 'query'
        IN_PATH = 'path'
        IN_BODY = 'body'
        IN_FORM = 'formData'
        IN_HEADER = 'header'
        
        # Create a proper Parameter class that stores arguments
        class Parameter:
            def __init__(self, name, in_, description=None, type=None, required=False, **kwargs):
                self.name = name
                self.in_ = in_
                self.description = description or ''
                self.type = type or 'string'
                self.required = required
                # Store all kwargs for compatibility
                for key, value in kwargs.items():
                    setattr(self, key, value)


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Maintenance Request management
    
    list: Get all maintenance requests (filtered by user role)
    retrieve: Get a specific maintenance request
    create: Create a new maintenance request
    update: Update a maintenance request
    partial_update: Partially update a maintenance request
    destroy: Delete a maintenance request
    
    MULTI-TENANCY: Data isolation based on user role
    - Property owners see maintenance requests for their properties
    - Tenants see only their own maintenance requests
    - Admins/staff see all maintenance requests
    """
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        MULTI-TENANCY: Filter queryset based on user role for data isolation
        - Property owners see maintenance requests for their properties
        - Tenants see only their own maintenance requests
        - Admins/staff see all maintenance requests
        """
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return MaintenanceRequest.objects.none()
        
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return MaintenanceRequest.objects.all()
        
        # Check if user is a property owner
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                # Property owners see maintenance requests for their properties
                return MaintenanceRequest.objects.filter(property__owner=user)
        except Profile.DoesNotExist:
            pass
        
        # Tenants see only their own maintenance requests
        return MaintenanceRequest.objects.filter(tenant=user)
    
    def perform_create(self, serializer):
        """Set tenant to current user when creating"""
        serializer.save(tenant=self.request.user)