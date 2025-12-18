from rest_framework import serializers
from .models import MaintenanceRequest


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = ['id', 'property', 'tenant', 'title', 'description', 'created_at']