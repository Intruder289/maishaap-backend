from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Custom throttle classes for specific endpoints
class SearchRateThrottle(UserRateThrottle):
    """Custom throttle for search endpoints"""
    rate = '30/minute'

from .models import (
    Property, PropertyType, Region, District, Amenity, 
    PropertyImage, PropertyView, PropertyFavorite, PropertyVisitPayment
)
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer, PropertyCreateUpdateSerializer,
    PropertyTypeSerializer, RegionSerializer, DistrictSerializer, AmenitySerializer,
    PropertyImageUploadSerializer, PropertyFavoriteSerializer,
    PropertySearchSerializer, PropertyStatsSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PropertyListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating properties
    MULTI-TENANCY: Owners only see their own properties, admins see all
    """
    queryset = Property.objects.select_related(
        'property_type', 'region', 'owner'
    ).prefetch_related('images', 'amenities').order_by('-created_at')
    
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'property_type': ['exact'],
        'region': ['exact'],
        'district': ['exact'],
        'bedrooms': ['exact', 'gte', 'lte'],
        'bathrooms': ['exact', 'gte', 'lte'],
        'rent_amount': ['gte', 'lte'],
        'status': ['exact'],
        'is_furnished': ['exact'],
        'pets_allowed': ['exact'],
        'is_featured': ['exact'],
    }
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['created_at', 'rent_amount', 'bedrooms', 'bathrooms']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PropertyCreateUpdateSerializer
        return PropertyListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_queryset(self):
        """
        MULTI-TENANCY: Filter properties by owner for data isolation
        - Property owners see only their own properties (including unapproved)
        - Tenants see only approved and active properties (for browsing/booking)
        - Admins/staff see all properties (including unapproved)
        - Unauthenticated users see only approved and active properties (public listing)
        """
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return super().get_queryset().none()
        
        queryset = super().get_queryset()
        
        # If user is authenticated and not admin/staff, check if they are a Property Owner
        if self.request.user.is_authenticated:
            if not (self.request.user.is_staff or self.request.user.is_superuser):
                # Check if user is a Property Owner (not a Tenant)
                from accounts.models import UserRole, CustomRole
                is_property_owner = UserRole.objects.filter(
                    user=self.request.user,
                    role__name__in=['Property Owner', 'Property owner']
                ).exists()
                
                # Also check profile role for backward compatibility
                if not is_property_owner and hasattr(self.request.user, 'profile'):
                    is_property_owner = self.request.user.profile.role == 'owner'
                
                # Only Property Owners see their own properties (including unapproved)
                # Tenants see only approved and active properties (for browsing/booking)
                if is_property_owner:
                    queryset = queryset.filter(owner=self.request.user)
                else:
                    # Tenants: only see approved and active properties
                    queryset = queryset.filter(is_active=True, is_approved=True)
            # Admin/staff: see all properties (no filter)
        else:
            # Unauthenticated users: only see approved and active properties
            queryset = queryset.filter(is_active=True, is_approved=True)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Get list of properties with filtering and search. Filter by region first, then district.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title, description, address", type=openapi.TYPE_STRING),
            openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('district', openapi.IN_QUERY, description="Filter by district ID (can be used with or without region filter)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('bedrooms', openapi.IN_QUERY, description="Filter by exact number of bedrooms", type=openapi.TYPE_INTEGER),
            openapi.Parameter('bedrooms__gte', openapi.IN_QUERY, description="Minimum number of bedrooms", type=openapi.TYPE_INTEGER),
            openapi.Parameter('bedrooms__lte', openapi.IN_QUERY, description="Maximum number of bedrooms", type=openapi.TYPE_INTEGER),
            openapi.Parameter('rent_amount__gte', openapi.IN_QUERY, description="Minimum rent amount", type=openapi.TYPE_NUMBER),
            openapi.Parameter('rent_amount__lte', openapi.IN_QUERY, description="Maximum rent amount", type=openapi.TYPE_NUMBER),
            openapi.Parameter('is_furnished', openapi.IN_QUERY, description="Filter furnished properties", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('pets_allowed', openapi.IN_QUERY, description="Filter pet-friendly properties", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by: created_at, -created_at, rent_amount, -rent_amount", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page (max 100)", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new property",
        request_body=PropertyCreateUpdateSerializer
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PropertyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific property
    """
    queryset = Property.objects.select_related(
        'property_type', 'region', 'owner'
    ).prefetch_related('images', 'amenities')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_object(self):
        obj = super().get_object()
        
        # Track property view
        if self.request.method == 'GET' and self.request.user.is_authenticated:
            PropertyView.objects.get_or_create(
                property=obj,
                user=self.request.user,
                defaults={
                    'ip_address': self.request.META.get('REMOTE_ADDR', ''),
                    'user_agent': self.request.META.get('HTTP_USER_AGENT', '')
                }
            )
        
        return obj
    
    def update(self, request, *args, **kwargs):
        """Only allow property owner to update"""
        obj = self.get_object()
        if obj.owner != request.user:
            return Response(
                {'error': 'You can only update your own properties.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Only allow property owner to delete"""
        obj = self.get_object()
        if obj.owner != request.user:
            return Response(
                {'error': 'You can only delete your own properties.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class PropertyTypeListAPIView(generics.ListCreateAPIView):
    """API view for property types"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PropertyTypeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for property type detail operations"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def update(self, request, *args, **kwargs):
        """Override update to handle partial updates properly"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)


class RegionListAPIView(generics.ListCreateAPIView):
    """API view for regions"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_description="Get list of all regions. Use this to get region IDs for filtering properties and districts.",
        operation_summary="List All Regions",
        manual_parameters=[
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of regions",
                schema=RegionSerializer(many=True)
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RegionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for region detail operations"""
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def update(self, request, *args, **kwargs):
        """Override update to handle partial updates properly"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)


class DistrictListAPIView(generics.ListCreateAPIView):
    """API view for districts"""
    queryset = District.objects.select_related('region').all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_description="Get list of districts. Filter by region using 'regions' parameter (comma-separated IDs or single ID) or 'region_id' (backward compatible).",
        manual_parameters=[
            openapi.Parameter(
                'regions',
                openapi.IN_QUERY,
                description="Filter by region ID(s). Can be a single ID or comma-separated IDs (e.g., '1' or '1,2,3')",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'region_id',
                openapi.IN_QUERY,
                description="Filter by region ID (backward compatible, use 'regions' for new code)",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter districts by region(s) if region_id or regions parameter is provided"""
        queryset = District.objects.select_related('region').all()
        
        # Support both 'region_id' (backward compatible) and 'regions' (new parameter)
        region_id = self.request.query_params.get('region_id', None)
        regions_param = self.request.query_params.get('regions', None)
        
        # If 'regions' parameter is provided, use it (can be comma-separated IDs or single ID)
        if regions_param:
            try:
                # Try to split by comma for multiple region IDs
                region_ids = [int(r.strip()) for r in regions_param.split(',') if r.strip()]
                if region_ids:
                    queryset = queryset.filter(region_id__in=region_ids)
            except (ValueError, TypeError):
                # If parsing fails, try as single ID
                try:
                    region_id = int(regions_param)
                    queryset = queryset.filter(region_id=region_id)
                except (ValueError, TypeError):
                    pass  # Invalid format, return all districts
        # Fallback to 'region_id' for backward compatibility
        elif region_id:
            try:
                queryset = queryset.filter(region_id=int(region_id))
            except (ValueError, TypeError):
                pass  # Invalid format, return all districts
        
        return queryset


class DistrictDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for district detail operations"""
    queryset = District.objects.select_related('region').all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AmenityListAPIView(generics.ListCreateAPIView):
    """API view for amenities"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AmenityDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for amenity detail operations"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def update(self, request, *args, **kwargs):
        """Override update to handle partial updates properly"""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)


class PropertyToggleStatusAPIView(generics.UpdateAPIView):
    """API view for toggling property active status"""
    queryset = Property.objects.all()
    serializer_class = PropertyCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        property_obj = self.get_object()
        is_active = request.data.get('is_active', not property_obj.is_active)
        
        property_obj.is_active = is_active
        # Also toggle status for visual consistency
        if is_active:
            # Activate - set to available
            if property_obj.status == 'unavailable':
                property_obj.status = 'available'
        else:
            # Deactivate - set to unavailable
            property_obj.status = 'unavailable'
        
        property_obj.save()
        property_obj.refresh_status_from_activity()
        
        return Response({
            'success': True,
            'message': f'Property {"activated" if is_active else "deactivated"} successfully',
            'is_active': property_obj.is_active,
            'status': property_obj.status
        })


class PropertyDeleteAPIView(generics.DestroyAPIView):
    """API view for deleting properties"""
    queryset = Property.objects.all()
    serializer_class = PropertyCreateUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        property_obj = self.get_object()
        property_title = property_obj.title
        property_obj.delete()
        
        return Response({
            'success': True,
            'message': f'Property "{property_title}" deleted successfully'
        })


class PropertyImageUploadAPIView(generics.CreateAPIView):
    """API view for uploading property images"""
    serializer_class = PropertyImageUploadSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Explicitly set parsers for form data
    
    @swagger_auto_schema(
        operation_description="Upload an image for a property. Use multipart/form-data content type.",
        operation_summary="Upload Property Image",
        request_body=None,  # Explicitly set to None to avoid conflict with manual_parameters
        consumes=['multipart/form-data'],  # Explicitly set content type
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Image file to upload'
            ),
            openapi.Parameter(
                'property',
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='Property ID'
            ),
            openapi.Parameter(
                'caption',
                openapi.IN_FORM,
                type=openapi.TYPE_STRING,
                required=False,
                description='Image caption (optional, max 200 characters)'
            ),
            openapi.Parameter(
                'is_primary',
                openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description='Set as primary image (default: false)'
            ),
            openapi.Parameter(
                'order',
                openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=False,
                description='Display order (default: 0)'
            ),
        ],
        responses={
            201: openapi.Response(
                description="Image uploaded successfully",
                schema=PropertyImageUploadSerializer
            ),
            400: "Validation error",
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MyPropertiesAPIView(generics.ListAPIView):
    """API view for user's own properties"""
    serializer_class = PropertyListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return Property.objects.none()
        
        return Property.objects.filter(owner=self.request.user).select_related(
            'property_type', 'region'
        ).prefetch_related('images', 'amenities').order_by('-created_at')


@swagger_auto_schema(
    method='post',
    operation_description="Toggle favorite status of a property",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'property_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Property ID')
        }
    ),
    responses={
        200: openapi.Response(
            description="Success",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_favorited': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    """Toggle favorite status of a property"""
    property_id = request.data.get('property_id')
    
    if not property_id:
        return Response(
            {'error': 'property_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        property_obj = Property.objects.get(id=property_id)
    except Property.DoesNotExist:
        return Response(
            {'error': 'Property not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    favorite, created = PropertyFavorite.objects.get_or_create(
        user=request.user,
        property=property_obj
    )
    
    if not created:
        favorite.delete()
        is_favorited = False
        message = "Property removed from favorites"
    else:
        is_favorited = True
        message = "Property added to favorites"
    
    return Response({
        'is_favorited': is_favorited,
        'message': message
    })


class FavoritePropertiesAPIView(generics.ListAPIView):
    """API view for user's favorite properties"""
    serializer_class = PropertyFavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return PropertyFavorite.objects.none()
        
        return PropertyFavorite.objects.filter(user=self.request.user).select_related(
            'property__property_type', 'property__region', 'property__owner'
        ).prefetch_related('property__images', 'property__amenities').order_by('-created_at')


@swagger_auto_schema(
    method='post',
    operation_description="Advanced property search with multiple filters",
    request_body=PropertySearchSerializer,
    responses={200: PropertyListSerializer(many=True)}
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
@throttle_classes([SearchRateThrottle])
def property_search(request):
    """
    Advanced property search API
    MULTI-TENANCY: Owners only see their own properties, admins see all
    """
    serializer = PropertySearchSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Start with all properties
    queryset = Property.objects.select_related(
        'property_type', 'region', 'owner'
    ).prefetch_related('images', 'amenities')
    
    # MULTI-TENANCY: Filter by owner for data isolation
    # Property owners see only their own properties (including unapproved)
    # Tenants see only approved and active properties (for browsing/booking)
    if request.user.is_authenticated:
        if not (request.user.is_staff or request.user.is_superuser):
            # Check if user is a Property Owner (not a Tenant)
            from accounts.models import UserRole
            is_property_owner = UserRole.objects.filter(
                user=request.user,
                role__name__in=['Property Owner', 'Property owner']
            ).exists()
            
            # Also check profile role for backward compatibility
            if not is_property_owner and hasattr(request.user, 'profile'):
                is_property_owner = request.user.profile.role == 'owner'
            
            # Only Property Owners see their own properties (including unapproved)
            # Tenants see only approved and active properties (for browsing/booking)
            if is_property_owner:
                queryset = queryset.filter(owner=request.user)
            else:
                # Tenants: only see approved and active properties
                queryset = queryset.filter(is_active=True, is_approved=True)
        # Admin/staff: see all properties (no filter)
    else:
        # Unauthenticated users: only see approved and active properties
        queryset = queryset.filter(is_active=True, is_approved=True)
    
    # Apply filters
    search_data = serializer.validated_data
    
    # Text search
    search_query = search_data.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Property type filter
    property_type = search_data.get('property_type')
    if property_type:
        queryset = queryset.filter(property_type_id=property_type)
    
    # Region filter
    region = search_data.get('region')
    if region:
        queryset = queryset.filter(region_id=region)
    
    # District filter
    district = search_data.get('district')
    if district:
        queryset = queryset.filter(district_id=district)
    
    # Bedroom filters
    min_bedrooms = search_data.get('min_bedrooms')
    if min_bedrooms is not None:
        queryset = queryset.filter(bedrooms__gte=min_bedrooms)
    
    max_bedrooms = search_data.get('max_bedrooms')
    if max_bedrooms is not None:
        queryset = queryset.filter(bedrooms__lte=max_bedrooms)
    
    # Bathroom filters
    min_bathrooms = search_data.get('min_bathrooms')
    if min_bathrooms is not None:
        queryset = queryset.filter(bathrooms__gte=min_bathrooms)
    
    max_bathrooms = search_data.get('max_bathrooms')
    if max_bathrooms is not None:
        queryset = queryset.filter(bathrooms__lte=max_bathrooms)
    
    # Rent filters
    min_rent = search_data.get('min_rent')
    if min_rent is not None:
        queryset = queryset.filter(rent_amount__gte=min_rent)
    
    max_rent = search_data.get('max_rent')
    if max_rent is not None:
        queryset = queryset.filter(rent_amount__lte=max_rent)
    
    # Boolean filters
    is_furnished = search_data.get('is_furnished')
    if is_furnished is not None:
        queryset = queryset.filter(is_furnished=is_furnished)
    
    pets_allowed = search_data.get('pets_allowed')
    if pets_allowed is not None:
        queryset = queryset.filter(pets_allowed=pets_allowed)
    
    # Status filter
    property_status = search_data.get('status')
    if property_status:
        queryset = queryset.filter(status=property_status)
    
    # Amenities filter
    amenities = search_data.get('amenities')
    if amenities:
        queryset = queryset.filter(amenities__id__in=amenities).distinct()
    
    # Order by creation date (newest first)
    queryset = queryset.order_by('-created_at')
    
    # Paginate results
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = PropertyListSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    serializer = PropertyListSerializer(queryset, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Get property statistics and analytics",
    responses={200: PropertyStatsSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def property_stats(request):
    """Get property statistics"""
    # Basic counts
    total_properties = Property.objects.count()
    available_properties = Property.objects.filter(status='available').count()
    rented_properties = Property.objects.filter(status='rented').count()
    
    # Views and favorites
    total_views = PropertyView.objects.count()
    total_favorites = PropertyFavorite.objects.count()
    
    # Average rent
    avg_rent = Property.objects.aggregate(avg_rent=Avg('rent_amount'))['avg_rent'] or 0
    
    # Properties by type
    properties_by_type = {}
    for prop_type in PropertyType.objects.annotate(count=Count('properties')):
        properties_by_type[prop_type.name] = prop_type.count
    
    # Properties by region
    properties_by_region = {}
    for region in Region.objects.annotate(count=Count('properties')):
        properties_by_region[region.name] = region.count
    
    stats_data = {
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'total_views': total_views,
        'total_favorites': total_favorites,
        'average_rent': avg_rent,
        'properties_by_type': properties_by_type,
        'properties_by_region': properties_by_region,
    }
    
    serializer = PropertyStatsSerializer(stats_data)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Get featured properties",
    responses={200: PropertyListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def featured_properties(request):
    """Get featured properties"""
    properties = Property.objects.filter(
        is_featured=True,
        status='available',
        is_active=True,
        is_approved=True
    ).select_related(
        'property_type', 'region', 'owner'
    ).prefetch_related('images', 'amenities').order_by('-created_at')[:10]
    
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    operation_description="Get recently added properties",
    responses={200: PropertyListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def recent_properties(request):
    """Get recently added properties"""
    properties = Property.objects.filter(
        is_active=True,
        is_approved=True
    ).select_related(
        'property_type', 'region', 'owner'
    ).prefetch_related('images', 'amenities').order_by('-created_at')[:10]
    
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def booking_details_api(request, booking_id):
    """Get booking details for modal display"""
    try:
        from .models import Booking
        
        booking = get_object_or_404(Booking, pk=booking_id)
        
        # Try to get payments, but handle the case where Payment model might not exist or have different structure
        payments = []
        try:
            from payments.models import Payment
            payments = Payment.objects.filter(booking=booking).order_by('-created_at')
        except:
            # If Payment model doesn't exist or has different structure, use empty list
            payments = []
        
        # Serialize booking data
        booking_data = {
            'id': booking.id,
            'booking_reference': booking.booking_reference,
            'booking_status': booking.booking_status,
            'booking_status_display': booking.get_booking_status_display(),
            'payment_status': booking.payment_status,
            'payment_status_display': booking.get_payment_status_display(),
            'check_in_date': booking.check_in_date.strftime('%B %d, %Y'),
            'check_out_date': booking.check_out_date.strftime('%B %d, %Y'),
            'number_of_guests': booking.number_of_guests,
            'total_amount': float(booking.total_amount),
            'base_rate': None,  # base_rate field doesn't exist in Booking model
            'notes': booking.special_requests,  # Use special_requests instead of notes
            'created_at': booking.created_at.strftime('%B %d, %Y %I:%M %p'),
            
            # Property details
            'property': {
                'title': booking.property_obj.title,
                'address': booking.property_obj.address,
                'property_type': booking.property_obj.property_type.name,
            },
            
            # Room details
            'room': {
                'room_number': booking.room_number,
                'room_type': booking.room_type,
            } if booking.room_number else None,
            
            # Customer details
            'customer': {
                'full_name': booking.customer.full_name,
                'email': booking.customer.email,
                'phone_number': booking.customer.phone,  # Use phone instead of phone_number
                'address': booking.customer.address,
                'date_of_birth': booking.customer.date_of_birth.strftime('%B %d, %Y') if booking.customer.date_of_birth else None,
            },
            
            # Payment history - handle different Payment model structures
            'payments': []
        }
        
        # Add payment history if payments exist and have the expected structure
        if payments:
            try:
                booking_data['payments'] = [
                    {
                        'id': payment.id,
                        'payment_date': payment.created_at.strftime('%B %d, %Y %I:%M %p'),
                        'amount': float(payment.amount),
                        'payment_method': getattr(payment, 'get_payment_method_display', lambda: 'Unknown')(),
                        'status': payment.status,
                        'status_display': getattr(payment, 'get_status_display', lambda: payment.status)(),
                        'reference_number': getattr(payment, 'reference_number', None) or getattr(payment, 'transaction_ref', None),
                    }
                    for payment in payments
                ]
            except Exception as e:
                # If there's an error processing payments, just use empty list
                booking_data['payments'] = []
        
        return Response(booking_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch booking details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def booking_status_update_api(request, booking_id):
    """Update booking status (confirm, check-in, check-out, cancel)"""
    try:
        import json
        from .models import Booking
        
        booking = get_object_or_404(Booking, pk=booking_id)
        data = json.loads(request.body)
        action = data.get('action')
        
        if not action:
            return JsonResponse({'error': 'Action is required'}, status=400)
        
        # Validate action based on current status
        valid_transitions = {
            'pending': ['confirm', 'cancel'],
            'confirmed': ['check_in', 'cancel'],
            'checked_in': ['check_out'],
            'checked_out': [],
            'cancelled': []
        }
        
        if action not in valid_transitions.get(booking.booking_status, []):
            return JsonResponse({
                'error': f'Cannot {action} booking with status {booking.booking_status}'
            }, status=400)
        
        # Update status based on action
        status_mapping = {
            'confirm': 'confirmed',
            'check_in': 'checked_in',
            'check_out': 'checked_out',
            'cancel': 'cancelled'
        }
        
        booking.booking_status = status_mapping[action]
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Booking {action}ed successfully',
            'new_status': booking.booking_status,
            'new_status_display': booking.get_booking_status_display()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to update booking status: {str(e)}'}, 
            status=500
        )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def booking_edit_api(request, booking_id):
    """Get booking data for editing or update booking"""
    try:
        from .models import Booking
        
        booking = get_object_or_404(Booking, pk=booking_id)
        
        if request.method == 'GET':
            # Return booking data for editing
            booking_data = {
                'id': booking.id,
                'booking_reference': booking.booking_reference,
                'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
                'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
                'number_of_guests': booking.number_of_guests,
                'room_number': booking.room_number,
                'room_type': booking.room_type,
                'total_amount': float(booking.total_amount),
                'base_rate': None,  # base_rate field doesn't exist in Booking model
                'special_requests': booking.special_requests,
                'notes': booking.special_requests,  # Use special_requests instead of notes
                
                # Customer data
                'customer': {
                    'first_name': booking.customer.first_name,
                    'last_name': booking.customer.last_name,
                    'email': booking.customer.email,
                    'phone': booking.customer.phone,
                    'address': booking.customer.address,
                },
                
                # Property data
                'property': {
                    'id': booking.property_obj.id,
                    'title': booking.property_obj.title,
                    'address': booking.property_obj.address,
                }
            }
            
            return Response(booking_data)
            
        elif request.method == 'POST':
            # Update booking
            data = request.data
            
            # Update booking fields
            booking.check_in_date = data.get('check_in_date', booking.check_in_date)
            booking.check_out_date = data.get('check_out_date', booking.check_out_date)
            booking.number_of_guests = data.get('number_of_guests', booking.number_of_guests)
            booking.room_number = data.get('room_number', booking.room_number)
            booking.room_type = data.get('room_type', booking.room_type)
            booking.total_amount = data.get('total_amount', booking.total_amount)
            booking.special_requests = data.get('special_requests', booking.special_requests)
            booking.notes = data.get('notes', booking.notes)
            
            # Update customer if provided
            if 'customer' in data:
                customer_data = data['customer']
                booking.customer.first_name = customer_data.get('first_name', booking.customer.first_name)
                booking.customer.last_name = customer_data.get('last_name', booking.customer.last_name)
                booking.customer.email = customer_data.get('email', booking.customer.email)
                booking.customer.phone = customer_data.get('phone', booking.customer.phone)
                booking.customer.address = customer_data.get('address', booking.customer.address)
                booking.customer.save()
            
            booking.save()
            
            return Response({
                'success': True,
                'message': 'Booking updated successfully',
                'booking_id': booking.id
            })
            
    except Exception as e:
        return Response(
            {'error': f'Failed to process booking edit: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_description="Check if user has already paid for visit access to a house property",
    operation_summary="Check Visit Payment Status",
    tags=['Property Visit'],
    responses={
        200: "Visit payment status retrieved",
        400: "Invalid property or not a house property"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def property_visit_status(request, property_id):
    """
    Check if user has already paid for visit access to a house property.
    
    GET /api/v1/properties/{property_id}/visit/status/
    """
    try:
        property_obj = get_object_or_404(Property, pk=property_id)
        
        # Only house properties support visit payments
        if property_obj.property_type.name.lower() != 'house':
            return Response(
                {'error': 'Visit payment is only available for house properties.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has already paid
        visit_payment = PropertyVisitPayment.objects.filter(
            property=property_obj,
            user=request.user,
            status='successful'
        ).first()
        
        has_paid = visit_payment is not None
        
        response_data = {
            'has_paid': has_paid,
            'visit_cost': float(property_obj.visit_cost) if property_obj.visit_cost else None,
            'property_id': property_obj.id,
            'property_title': property_obj.title
        }
        
        # If user has paid, include contact info
        if has_paid:
            owner = property_obj.owner
            owner_profile = getattr(owner, 'profile', None)
            
            response_data['owner_contact'] = {
                'phone': owner_profile.phone if owner_profile and owner_profile.phone else None,
                'email': owner.email,
                'name': owner.get_full_name() or owner.username
            }
            response_data['location'] = {
                'address': property_obj.address,
                'region': property_obj.region.name if property_obj.region else None,
                'district': property_obj.district.name if property_obj.district else None,
                'latitude': float(property_obj.latitude) if property_obj.latitude else None,
                'longitude': float(property_obj.longitude) if property_obj.longitude else None
            }
            response_data['paid_at'] = visit_payment.paid_at.isoformat() if visit_payment.paid_at else None
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to check visit status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Initiate visit payment for a house property. Creates payment record and returns payment link.",
    operation_summary="Initiate Visit Payment",
    tags=['Property Visit'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'payment_method': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Payment method (online, mobile_money, etc.)',
                default='online'
            )
        }
    ),
    responses={
        200: "Payment initiated successfully",
        400: "Invalid property, already paid, or visit cost not set",
        404: "Property not found"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_visit_initiate(request, property_id):
    """
    Initiate visit payment for a house property.
    Creates a payment record and initiates gateway payment.
    
    POST /api/v1/properties/{property_id}/visit/initiate/
    """
    try:
        property_obj = get_object_or_404(Property, pk=property_id)
        
        # Only house properties support visit payments
        if property_obj.property_type.name.lower() != 'house':
            return Response(
                {'error': 'Visit payment is only available for house properties.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if visit cost is set
        if not property_obj.visit_cost or property_obj.visit_cost <= 0:
            return Response(
                {'error': 'Visit cost is not set for this property.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has already paid
        existing_payment = PropertyVisitPayment.objects.filter(
            property=property_obj,
            user=request.user,
            status='successful'
        ).first()
        
        if existing_payment:
            return Response(
                {
                    'error': 'You have already paid for visit access to this property.',
                    'has_paid': True,
                    'payment_id': existing_payment.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create pending visit payment
        visit_payment, created = PropertyVisitPayment.objects.get_or_create(
            property=property_obj,
            user=request.user,
            defaults={
                'amount': property_obj.visit_cost,
                'status': 'pending'
            }
        )
        
        # Create unified Payment record
        from payments.models import Payment, PaymentProvider, PaymentTransaction
        from django.utils import timezone
        
        # Get or create payment provider (AZAM Pay)
        provider, _ = PaymentProvider.objects.get_or_create(
            name='AZAM Pay',
            defaults={'description': 'AZAM Pay Payment Gateway'}
        )
        
        # Create payment record
        payment = Payment.objects.create(
            tenant=request.user,
            provider=provider,
            amount=visit_payment.amount,
            payment_method='online',
            status='pending',
            notes=f'Visit payment for property: {property_obj.title}',
            recorded_by=request.user
        )
        
        # Link visit payment to unified payment
        visit_payment.payment = payment
        visit_payment.save()
        
        # Initiate gateway payment
        from payments.gateway_service import AZAMPayGateway
        
        callback_url = f"{request.build_absolute_uri('/')}api/v1/payments/webhook/azam-pay/"
        gateway_response = AZAMPayGateway.initiate_payment(payment, callback_url=callback_url)
        
        if gateway_response.get('success'):
            # Create payment transaction
            PaymentTransaction.objects.create(
                payment=payment,
                provider=provider,
                gateway_transaction_id=gateway_response.get('transaction_id'),
                azam_reference=gateway_response.get('reference'),
                status='initiated',
                request_payload={'property_id': property_id, 'visit_payment_id': visit_payment.id}
            )
            
            visit_payment.transaction_id = gateway_response.get('transaction_id')
            visit_payment.gateway_reference = gateway_response.get('reference')
            visit_payment.save()
            
            return Response({
                'success': True,
                'message': 'Payment initiated successfully',
                'payment_link': gateway_response.get('payment_link'),
                'transaction_id': gateway_response.get('transaction_id'),
                'reference': gateway_response.get('reference'),
                'visit_payment_id': visit_payment.id,
                'amount': float(visit_payment.amount)
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {
                    'error': gateway_response.get('error', 'Failed to initiate payment'),
                    'visit_payment_id': visit_payment.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Visit payment initiation error: {str(e)}")
        return Response(
            {'error': f'Failed to initiate visit payment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Verify visit payment and retrieve owner contact info and location after successful payment",
    operation_summary="Verify Visit Payment",
    tags=['Property Visit'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['transaction_id'],
        properties={
            'transaction_id': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='Payment gateway transaction ID'
            )
        }
    ),
    responses={
        200: "Payment verified and contact info returned",
        400: "Payment verification failed or already processed",
        404: "Visit payment not found"
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def property_visit_verify(request, property_id):
    """
    Verify visit payment and return owner contact info and location.
    
    POST /api/v1/properties/{property_id}/visit/verify/
    {
        "transaction_id": "txn_123456"
    }
    """
    try:
        property_obj = get_object_or_404(Property, pk=property_id)
        transaction_id = request.data.get('transaction_id')
        
        if not transaction_id:
            return Response(
                {'error': 'transaction_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get visit payment
        visit_payment = PropertyVisitPayment.objects.filter(
            property=property_obj,
            user=request.user,
            transaction_id=transaction_id
        ).first()
        
        if not visit_payment:
            return Response(
                {'error': 'Visit payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # If already successful, return contact info
        if visit_payment.status == 'successful':
            owner = property_obj.owner
            owner_profile = getattr(owner, 'profile', None)
            
            return Response({
                'success': True,
                'message': 'Payment already verified',
                'owner_contact': {
                    'phone': owner_profile.phone if owner_profile and owner_profile.phone else None,
                    'email': owner.email,
                    'name': owner.get_full_name() or owner.username
                },
                'location': {
                    'address': property_obj.address,
                    'region': property_obj.region.name if property_obj.region else None,
                    'district': property_obj.district.name if property_obj.district else None,
                    'latitude': float(property_obj.latitude) if property_obj.latitude else None,
                    'longitude': float(property_obj.longitude) if property_obj.longitude else None
                },
                'paid_at': visit_payment.paid_at.isoformat() if visit_payment.paid_at else None
            }, status=status.HTTP_200_OK)
        
        # Verify payment with gateway
        if visit_payment.payment:
            from payments.gateway_service import AZAMPayGateway
            
            verification_result = AZAMPayGateway.verify_payment(
                visit_payment.payment,
                transaction_id
            )
            
            if verification_result.get('success') and verification_result.get('verified'):
                # Update visit payment status
                from django.utils import timezone
                visit_payment.status = 'successful'
                visit_payment.paid_at = timezone.now()
                visit_payment.save()
                
                # Update unified payment
                if visit_payment.payment:
                    visit_payment.payment.status = 'successful'
                    visit_payment.payment.paid_date = timezone.now().date()
                    visit_payment.payment.save()
                
                # Get owner contact info
                owner = property_obj.owner
                owner_profile = getattr(owner, 'profile', None)
                
                return Response({
                    'success': True,
                    'message': 'Payment verified successfully',
                    'owner_contact': {
                        'phone': owner_profile.phone if owner_profile and owner_profile.phone else None,
                        'email': owner.email,
                        'name': owner.get_full_name() or owner.username
                    },
                    'location': {
                        'address': property_obj.address,
                        'region': property_obj.region.name if property_obj.region else None,
                        'district': property_obj.district.name if property_obj.district else None,
                        'latitude': float(property_obj.latitude) if property_obj.latitude else None,
                        'longitude': float(property_obj.longitude) if property_obj.longitude else None
                    },
                    'paid_at': visit_payment.paid_at.isoformat()
                }, status=status.HTTP_200_OK)
            else:
                visit_payment.status = 'failed'
                visit_payment.save()
                
                return Response(
                    {
                        'error': verification_result.get('error', 'Payment verification failed'),
                        'status': 'failed'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Payment record not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Visit payment verification error: {str(e)}")
        return Response(
            {'error': f'Failed to verify visit payment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )