from rest_framework import serializers
from documents.models import Lease, Booking, Document
from properties.serializers import PropertyListSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name="serializers"


class LeaseSerializer(serializers.ModelSerializer):
    """Serializer for Lease model"""
    property_details = PropertyListSerializer(source='property_ref', read_only=True)
    tenant_details = UserBasicSerializer(source='tenant', read_only=True)
    is_active = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Lease
        fields = [
            'id', 'property_ref', 'property_details', 'tenant', 'tenant_details',
            'start_date', 'end_date', 'rent_amount', 'status', 'created_at',
            'is_active', 'duration_days'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Validate lease dates"""
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    property_details = PropertyListSerializer(source='property_ref', read_only=True)
    tenant_details = UserBasicSerializer(source='tenant', read_only=True)
    nights = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'property_ref', 'property_details', 'tenant', 'tenant_details',
            'check_in', 'check_out', 'total_amount', 'status', 'created_at',
            'nights', 'is_upcoming'
        ]
        read_only_fields = ['created_at']
    
    def validate(self, data):
        """Validate booking dates"""
        if data.get('check_out') and data.get('check_in'):
            if data['check_out'] <= data['check_in']:
                raise serializers.ValidationError("Check-out date must be after check-in date")
        return data


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    file_url = serializers.ReadOnlyField()
    file_size = serializers.ReadOnlyField()
    lease_details = LeaseSerializer(source='lease', read_only=True)
    booking_details = BookingSerializer(source='booking', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'lease', 'lease_details', 'booking', 'booking_details',
            'property_ref', 'user', 'file_name', 'file', 'file_url', 
            'file_size', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at', 'file_url', 'file_size']
    
    def validate(self, data):
        """Ensure at least one relationship is set"""
        if not any([data.get('lease'), data.get('booking'), data.get('property_ref'), data.get('user')]):
            raise serializers.ValidationError(
                "Document must be associated with a lease, booking, property, or user"
            )
        return data


class LeaseCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating leases"""
    tenant = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    
    class Meta:
        model = Lease
        fields = ['property_ref', 'tenant', 'start_date', 'end_date', 'rent_amount', 'status']
        extra_kwargs = {
            'status': {'required': False, 'read_only': True}  # Status is set automatically
        }


class BookingCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating bookings"""
    tenant = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    
    class Meta:
        model = Booking
        fields = ['property_ref', 'tenant', 'check_in', 'check_out', 'total_amount', 'status']
        extra_kwargs = {
            'status': {'required': False, 'read_only': True}  # Status is set automatically
        }
