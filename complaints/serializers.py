from rest_framework import serializers
from django.contrib.auth import get_user_model
from complaints.models import Complaint, ComplaintResponse, Feedback
from properties.serializers import PropertyListSerializer

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields
        ref_name="serializers"


class ComplaintResponseSerializer(serializers.ModelSerializer):
    """Serializer for complaint responses"""
    responder_details = UserBasicSerializer(source='responder', read_only=True)
    
    class Meta:
        model = ComplaintResponse
        fields = [
            'id', 'complaint', 'responder', 'responder_details',
            'response_type', 'message', 'is_visible_to_user', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Set the responder as the current user
        validated_data['responder'] = self.context['request'].user
        return super().create(validated_data)


class ComplaintSerializer(serializers.ModelSerializer):
    """Serializer for reading complaint data"""
    user_details = UserBasicSerializer(source='user', read_only=True)
    property_details = PropertyListSerializer(source='property', read_only=True)
    resolved_by_details = UserBasicSerializer(source='resolved_by', read_only=True)
    responses = ComplaintResponseSerializer(many=True, read_only=True)
    is_resolved = serializers.ReadOnlyField()
    days_open = serializers.ReadOnlyField()
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'user', 'user_details', 'property', 'property_details',
            'title', 'description', 'category', 'priority', 'status', 'rating',
            'created_at', 'updated_at', 'resolved_at', 'resolved_by', 'resolved_by_details',
            'responses', 'is_resolved', 'days_open'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at']


class ComplaintCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating complaints"""
    
    class Meta:
        model = Complaint
        fields = [
            'property', 'title', 'description', 'category', 'priority', 'rating'
        ]
    
    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        # Set the user as the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ComplaintStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating complaint status (staff only)"""
    
    class Meta:
        model = Complaint
        fields = ['status', 'resolved_by']
        read_only_fields = ['resolved_by']
    
    def update(self, instance, validated_data):
        # Set resolved_by when status changes to resolved
        if validated_data.get('status') == 'resolved':
            validated_data['resolved_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for feedback"""
    user_details = UserBasicSerializer(source='user', read_only=True)
    property_details = PropertyListSerializer(source='property', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_details', 'property', 'property_details',
            'feedback_type', 'title', 'message', 'rating', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        # Set the user as the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating feedback"""
    
    class Meta:
        model = Feedback
        fields = ['property', 'feedback_type', 'title', 'message', 'rating']
    
    def validate_rating(self, value):
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value