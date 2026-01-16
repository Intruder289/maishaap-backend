from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Property, PropertyType, Region, District, Amenity, 
    PropertyImage, PropertyView, PropertyFavorite, PropertyAmenity, Room, Booking
)
from django.utils import timezone
from datetime import datetime


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for Region model"""
    
    class Meta:
        model = Region
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for District model"""
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'region', 'region_name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertyTypeSerializer(serializers.ModelSerializer):
    """Serializer for PropertyType model"""
    
    class Meta:
        model = PropertyType
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer for Amenity model"""
    
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'description', 'icon', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertyImageSerializer(serializers.ModelSerializer):
    """Serializer for PropertyImage model"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'image_url', 'caption', 'is_primary', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """Get the full URL for the image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class OwnerSerializer(serializers.ModelSerializer):
    """Serializer for property owner information"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']
    
    def get_full_name(self, obj):
        """Get owner's full name"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class PropertyListSerializer(serializers.ModelSerializer):
    """Serializer for property list view (lightweight)"""
    property_type = PropertyTypeSerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    owner = OwnerSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    amenities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'region', 'bedrooms', 'bathrooms',
            'rent_amount', 'rent_period', 'deposit_amount', 'visit_cost', 'status', 'size_sqft', 'is_furnished',
            'pets_allowed', 'primary_image', 'owner', 'is_favorited', 'amenities_count',
            'created_at', 'available_from', 'is_active', 'total_rooms', 'capacity'
        ]
    
    def get_primary_image(self, obj):
        """Get the primary image for the property"""
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image:
            return PropertyImageSerializer(primary_image, context=self.context).data
        return None
    
    def get_is_favorited(self, obj):
        """Check if property is favorited by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PropertyFavorite.objects.filter(
                user=request.user, 
                property=obj
            ).exists()
        return False
    
    def get_amenities_count(self, obj):
        """Get count of amenities for this property"""
        return obj.amenities.count()


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed property view"""
    property_type = PropertyTypeSerializer(read_only=True)
    region = RegionSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = OwnerSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    available_rooms = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'region', 'address',
            'latitude', 'longitude', 'bedrooms', 'bathrooms', 'size_sqft',
            'floor_number', 'total_floors', 'total_rooms', 'room_types',
            'capacity', 'venue_type', 'rent_amount', 'rent_period', 'deposit_amount',
            'utilities_included', 'visit_cost', 'status', 'is_featured', 'is_furnished',
            'pets_allowed', 'smoking_allowed', 'available_from', 'amenities',
            'images', 'owner', 'is_favorited', 'views_count', 'available_rooms',
            'created_at', 'updated_at', 'is_active'
        ]
    
    def get_is_favorited(self, obj):
        """Check if property is favorited by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return PropertyFavorite.objects.filter(
                user=request.user, 
                property=obj
            ).exists()
        return False
    
    def get_views_count(self, obj):
        """Get total views count for this property"""
        return obj.views.count()
    
    def get_available_rooms(self, obj):
        """Get available rooms for hotel and lodge properties"""
        # Only return available rooms for hotel and lodge properties
        property_type_name = obj.property_type.name.lower() if obj.property_type else ''
        if property_type_name not in ['hotel', 'lodge']:
            return []
        
        # Get query parameters for date filtering (optional)
        request = self.context.get('request')
        check_in_date = None
        check_out_date = None
        
        if request:
            check_in_str = request.query_params.get('check_in_date')
            check_out_str = request.query_params.get('check_out_date')
            
            if check_in_str:
                try:
                    check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
            
            if check_out_str:
                try:
                    check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
        
        # Get all rooms for this property
        rooms = Room.objects.filter(
            property_obj=obj,
            is_active=True
        ).order_by('room_number')
        
        # Filter available rooms
        available_rooms_list = []
        
        for room in rooms:
            # Basic availability check: status must be 'available'
            if room.status != 'available':
                continue
            
            # If room has a current booking, it's not available
            if room.current_booking:
                continue
            
            # If date range is provided, check for booking conflicts
            if check_in_date and check_out_date:
                # Check if room has any bookings that conflict with the requested dates
                conflicting_bookings = Booking.objects.filter(
                    property_obj=obj,
                    room_number=room.room_number,
                    booking_status__in=['pending', 'confirmed', 'checked_in'],
                    check_in_date__lt=check_out_date,
                    check_out_date__gt=check_in_date
                ).exists()
                
                if conflicting_bookings:
                    continue
            
            # Room is available, add to list
            available_rooms_list.append(room)
        
        # Serialize available rooms
        return RoomSerializer(available_rooms_list, many=True, context=self.context).data


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating properties"""
    amenities_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'property_type', 'region', 'address',
            'latitude', 'longitude', 'bedrooms', 'bathrooms', 'size_sqft',
            'floor_number', 'total_floors', 'total_rooms', 'room_types',
            'capacity', 'venue_type', 'rent_amount', 'rent_period', 'deposit_amount',
            'utilities_included', 'visit_cost', 'status', 'is_featured', 'is_furnished',
            'pets_allowed', 'smoking_allowed', 'available_from', 'amenities_ids',
            'is_active'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Custom validation"""
        floor_number = data.get('floor_number')
        total_floors = data.get('total_floors')
        
        if floor_number and total_floors and floor_number > total_floors:
            raise serializers.ValidationError(
                "Floor number cannot be greater than total floors."
            )
        
        return data
    
    def create(self, validated_data):
        """Create property with amenities"""
        amenities_ids = validated_data.pop('amenities_ids', [])
        
        # Set owner from request user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
            # Admin/staff created properties are auto-approved, others require approval
            if request.user.is_staff or request.user.is_superuser:
                validated_data['is_active'] = True
                validated_data['is_approved'] = True
                from django.utils import timezone
                validated_data['approved_by'] = request.user
                validated_data['approved_at'] = timezone.now()
            else:
                # Non-admin owners require approval
                validated_data['is_active'] = False
                validated_data['is_approved'] = False
        else:
            # Unauthenticated - require approval
            validated_data['is_active'] = False
            validated_data['is_approved'] = False
        
        property_instance = Property.objects.create(**validated_data)
        
        # Add amenities
        if amenities_ids:
            amenities = Amenity.objects.filter(id__in=amenities_ids)
            property_instance.amenities.set(amenities)
        
        return property_instance
    
    def update(self, instance, validated_data):
        """Update property with amenities"""
        amenities_ids = validated_data.pop('amenities_ids', None)
        
        # Update property fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update amenities if provided
        if amenities_ids is not None:
            amenities = Amenity.objects.filter(id__in=amenities_ids)
            instance.amenities.set(amenities)
        
        return instance


class PropertyImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading property images"""
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image', 'caption', 'is_primary', 'order']
        read_only_fields = ['id']
    
    def validate_property(self, value):
        """Validate that user owns the property"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if value.owner != request.user:
                raise serializers.ValidationError(
                    "You can only upload images for your own properties."
                )
        return value


class PropertyFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for property favorites"""
    property = PropertyListSerializer(read_only=True)
    
    class Meta:
        model = PropertyFavorite
        fields = ['id', 'property', 'created_at']
        read_only_fields = ['id', 'created_at']


