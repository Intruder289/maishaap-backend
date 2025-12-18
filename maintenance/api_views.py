from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for maintenance requests
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