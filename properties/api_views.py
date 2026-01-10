"""
Temporary shim API views for properties.

NOTE:
- The original `api_views.py` was accidentally overwritten earlier.
- To get the project running again, we provide minimal stub implementations
  for the endpoints referenced in `properties/api_urls.py`.
- Most endpoints return HTTP 501 (Not Implemented) so you can still start
  the server and use the parts of the system we recently worked on
  (booking, availability, AZAM Pay testing, etc.).
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import parsers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    PropertyType, Region, PropertyFavorite, Property, PropertyImage,
    District, Amenity
)
from .serializers import (
    PropertyTypeSerializer,
    RegionSerializer,
    PropertyFavoriteSerializer,
    PropertyCreateUpdateSerializer,
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyImageUploadSerializer,
    DistrictSerializer,
    AmenitySerializer
)


def _not_implemented_detail(name: str) -> Response:
    """Helper for consistent 501 responses."""
    return Response(
        {"detail": f"{name} is not implemented in this temporary shim."},
        status=status.HTTP_501_NOT_IMPLEMENTED,
    )


# ---------------------------------------------------------------------------
# Property CRUD stubs
# ---------------------------------------------------------------------------

class PropertyListCreateAPIView(APIView):
    """
    API endpoint to list and create properties.
    GET: List all properties (public)
    POST: Create a new property (requires authentication)
    """
    # Default permission - can be overridden per method
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Override to require authentication for POST"""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    @swagger_auto_schema(
        operation_description="Get a list of all properties. Public endpoint - no authentication required.",
        operation_summary="List Properties",
        tags=['Properties'],
        responses={
            200: PropertyListSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all properties"""
        properties = Property.objects.filter(
            is_active=True,
            is_approved=True
        ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities').order_by('-created_at')
        
        serializer = PropertyListSerializer(properties, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new property. Requires authentication. Property will be pending approval unless user is admin/staff.",
        operation_summary="Create Property",
        tags=['Properties'],
        request_body=PropertyCreateUpdateSerializer,
        responses={
            201: PropertyDetailSerializer,
            400: "Validation error",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        """Create a new property"""
        serializer = PropertyCreateUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            property_instance = serializer.save()
            response_serializer = PropertyDetailSerializer(property_instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyDetailAPIView(APIView):
    """
    API endpoint for property detail operations.
    GET: Get property details (public)
    PUT: Update entire property (requires authentication, must be owner or admin)
    PATCH: Partially update property (requires authentication, must be owner or admin)
    DELETE: Delete property (requires authentication, must be owner or admin)
    """
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Override to require authentication for write operations"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [AllowAny()]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific property by ID",
        operation_summary="Get Property Details",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: PropertyDetailSerializer,
            404: "Property not found"
        }
    )
    def get(self, request, pk, *args, **kwargs):
        """Get property details"""
        property_obj = get_object_or_404(Property, pk=pk)
        serializer = PropertyDetailSerializer(property_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update an entire property. User must own the property or be admin/staff.",
        operation_summary="Update Property",
        tags=['Properties'],
        request_body=PropertyCreateUpdateSerializer,
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: PropertyDetailSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Permission denied - you must own the property",
            404: "Property not found"
        },
        security=[{'Bearer': []}]
    )
    def put(self, request, pk, *args, **kwargs):
        """Update entire property"""
        property_obj = get_object_or_404(Property, pk=pk)
        
        # Check permissions
        if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to update this property."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PropertyCreateUpdateSerializer(property_obj, data=request.data, context={'request': request})
        if serializer.is_valid():
            updated_property = serializer.save()
            response_serializer = PropertyDetailSerializer(updated_property, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Partially update a property. User must own the property or be admin/staff.",
        operation_summary="Partially Update Property",
        tags=['Properties'],
        request_body=PropertyCreateUpdateSerializer,
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: PropertyDetailSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Permission denied - you must own the property",
            404: "Property not found"
        },
        security=[{'Bearer': []}]
    )
    def patch(self, request, pk, *args, **kwargs):
        """Partially update property"""
        property_obj = get_object_or_404(Property, pk=pk)
        
        # Check permissions
        if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to update this property."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PropertyCreateUpdateSerializer(property_obj, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            updated_property = serializer.save()
            response_serializer = PropertyDetailSerializer(updated_property, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a property. User must own the property or be admin/staff.",
        operation_summary="Delete Property",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Property deleted successfully",
            401: "Authentication required",
            403: "Permission denied - you must own the property",
            404: "Property not found"
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk, *args, **kwargs):
        """Delete property"""
        property_obj = get_object_or_404(Property, pk=pk)
        
        # Check permissions
        if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to delete this property."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        property_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyToggleStatusAPIView(APIView):
    """
    API endpoint to toggle property status (active/inactive).
    Requires authentication - user must own the property or be admin/staff.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Toggle property active status. User must own the property or be admin/staff.",
        operation_summary="Toggle Property Status",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Status toggled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Authentication required",
            403: "Permission denied - you must own the property",
            404: "Property not found"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, pk, *args, **kwargs):
        """Toggle property status"""
        property_obj = get_object_or_404(Property, pk=pk)
        
        # Check permissions
        if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to toggle this property's status."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        property_obj.is_active = not property_obj.is_active
        property_obj.save()
        
        return Response({
            'id': property_obj.id,
            'is_active': property_obj.is_active,
            'message': f"Property status set to {'active' if property_obj.is_active else 'inactive'}"
        }, status=status.HTTP_200_OK)


class PropertyDeleteAPIView(APIView):
    """
    API endpoint to delete a property.
    Requires authentication - user must own the property or be admin/staff.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a property. User must own the property or be admin/staff.",
        operation_summary="Delete Property",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Property deleted successfully",
            401: "Authentication required",
            403: "Permission denied - you must own the property",
            404: "Property not found"
        },
        security=[{'Bearer': []}]
    )
    def delete(self, request, pk, *args, **kwargs):
        """Delete property"""
        property_obj = get_object_or_404(Property, pk=pk)
        
        # Check permissions
        if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to delete this property."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        property_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyPropertiesAPIView(APIView):
    """
    API endpoint to get properties owned by the current authenticated user.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all properties owned by the current authenticated user",
        operation_summary="Get My Properties",
        tags=['Properties'],
        responses={
            200: PropertyListSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        """Get current user's properties"""
        properties = Property.objects.filter(owner=request.user).select_related(
            'property_type', 'region', 'owner'
        ).prefetch_related('images', 'amenities').order_by('-created_at')
        
        serializer = PropertyListSerializer(properties, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Property metadata stubs
# ---------------------------------------------------------------------------

class PropertyTypeListAPIView(APIView):
    """
    API endpoint to list all property types.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all property types (apartment, house, studio, etc.)",
        operation_summary="List Property Types",
        tags=['Properties'],
        responses={
            200: PropertyTypeSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all property types"""
        property_types = PropertyType.objects.all().order_by('name')
        serializer = PropertyTypeSerializer(property_types, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyTypeDetailAPIView(APIView):
    """
    API endpoint to get property type details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific property type by ID",
        operation_summary="Get Property Type Details",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Property Type ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: PropertyTypeSerializer,
            404: "Property type not found"
        }
    )
    def get(self, request, pk, *args, **kwargs):
        """Get property type details"""
        property_type = get_object_or_404(PropertyType, pk=pk)
        serializer = PropertyTypeSerializer(property_type, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegionListAPIView(APIView):
    """
    API endpoint to list all regions.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all regions/locations where properties are available",
        operation_summary="List Regions",
        tags=['Properties'],
        responses={
            200: RegionSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all regions"""
        regions = Region.objects.all().order_by('name')
        serializer = RegionSerializer(regions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegionDetailAPIView(APIView):
    """
    API endpoint to get region details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific region by ID",
        operation_summary="Get Region Details",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Region ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: RegionSerializer,
            404: "Region not found"
        }
    )
    def get(self, request, pk, *args, **kwargs):
        """Get region details"""
        region = get_object_or_404(Region, pk=pk)
        serializer = RegionSerializer(region, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictListAPIView(APIView):
    """
    API endpoint to list all districts.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all districts within regions",
        operation_summary="List Districts",
        tags=['Properties'],
        responses={
            200: DistrictSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all districts"""
        districts = District.objects.all().select_related('region').order_by('name')
        serializer = DistrictSerializer(districts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictDetailAPIView(APIView):
    """
    API endpoint to get district details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific district by ID",
        operation_summary="Get District Details",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="District ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: DistrictSerializer,
            404: "District not found"
        }
    )
    def get(self, request, pk, *args, **kwargs):
        """Get district details"""
        district = get_object_or_404(District, pk=pk)
        serializer = DistrictSerializer(district, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AmenityListAPIView(APIView):
    """
    API endpoint to list all amenities.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get a list of all property amenities (e.g., WiFi, Parking, Pool, etc.)",
        operation_summary="List Amenities",
        tags=['Properties'],
        responses={
            200: AmenitySerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all amenities"""
        amenities = Amenity.objects.all().order_by('name')
        serializer = AmenitySerializer(amenities, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AmenityDetailAPIView(APIView):
    """
    API endpoint to get amenity details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get detailed information about a specific amenity by ID",
        operation_summary="Get Amenity Details",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Amenity ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: AmenitySerializer,
            404: "Amenity not found"
        }
    )
    def get(self, request, pk, *args, **kwargs):
        """Get amenity details"""
        amenity = get_object_or_404(Amenity, pk=pk)
        serializer = AmenitySerializer(amenity, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyImageUploadAPIView(APIView):
    """
    API endpoint to upload property images.
    Requires authentication - user must own the property.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @swagger_auto_schema(
        operation_description="Upload an image for a property. User must own the property.",
        operation_summary="Upload Property Image",
        tags=['Properties'],
        request_body=PropertyImageUploadSerializer,
        responses={
            201: PropertyImageUploadSerializer,
            400: "Validation error",
            401: "Authentication required",
            403: "Permission denied - you must own the property"
        },
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        """Upload a property image"""
        serializer = PropertyImageUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Check if user owns the property
            property_obj = serializer.validated_data['property']
            if property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
                return Response(
                    {"detail": "You can only upload images for your own properties."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check image limit (max 10 images per property)
            if property_obj.images.count() >= 10:
                return Response(
                    {"detail": "Maximum of 10 images allowed per property."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If this is set as primary, unset all other primary images
            if serializer.validated_data.get('is_primary', False):
                PropertyImage.objects.filter(property=property_obj).update(is_primary=False)
            
            image_instance = serializer.save()
            response_serializer = PropertyImageUploadSerializer(image_instance, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoritePropertiesAPIView(APIView):
    """
    API endpoint to get user's favorite properties.
    Requires authentication - returns favorites for the current user.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a list of properties favorited by the current authenticated user",
        operation_summary="Get Favorite Properties",
        tags=['Properties'],
        responses={
            200: PropertyFavoriteSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        """Get current user's favorite properties"""
        favorites = PropertyFavorite.objects.filter(user=request.user).select_related('property').order_by('-created_at')
        serializer = PropertyFavoriteSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    operation_description="Add or remove a property from user's favorites. If property is already favorited, it will be removed. If not favorited, it will be added.",
    operation_summary="Toggle Property Favorite",
    tags=['Properties'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['property_id'],
        properties={
            'property_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the property to favorite/unfavorite'
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Favorite status toggled successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_favorited': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the property is now favorited'),
                    'favorites_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of users who favorited this property'),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: "Invalid property ID",
        401: "Authentication required",
        404: "Property not found"
    },
    security=[{'Bearer': []}],
    methods=['post']
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    """Toggle favorite status for a property"""
    property_id = request.data.get('property_id')
    
    if not property_id:
        return Response(
            {"detail": "property_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        property_obj = Property.objects.get(pk=property_id)
    except Property.DoesNotExist:
        return Response(
            {"detail": "Property not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already favorited
    favorite, created = PropertyFavorite.objects.get_or_create(
        user=request.user,
        property=property_obj
    )
    
    if not created:
        # Already favorited, remove it
        favorite.delete()
        is_favorited = False
        message = "Property removed from favorites"
    else:
        # Added to favorites
        is_favorited = True
        message = "Property added to favorites"
    
    return Response({
        'is_favorited': is_favorited,
        'favorites_count': property_obj.favorited_by.count(),
        'message': message
    }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Search and special endpoints
# ---------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    operation_description="Search properties with filters. Supports search by title, description, address, property type, region, bedrooms, rent range, etc.",
    operation_summary="Search Properties",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search query (title, description, address)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('district', openapi.IN_QUERY, description="Filter by district ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('min_bedrooms', openapi.IN_QUERY, description="Minimum bedrooms", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('max_bedrooms', openapi.IN_QUERY, description="Maximum bedrooms", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('min_rent', openapi.IN_QUERY, description="Minimum rent amount", type=openapi.TYPE_NUMBER, required=False),
        openapi.Parameter('max_rent', openapi.IN_QUERY, description="Maximum rent amount", type=openapi.TYPE_NUMBER, required=False),
        openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", type=openapi.TYPE_STRING, required=False),
    ],
    responses={
        200: PropertyListSerializer(many=True)
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def property_search(request):
    """Search properties with filters"""
    from django.db.models import Q
    
    properties = Property.objects.filter(
        is_active=True,
        is_approved=True
    ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities')
    
    # Search query
    search_query = request.GET.get('search', '').strip()
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Filters
    property_type_id = request.GET.get('property_type')
    if property_type_id:
        properties = properties.filter(property_type_id=property_type_id)
    
    region_id = request.GET.get('region')
    if region_id:
        properties = properties.filter(region_id=region_id)
    
    district_id = request.GET.get('district')
    if district_id:
        properties = properties.filter(district_id=district_id)
    
    min_bedrooms = request.GET.get('min_bedrooms')
    if min_bedrooms:
        try:
            properties = properties.filter(bedrooms__gte=int(min_bedrooms))
        except (ValueError, TypeError):
            pass
    
    max_bedrooms = request.GET.get('max_bedrooms')
    if max_bedrooms:
        try:
            properties = properties.filter(bedrooms__lte=int(max_bedrooms))
        except (ValueError, TypeError):
            pass
    
    min_rent = request.GET.get('min_rent')
    if min_rent:
        try:
            properties = properties.filter(rent_amount__gte=float(min_rent))
        except (ValueError, TypeError):
            pass
    
    max_rent = request.GET.get('max_rent')
    if max_rent:
        try:
            properties = properties.filter(rent_amount__lte=float(max_rent))
        except (ValueError, TypeError):
            pass
    
    status_filter = request.GET.get('status')
    if status_filter:
        properties = properties.filter(status=status_filter)
    
    properties = properties.order_by('-created_at')
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get featured properties (properties marked as featured)",
    operation_summary="Get Featured Properties",
    tags=['Properties'],
    responses={
        200: PropertyListSerializer(many=True)
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def featured_properties(request):
    """Get featured properties"""
    properties = Property.objects.filter(
        is_active=True,
        is_approved=True,
        is_featured=True
    ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities').order_by('-created_at')
    
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get recently added properties (most recent first)",
    operation_summary="Get Recent Properties",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter('limit', openapi.IN_QUERY, description="Number of properties to return (default: 10)", type=openapi.TYPE_INTEGER, required=False),
    ],
    responses={
        200: PropertyListSerializer(many=True)
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def recent_properties(request):
    """Get recent properties"""
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
        if limit > 100:
            limit = 100
    except (ValueError, TypeError):
        limit = 10
    
    properties = Property.objects.filter(
        is_active=True,
        is_approved=True
    ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities').order_by('-created_at')[:limit]
    
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    operation_description="Get property statistics including total properties, available properties, rented properties, average rent, and breakdowns by type and region",
    operation_summary="Get Property Statistics",
    tags=['Properties'],
    responses={
        200: openapi.Response(
            description="Property statistics",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_properties': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'available_properties': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'rented_properties': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'under_maintenance': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'average_rent': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'properties_by_type': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'properties_by_region': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            )
        )
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def property_stats(request):
    """Get property statistics"""
    from django.db.models import Count, Avg
    
    total_properties = Property.objects.filter(is_approved=True).count()
    available_properties = Property.objects.filter(status='available', is_active=True, is_approved=True).count()
    rented_properties = Property.objects.filter(status='rented', is_approved=True).count()
    under_maintenance = Property.objects.filter(status='under_maintenance', is_approved=True).count()
    
    average_rent = Property.objects.filter(
        is_approved=True,
        rent_amount__isnull=False
    ).aggregate(avg_rent=Avg('rent_amount'))['avg_rent'] or 0
    
    # Properties by type
    properties_by_type = PropertyType.objects.annotate(
        count=Count('properties', filter=Q(properties__is_approved=True))
    ).values('id', 'name', 'count')
    
    # Properties by region
    properties_by_region = Region.objects.annotate(
        count=Count('properties', filter=Q(properties__is_approved=True))
    ).values('id', 'name', 'count')
    
    return Response({
        'total_properties': total_properties,
        'available_properties': available_properties,
        'rented_properties': rented_properties,
        'under_maintenance': under_maintenance,
        'average_rent': float(average_rent) if average_rent else 0,
        'properties_by_type': {pt['name']: pt['count'] for pt in properties_by_type},
        'properties_by_region': {r['name']: r['count'] for r in properties_by_region},
    }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Booking API endpoints
# ---------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    operation_description="Get detailed information about a specific booking by ID. User must be the booking tenant or property owner.",
    operation_summary="Get Booking Details",
    tags=['Bookings'],
    manual_parameters=[
        openapi.Parameter(
            'booking_id',
            openapi.IN_PATH,
            description="Booking ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Booking details",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        401: "Authentication required",
        403: "Permission denied",
        404: "Booking not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def booking_details_api(request, booking_id):
    """Get booking details"""
    try:
        from documents.models import Booking
        booking = get_object_or_404(Booking, pk=booking_id)
        
        # Check permissions - tenant or property owner
        if booking.tenant != request.user and booking.property_ref.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to view this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return Response({
            'id': booking.id,
            'property': booking.property_ref.id,
            'property_title': booking.property_ref.title,
            'tenant': booking.tenant.username,
            'check_in': booking.check_in,
            'check_out': booking.check_out,
            'total_amount': str(booking.total_amount),
            'status': booking.status,
            'created_at': booking.created_at,
            'nights': booking.nights,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"Error retrieving booking: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Update booking status. User must be property owner or admin.",
    operation_summary="Update Booking Status",
    tags=['Bookings'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['status'],
        properties={
            'status': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['pending', 'confirmed', 'cancelled', 'completed'],
                description='New booking status'
            )
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            'booking_id',
            openapi.IN_PATH,
            description="Booking ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Status updated successfully",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        400: "Invalid status",
        401: "Authentication required",
        403: "Permission denied",
        404: "Booking not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def booking_status_update_api(request, booking_id):
    """Update booking status"""
    try:
        from documents.models import Booking
        booking = get_object_or_404(Booking, pk=booking_id)
        
        # Check permissions - property owner or admin
        if booking.property_ref.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to update this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
            return Response(
                {"detail": "Invalid status. Must be one of: pending, confirmed, cancelled, completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = new_status
        booking.save()
        
        return Response({
            'id': booking.id,
            'status': booking.status,
            'message': f'Booking status updated to {new_status}'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"Error updating booking: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_description="Edit booking details. User must be property owner or admin.",
    operation_summary="Edit Booking",
    tags=['Bookings'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'check_in': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Check-in date (YYYY-MM-DD)'),
            'check_out': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Check-out date (YYYY-MM-DD)'),
            'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Total booking amount'),
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            'booking_id',
            openapi.IN_PATH,
            description="Booking ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Booking updated successfully",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        400: "Validation error",
        401: "Authentication required",
        403: "Permission denied",
        404: "Booking not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def booking_edit_api(request, booking_id):
    """Edit booking"""
    try:
        from documents.models import Booking
        from django.utils.dateparse import parse_date
        booking = get_object_or_404(Booking, pk=booking_id)
        
        # Check permissions - property owner or admin
        if booking.property_ref.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to edit this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update fields if provided
        if 'check_in' in request.data:
            check_in = parse_date(request.data['check_in'])
            if check_in:
                booking.check_in = check_in
        
        if 'check_out' in request.data:
            check_out = parse_date(request.data['check_out'])
            if check_out:
                booking.check_out = check_out
        
        if 'total_amount' in request.data:
            try:
                booking.total_amount = float(request.data['total_amount'])
            except (ValueError, TypeError):
                return Response(
                    {"detail": "Invalid total_amount"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        booking.save()
        
        return Response({
            'id': booking.id,
            'check_in': booking.check_in,
            'check_out': booking.check_out,
            'total_amount': str(booking.total_amount),
            'message': 'Booking updated successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"Error editing booking: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ---------------------------------------------------------------------------
# Visit payment / property visit endpoints
# ---------------------------------------------------------------------------

@swagger_auto_schema(
    method='get',
    operation_description="Get property visit payment status. Check if visit payment has been made for a property.",
    operation_summary="Get Property Visit Status",
    tags=['Property Visits'],
    manual_parameters=[
        openapi.Parameter(
            'property_id',
            openapi.IN_PATH,
            description="Property ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Visit status",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'has_paid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'visit_cost': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        401: "Authentication required",
        404: "Property not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def property_visit_status(request, property_id):
    """Get property visit payment status"""
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if user has paid for visit
    from .models import PropertyVisitPayment
    visit_payment = PropertyVisitPayment.objects.filter(
        property=property_obj,
        user=request.user,
        status='completed'
    ).first()
    
    has_paid = visit_payment is not None
    visit_cost = property_obj.visit_cost or 0
    
    return Response({
        'has_paid': has_paid,
        'visit_cost': float(visit_cost) if visit_cost else 0,
        'message': 'Visit payment completed' if has_paid else 'Visit payment pending'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Initiate a property visit payment. Creates a payment request for visiting the property.",
    operation_summary="Initiate Property Visit Payment",
    tags=['Property Visits'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'payment_method': openapi.Schema(type=openapi.TYPE_STRING, description='Payment method (e.g., mobile_money, card)'),
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            'property_id',
            openapi.IN_PATH,
            description="Property ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Visit payment initiated",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        400: "Invalid request",
        401: "Authentication required",
        404: "Property not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def property_visit_initiate(request, property_id):
    """Initiate property visit payment"""
    property_obj = get_object_or_404(Property, pk=property_id)
    
    if not property_obj.visit_cost or property_obj.visit_cost <= 0:
        return Response(
            {"detail": "This property does not require a visit payment."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already paid
    from .models import PropertyVisitPayment
    existing_payment = PropertyVisitPayment.objects.filter(
        property=property_obj,
        user=request.user,
        status='completed'
    ).first()
    
    if existing_payment:
        return Response({
            'message': 'Visit payment already completed',
            'payment_id': existing_payment.id,
            'status': 'completed'
        }, status=status.HTTP_200_OK)
    
    # Create payment record (stub - actual payment processing would go here)
    return Response({
        'message': 'Visit payment initiated',
        'property_id': property_obj.id,
        'visit_cost': float(property_obj.visit_cost),
        'status': 'pending'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Verify property visit payment. Confirms that payment has been completed.",
    operation_summary="Verify Property Visit Payment",
    tags=['Property Visits'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['payment_reference'],
        properties={
            'payment_reference': openapi.Schema(type=openapi.TYPE_STRING, description='Payment reference/transaction ID'),
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            'property_id',
            openapi.IN_PATH,
            description="Property ID",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Payment verified",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        400: "Invalid payment reference",
        401: "Authentication required",
        404: "Property not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def property_visit_verify(request, property_id):
    """Verify property visit payment"""
    property_obj = get_object_or_404(Property, pk=property_id)
    
    payment_reference = request.data.get('payment_reference')
    if not payment_reference:
        return Response(
            {"detail": "payment_reference is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify payment (stub - actual verification would go here)
    return Response({
        'message': 'Visit payment verified',
        'property_id': property_obj.id,
        'payment_reference': payment_reference,
        'status': 'completed'
    }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# New: property availability API (used by booking forms / tests)
# ---------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def property_availability_api(request, property_id):
    """
    Get property availability information including booked dates and next available date.
    This mirrors the logic used by the booking forms to show availability.
    """
    try:
        from .models import Property, Booking
        from documents.models import Lease
        from django.utils import timezone
        from datetime import datetime, timedelta

        property_obj = get_object_or_404(Property, pk=property_id)

        # Get all active bookings (confirmed, checked_in, pending)
        active_bookings = property_obj.property_bookings.filter(
            booking_status__in=["confirmed", "checked_in", "pending"]
        ).order_by("check_in_date")

        # Get active leases
        active_leases = Lease.objects.filter(
            property_ref=property_obj, status="active"
        ).order_by("start_date")

        # Prepare booked dates from bookings
        booked_dates = []
        current_bookings = []

        for booking in active_bookings:
            booked_dates.append(
                {
                    "check_in": booking.check_in_date.strftime("%Y-%m-%d"),
                    "check_out": booking.check_out_date.strftime("%Y-%m-%d"),
                    "status": booking.booking_status,
                    "booking_reference": booking.booking_reference,
                }
            )
            current_bookings.append(
                {
                    "id": booking.id,
                    "check_in": booking.check_in_date.strftime("%Y-%m-%d"),
                    "check_out": booking.check_out_date.strftime("%Y-%m-%d"),
                    "status": booking.booking_status,
                    "booking_reference": booking.booking_reference,
                    "customer": booking.customer.full_name
                    if booking.customer
                    else "N/A",
                }
            )

        # Add lease dates
        for lease in active_leases:
            booked_dates.append(
                {
                    "check_in": lease.start_date.strftime("%Y-%m-%d"),
                    "check_out": lease.end_date.strftime("%Y-%m-%d"),
                    "status": "lease",
                    "booking_reference": f"Lease-{lease.id}",
                }
            )

        # Calculate next available date
        today = timezone.now().date()
        next_available_date = None

        # Sort booked dates by check_in
        sorted_bookings = sorted(booked_dates, key=lambda x: x["check_in"])

        # Find first gap or date after last booking
        if sorted_bookings:
            last_checkout = max(
                datetime.strptime(b["check_out"], "%Y-%m-%d").date()
                for b in sorted_bookings
            )
            # Next available is day after last checkout
            if last_checkout >= today:
                next_available_date = (last_checkout + timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                )
            else:
                next_available_date = today.strftime("%Y-%m-%d")
        else:
            # No bookings, available from today
            next_available_date = today.strftime("%Y-%m-%d")

        # Check if property is currently available
        is_available = property_obj.is_available_for_booking()

        return Response(
            {
                "property_id": property_obj.id,
                "property_title": property_obj.title,
                "is_available": is_available,
                "property_status": property_obj.status,
                "booked_dates": booked_dates,
                "current_bookings": current_bookings,
                "next_available_date": next_available_date,
                "has_active_bookings": len(current_bookings) > 0,
                "has_active_leases": len(active_leases) > 0,
            }
        )

    except Exception as e:
        return Response(
            {"error": f"Failed to fetch availability: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