class PropertyViewSerializer(serializers.ModelSerializer):
    """Serializer for property views (analytics)"""
    property_title = serializers.CharField(source='property.title', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PropertyView
        fields = ['id', 'property', 'property_title', 'user', 'user_name', 'ip_address', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']


class RoomSerializer(serializers.ModelSerializer):
    """Serializer for Room model - used for available rooms in property details"""
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'room_number', 'room_type', 'floor_number', 'capacity',
            'bed_type', 'amenities', 'base_rate', 'status', 'is_available'
        ]
        read_only_fields = ['id', 'status', 'is_available']
    
    def get_is_available(self, obj):
        """Check if room is currently available"""
        return obj.is_available


class PropertySearchSerializer(serializers.Serializer):
    """Serializer for property search parameters"""
    search = serializers.CharField(required=False, allow_blank=True)
    property_type = serializers.IntegerField(required=False)
    region = serializers.IntegerField(required=False)
    district = serializers.IntegerField(required=False, help_text="Filter by district ID")
    min_bedrooms = serializers.IntegerField(required=False, min_value=0)
    max_bedrooms = serializers.IntegerField(required=False, min_value=0)
    min_bathrooms = serializers.IntegerField(required=False, min_value=0)
    max_bathrooms = serializers.IntegerField(required=False, min_value=0)
    min_rent = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, min_value=0)
    max_rent = serializers.DecimalField(required=False, max_digits=10, decimal_places=2, min_value=0)
    is_furnished = serializers.BooleanField(required=False)
    pets_allowed = serializers.BooleanField(required=False)
    amenities = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    status = serializers.ChoiceField(
        choices=Property.PROPERTY_STATUS_CHOICES,
        required=False
    )
    
    def validate(self, data):
        """Validate search parameters"""
        min_bedrooms = data.get('min_bedrooms')
        max_bedrooms = data.get('max_bedrooms')
        
        if min_bedrooms and max_bedrooms and min_bedrooms > max_bedrooms:
            raise serializers.ValidationError(
                "min_bedrooms cannot be greater than max_bedrooms"
            )
        
        min_bathrooms = data.get('min_bathrooms')
        max_bathrooms = data.get('max_bathrooms')
        
        if min_bathrooms and max_bathrooms and min_bathrooms > max_bathrooms:
            raise serializers.ValidationError(
                "min_bathrooms cannot be greater than max_bathrooms"
            )
        
        min_rent = data.get('min_rent')
        max_rent = data.get('max_rent')
        
        if min_rent and max_rent and min_rent > max_rent:
            raise serializers.ValidationError(
                "min_rent cannot be greater than max_rent"
            )
        
        return data


class PropertyStatsSerializer(serializers.Serializer):
    """Serializer for property statistics"""
    total_properties = serializers.IntegerField()
    available_properties = serializers.IntegerField()
    rented_properties = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_favorites = serializers.IntegerField()
    average_rent = serializers.DecimalField(max_digits=10, decimal_places=2)
    properties_by_type = serializers.DictField()
    properties_by_region = serializers.DictField()