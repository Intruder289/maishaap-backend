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
# Swagger documentation - using drf-spectacular
# Always import extend_schema from drf-spectacular as it's used throughout the file
try:
    from drf_spectacular.utils import extend_schema, OpenApiParameter
    from drf_spectacular.types import OpenApiTypes
except ImportError:
    # Fallback if drf-spectacular is not available
    extend_schema = lambda *args, **kwargs: lambda func: func  # No-op decorator
    OpenApiParameter = None
    OpenApiTypes = None

# Also try to import drf-yasg for backward compatibility (if available)
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
except ImportError:
    # drf-yasg not installed, create fallback openapi class first
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
    
    # Create a wrapper to convert swagger_auto_schema to extend_schema for drf-spectacular
    def swagger_auto_schema(*args, **kwargs):
        # Handle method parameter - drf-spectacular doesn't need it
        # but we should still process the decorator
        method = kwargs.pop('method', None)
        
        # Extract parameters from manual_parameters if present
        manual_params = kwargs.get('manual_parameters', [])
        spectacular_params = []
        
        if manual_params:
            # Convert drf-yasg parameters to drf-spectacular parameters
            for param in manual_params:
                # Skip None values
                if param is None:
                    continue
                
                # Skip lambda functions (old fallback)
                if callable(param) and not hasattr(param, 'name'):
                    continue
                
                # Try to extract parameter info
                param_name = None
                param_type = OpenApiTypes.STR
                param_location = OpenApiParameter.QUERY
                param_description = ''
                param_required = False
                
                # Check if it's a Parameter-like object (has 'name' attribute)
                if hasattr(param, 'name') and param.name:
                    param_name = param.name
                    param_description = getattr(param, 'description', '') or ''
                    param_required = getattr(param, 'required', False)
                    
                    # Determine type - check both string constants and actual values
                    param_type_attr = getattr(param, 'type', None)
                    type_str = str(param_type_attr).lower() if param_type_attr else ''
                    
                    if (param_type_attr == openapi.TYPE_INTEGER or 
                        type_str == 'integer' or 
                        'integer' in type_str):
                        param_type = OpenApiTypes.INT
                    elif (param_type_attr == openapi.TYPE_NUMBER or 
                          type_str == 'number' or 
                          'number' in type_str):
                        param_type = OpenApiTypes.NUMBER
                    elif (param_type_attr == openapi.TYPE_BOOLEAN or 
                          type_str == 'boolean' or 
                          'boolean' in type_str):
                        param_type = OpenApiTypes.BOOL
                    else:
                        param_type = OpenApiTypes.STR
                    
                    # Determine location
                    param_in = getattr(param, 'in_', None)
                    in_str = str(param_in).lower() if param_in else ''
                    
                    if (param_in == openapi.IN_QUERY or 
                        in_str == 'query' or 
                        'query' in in_str):
                        param_location = OpenApiParameter.QUERY
                    elif (param_in == openapi.IN_PATH or 
                          in_str == 'path' or 
                          'path' in in_str):
                        param_location = OpenApiParameter.PATH
                    else:
                        param_location = OpenApiParameter.QUERY
                    
                    # Create the parameter
                    spectacular_params.append(
                        OpenApiParameter(
                            name=param_name,
                            type=param_type,
                            location=param_location,
                            description=param_description,
                            required=param_required
                        )
                    )
                # Handle tuple/list format: (name, location, description, type, required)
                elif isinstance(param, (tuple, list)) and len(param) >= 2:
                    param_name = param[0]
                    param_location_str = param[1] if len(param) > 1 else 'query'
                    param_description = param[2] if len(param) > 2 else ''
                    param_type_str = param[3] if len(param) > 3 else 'string'
                    param_required = param[4] if len(param) > 4 else False
                    
                    # Convert location
                    if param_location_str == 'query' or param_location_str == openapi.IN_QUERY:
                        param_location = OpenApiParameter.QUERY
                    elif param_location_str == 'path' or param_location_str == openapi.IN_PATH:
                        param_location = OpenApiParameter.PATH
                    else:
                        param_location = OpenApiParameter.QUERY
                    
                    # Convert type
                    if 'int' in str(param_type_str).lower():
                        param_type = OpenApiTypes.INT
                    elif 'number' in str(param_type_str).lower():
                        param_type = OpenApiTypes.NUMBER
                    else:
                        param_type = OpenApiTypes.STR
                    
                    spectacular_params.append(
                        OpenApiParameter(
                            name=param_name,
                            type=param_type,
                            location=param_location,
                            description=param_description,
                            required=param_required
                        )
                    )
        
        # Use extend_schema with parameters
        # extend_schema already returns a decorator, so we can return it directly
        # Build extend_schema kwargs
        schema_kwargs = {
            'summary': kwargs.get('operation_summary', ''),
            'description': kwargs.get('operation_description', ''),
            'tags': kwargs.get('tags', []),
        }
        
        # Only add parameters if we have any (don't pass empty list or None)
        if spectacular_params:
            schema_kwargs['parameters'] = spectacular_params
        
        # Add responses if provided
        if kwargs.get('responses'):
            schema_kwargs['responses'] = kwargs.get('responses')
        
        # Add request/request_body if provided (for POST/PUT/PATCH)
        if kwargs.get('request_body'):
            schema_kwargs['request'] = kwargs.get('request_body')
        elif kwargs.get('request'):
            schema_kwargs['request'] = kwargs.get('request')
        
        return extend_schema(**schema_kwargs)

from .models import (
    PropertyType, Region, PropertyFavorite, Property, PropertyImage,
    District, Amenity, Room, Booking, Customer
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
    AmenitySerializer,
    RoomSerializer
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

    # Use drf-spectacular directly to ensure parameters are properly documented
    @extend_schema(
        summary="List Properties",
        description="Get a list of all properties. Public endpoint - no authentication required. Supports filtering and pagination.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('property_type', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by property type ID", required=False),
            OpenApiParameter('category', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", required=False),
            OpenApiParameter('region', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by region ID", required=False),
            OpenApiParameter('district', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by district ID", required=False),
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", required=False),
            OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Page number for pagination (default: 1)", required=False),
            OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Number of items per page (default: 20, max: 100)", required=False),
        ],
        responses={200: PropertyListSerializer(many=True)}
    )
    @swagger_auto_schema(
        operation_description="Get a list of all properties. Public endpoint - no authentication required. Supports filtering and pagination.",
        operation_summary="List Properties",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('district', openapi.IN_QUERY, description="Filter by district ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination (default: 1)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page (default: 20, max: 100)", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: PropertyListSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all properties with optional filtering"""
        properties = Property.objects.filter(
            is_active=True,
            is_approved=True
        ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities')
        
        # Filter by property_type ID (if provided)
        property_type_id = request.GET.get('property_type')
        if property_type_id:
            try:
                properties = properties.filter(property_type_id=int(property_type_id))
            except (ValueError, TypeError):
                pass
        
        # Filter by category name (for mobile app compatibility)
        # This allows filtering by category name like 'house', 'hotel', 'lodge', 'venue'
        category_name = request.GET.get('category')
        if category_name:
            # Normalize category name to lowercase for matching
            category_name = category_name.lower().strip()
            properties = properties.filter(property_type__name__iexact=category_name)
        
        # Filter by region (if provided)
        region_id = request.GET.get('region')
        if region_id:
            try:
                properties = properties.filter(region_id=int(region_id))
            except (ValueError, TypeError):
                pass
        
        # Filter by district (if provided)
        district_id = request.GET.get('district')
        if district_id:
            try:
                properties = properties.filter(district_id=int(district_id))
            except (ValueError, TypeError):
                pass
        
        # Filter by status (if provided)
        status_filter = request.GET.get('status')
        if status_filter:
            properties = properties.filter(status=status_filter)
        
        properties = properties.order_by('-created_at')
        
        # Pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        
        try:
            page = int(page)
            page_size = int(page_size)
            if page_size > 100:
                page_size = 100
            if page_size < 1:
                page_size = 20
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        # Calculate pagination
        total = properties.count()
        start = (page - 1) * page_size
        end = start + page_size
        properties_page = properties[start:end]
        
        serializer = PropertyListSerializer(properties_page, many=True, context={'request': request})
        
        # Return paginated response
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if total > 0 else 0,
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Create Property",
        description="Create a new property. Requires authentication. Property will be pending approval unless user is admin/staff.",
        tags=['Properties'],
        request=PropertyCreateUpdateSerializer,
        responses={
            201: PropertyDetailSerializer,
            400: {'description': 'Validation error'},
            401: {'description': 'Authentication required'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get Property Details",
        description="Get detailed information about a specific property by ID",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
        ],
        responses={
            200: PropertyDetailSerializer,
            404: {'description': 'Property not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Update Property",
        description="Update an entire property. User must own the property or be admin/staff.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
        ],
        request=PropertyCreateUpdateSerializer,
        responses={
            200: PropertyDetailSerializer,
            400: {'description': 'Validation error'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied - you must own the property'},
            404: {'description': 'Property not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Partially Update Property",
        description="Partially update a property. User must own the property or be admin/staff.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
        ],
        request=PropertyCreateUpdateSerializer,
        responses={
            200: PropertyDetailSerializer,
            400: {'description': 'Validation error'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied - you must own the property'},
            404: {'description': 'Property not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Toggle Property Status",
        description="Toggle property active status. User must own the property or be admin/staff.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
        ],
        responses={
            200: {
                'description': 'Status toggled successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'is_active': {'type': 'boolean'},
                                'message': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied - you must own the property'},
            404: {'description': 'Property not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Delete Property",
        description="Delete a property. User must own the property or be admin/staff.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
        ],
        responses={
            204: {'description': 'Property deleted successfully'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied - you must own the property'},
            404: {'description': 'Property not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get My Properties",
        description="Get all properties owned by the current authenticated user. Supports pagination and optional filtering.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Page number for pagination (default: 1)", required=False),
            OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Number of items per page (default: 20, max: 100)", required=False),
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", required=False),
            OpenApiParameter('property_type', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by property type ID", required=False),
        ],
        responses={
            200: PropertyListSerializer(many=True),
            401: {'description': 'Authentication required'}
        }
    )
    @swagger_auto_schema(
        operation_description="Get all properties owned by the current authenticated user. Supports pagination and optional filtering.",
        operation_summary="Get My Properties",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination (default: 1)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page (default: 20, max: 100)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: PropertyListSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        """Get current user's properties with optional pagination and filtering"""
        properties = Property.objects.filter(owner=request.user).select_related(
            'property_type', 'region', 'owner'
        ).prefetch_related('images', 'amenities')
        
        # Filter by status (if provided)
        status_filter = request.GET.get('status')
        if status_filter:
            properties = properties.filter(status=status_filter)
        
        # Filter by property_type ID (if provided)
        property_type_id = request.GET.get('property_type')
        if property_type_id:
            try:
                properties = properties.filter(property_type_id=int(property_type_id))
            except (ValueError, TypeError):
                pass
        
        properties = properties.order_by('-created_at')
        
        # Pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        
        try:
            page = int(page)
            page_size = int(page_size)
            if page_size > 100:
                page_size = 100
            if page_size < 1:
                page_size = 20
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        # Calculate pagination
        total = properties.count()
        start = (page - 1) * page_size
        end = start + page_size
        properties_page = properties[start:end]
        
        serializer = PropertyListSerializer(properties_page, many=True, context={'request': request})
        
        # Return paginated response
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if total > 0 else 0,
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Property metadata stubs
# ---------------------------------------------------------------------------

class PropertyTypeListAPIView(APIView):
    """
    API endpoint to list all property types.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="List Property Types",
        description="Get a list of all property types (apartment, house, studio, etc.). Supports optional search.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Search property types by name", required=False),
        ],
        responses={200: PropertyTypeSerializer(many=True)}
    )
    @swagger_auto_schema(
        operation_description="Get a list of all property types (apartment, house, studio, etc.). Supports optional search.",
        operation_summary="List Property Types",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search property types by name", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: PropertyTypeSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all property types with optional search"""
        property_types = PropertyType.objects.all()
        
        # Optional search filter
        search_query = request.GET.get('search', '').strip()
        if search_query:
            property_types = property_types.filter(name__icontains=search_query)
        
        property_types = property_types.order_by('name')
        serializer = PropertyTypeSerializer(property_types, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyTypeDetailAPIView(APIView):
    """
    API endpoint to get property type details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get Property Type Details",
        description="Get detailed information about a specific property type by ID",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property Type ID", required=True),
        ],
        responses={
            200: PropertyTypeSerializer,
            404: {'description': 'Property type not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="List Regions",
        description="Get a list of all regions/locations where properties are available. Supports optional search.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Search regions by name", required=False),
        ],
        responses={200: RegionSerializer(many=True)}
    )
    @swagger_auto_schema(
        operation_description="Get a list of all regions/locations where properties are available. Supports optional search.",
        operation_summary="List Regions",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search regions by name", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: RegionSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all regions with optional search"""
        regions = Region.objects.all()
        
        # Optional search filter
        search_query = request.GET.get('search', '').strip()
        if search_query:
            regions = regions.filter(name__icontains=search_query)
        
        regions = regions.order_by('name')
        serializer = RegionSerializer(regions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegionDetailAPIView(APIView):
    """
    API endpoint to get region details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get Region Details",
        description="Get detailed information about a specific region by ID",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Region ID", required=True),
        ],
        responses={
            200: RegionSerializer,
            404: {'description': 'Region not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="List Districts",
        description="Get a list of all districts within regions. Supports optional filtering.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Search districts by name", required=False),
            OpenApiParameter('region', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter districts by region ID", required=False),
        ],
        responses={200: DistrictSerializer(many=True)}
    )
    @swagger_auto_schema(
        operation_description="Get a list of all districts within regions. Supports optional filtering.",
        operation_summary="List Districts",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search districts by name", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filter districts by region ID", type=openapi.TYPE_INTEGER, required=False),
        ],
        responses={
            200: DistrictSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all districts with optional filtering"""
        districts = District.objects.all().select_related('region')
        
        # Optional search filter
        search_query = request.GET.get('search', '').strip()
        if search_query:
            districts = districts.filter(name__icontains=search_query)
        
        # Optional region filter
        region_id = request.GET.get('region')
        if region_id:
            try:
                districts = districts.filter(region_id=int(region_id))
            except (ValueError, TypeError):
                pass
        
        districts = districts.order_by('name')
        serializer = DistrictSerializer(districts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DistrictDetailAPIView(APIView):
    """
    API endpoint to get district details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get District Details",
        description="Get detailed information about a specific district by ID",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="District ID", required=True),
        ],
        responses={
            200: DistrictSerializer,
            404: {'description': 'District not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="List Amenities",
        description="Get a list of all available amenities (WiFi, Parking, Pool, etc.). Supports optional search.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Search amenities by name", required=False),
        ],
        responses={200: AmenitySerializer(many=True)}
    )
    @swagger_auto_schema(
        operation_description="Get a list of all property amenities (e.g., WiFi, Parking, Pool, etc.). Supports optional search.",
        operation_summary="List Amenities",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search amenities by name", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: AmenitySerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        """Get all amenities with optional search"""
        amenities = Amenity.objects.all()
        
        # Optional search filter
        search_query = request.GET.get('search', '').strip()
        if search_query:
            amenities = amenities.filter(name__icontains=search_query)
        
        amenities = amenities.order_by('name')
        serializer = AmenitySerializer(amenities, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AmenityDetailAPIView(APIView):
    """
    API endpoint to get amenity details.
    Public endpoint - no authentication required.
    """
    permission_classes = [AllowAny]

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get Amenity Details",
        description="Get detailed information about a specific amenity by ID",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('pk', OpenApiTypes.INT, OpenApiParameter.PATH, description="Amenity ID", required=True),
        ],
        responses={
            200: AmenitySerializer,
            404: {'description': 'Amenity not found'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Upload Property Image",
        description="Upload an image for a property. User must own the property.",
        tags=['Properties'],
        request=PropertyImageUploadSerializer,
        responses={
            201: PropertyImageUploadSerializer,
            400: {'description': 'Validation error'},
            401: {'description': 'Authentication required'},
            403: {'description': 'Permission denied - you must own the property'}
        }
    )
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

    # CRITICAL: @extend_schema must be BEFORE @swagger_auto_schema for drf-spectacular
    @extend_schema(
        summary="Get Favorite Properties",
        description="Get a list of properties favorited by the current authenticated user. Supports pagination and optional filtering.",
        tags=['Properties'],
        parameters=[
            OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Page number for pagination (default: 1)", required=False),
            OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Number of items per page (default: 20, max: 100)", required=False),
            OpenApiParameter('property_type', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter favorites by property type ID", required=False),
            OpenApiParameter('category', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter favorites by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", required=False),
        ],
        responses={
            200: PropertyFavoriteSerializer(many=True),
            401: {'description': 'Authentication required'}
        }
    )
    @swagger_auto_schema(
        operation_description="Get a list of properties favorited by the current authenticated user. Supports pagination and optional filtering.",
        operation_summary="Get Favorite Properties",
        tags=['Properties'],
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination (default: 1)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page (default: 20, max: 100)", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter favorites by property type ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter favorites by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", type=openapi.TYPE_STRING, required=False),
        ],
        responses={
            200: PropertyFavoriteSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def get(self, request, *args, **kwargs):
        """Get current user's favorite properties with optional pagination and filtering"""
        favorites = PropertyFavorite.objects.filter(user=request.user).select_related('property', 'property__property_type').order_by('-created_at')
        
        # Filter by property_type ID (if provided)
        property_type_id = request.GET.get('property_type')
        if property_type_id:
            try:
                favorites = favorites.filter(property__property_type_id=int(property_type_id))
            except (ValueError, TypeError):
                pass
        
        # Filter by category name (if provided)
        category_name = request.GET.get('category')
        if category_name:
            category_name = category_name.lower().strip()
            favorites = favorites.filter(property__property_type__name__iexact=category_name)
        
        # Pagination
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)
        
        try:
            page = int(page)
            page_size = int(page_size)
            # Limit max page size
            if page_size > 100:
                page_size = 100
            if page_size < 1:
                page_size = 20
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        # Calculate pagination
        total = favorites.count()
        start = (page - 1) * page_size
        end = start + page_size
        favorites_page = favorites[start:end]
        
        serializer = PropertyFavoriteSerializer(favorites_page, many=True, context={'request': request})
        
        # Return paginated response
        return Response({
            'count': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if total > 0 else 0,
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Toggle Property Favorite",
    description="Add or remove a property from user's favorites. If property is already favorited, it will be removed. If not favorited, it will be added.",
    tags=['Properties'],
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'required': ['property_id'],
                'properties': {
                    'property_id': {
                        'type': 'integer',
                        'description': 'ID of the property to favorite/unfavorite'
                    }
                }
            }
        }
    },
    responses={
        200: {
            'description': 'Favorite status toggled successfully',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'is_favorited': {'type': 'boolean', 'description': 'Whether the property is now favorited'},
                            'favorites_count': {'type': 'integer', 'description': 'Total number of users who favorited this property'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {'description': 'Invalid property ID'},
        401: {'description': 'Authentication required'},
        404: {'description': 'Property not found'}
    }
)
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
        400: openapi.Response(
            description="Invalid property ID",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        401: openapi.Response(
            description="Authentication required",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        ),
        404: openapi.Response(
            description="Property not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        )
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

# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular to detect parameters
@extend_schema(
    summary="Search Properties",
    description="Search properties with filters. Supports search by title, description, address, property type (ID) or category (name), region, bedrooms, rent range, etc. Supports pagination.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Search query (title, description, address)", required=False),
        OpenApiParameter('property_type', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by property type ID", required=False),
        OpenApiParameter('category', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", required=False),
        OpenApiParameter('region', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by region ID", required=False),
        OpenApiParameter('district', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Filter by district ID", required=False),
        OpenApiParameter('min_bedrooms', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Minimum bedrooms", required=False),
        OpenApiParameter('max_bedrooms', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Maximum bedrooms", required=False),
        OpenApiParameter('min_rent', OpenApiTypes.NUMBER, OpenApiParameter.QUERY, description="Minimum rent amount", required=False),
        OpenApiParameter('max_rent', OpenApiTypes.NUMBER, OpenApiParameter.QUERY, description="Maximum rent amount", required=False),
        OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", required=False),
        OpenApiParameter('page', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Page number for pagination (default: 1)", required=False),
        OpenApiParameter('page_size', OpenApiTypes.INT, OpenApiParameter.QUERY, description="Number of items per page (default: 20, max: 100)", required=False),
    ],
    responses={200: PropertyListSerializer(many=True)}
)
@swagger_auto_schema(
    method='get',
    operation_description="Search properties with filters. Supports search by title, description, address, property type (ID) or category (name), region, bedrooms, rent range, etc. Supports pagination.",
    operation_summary="Search Properties",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search query (title, description, address)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('district', openapi.IN_QUERY, description="Filter by district ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('min_bedrooms', openapi.IN_QUERY, description="Minimum bedrooms", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('max_bedrooms', openapi.IN_QUERY, description="Maximum bedrooms", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('min_rent', openapi.IN_QUERY, description="Minimum rent amount", type=openapi.TYPE_NUMBER, required=False),
        openapi.Parameter('max_rent', openapi.IN_QUERY, description="Maximum rent amount", type=openapi.TYPE_NUMBER, required=False),
        openapi.Parameter('status', openapi.IN_QUERY, description="Filter by status (available, rented, under_maintenance, unavailable)", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination (default: 1)", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page (default: 20, max: 100)", type=openapi.TYPE_INTEGER, required=False),
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
    # Filter by property_type ID (if provided)
    property_type_id = request.GET.get('property_type')
    if property_type_id:
        try:
            properties = properties.filter(property_type_id=int(property_type_id))
        except (ValueError, TypeError):
            pass
    
    # Filter by category name (for mobile app compatibility)
    # This allows filtering by category name like 'house', 'hotel', 'lodge', 'venue'
    category_name = request.GET.get('category')
    if category_name:
        # Normalize category name to lowercase for matching
        category_name = category_name.lower().strip()
        properties = properties.filter(property_type__name__iexact=category_name)
    
    region_id = request.GET.get('region')
    if region_id:
        try:
            properties = properties.filter(region_id=int(region_id))
        except (ValueError, TypeError):
            pass
    
    district_id = request.GET.get('district')
    if district_id:
        try:
            properties = properties.filter(district_id=int(district_id))
        except (ValueError, TypeError):
            pass
    
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
    
    # Pagination
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 20)
    
    try:
        page = int(page)
        page_size = int(page_size)
        if page_size > 100:
            page_size = 100
        if page_size < 1:
            page_size = 20
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1
        page_size = 20
    
    # Calculate pagination
    total = properties.count()
    start = (page - 1) * page_size
    end = start + page_size
    properties_page = properties[start:end]
    
    serializer = PropertyListSerializer(properties_page, many=True, context={'request': request})
    
    # Return paginated response
    return Response({
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size if total > 0 else 0,
        'results': serializer.data
    }, status=status.HTTP_200_OK)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular to detect parameters
@extend_schema(
    summary="Get Featured Properties",
    description="Get featured properties (properties marked as featured). Supports optional filtering.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of properties to return (default: all, max: 100)',
            required=False
        ),
        OpenApiParameter(
            name='property_type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter by property type ID',
            required=False
        ),
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')",
            required=False
        ),
        OpenApiParameter(
            name='region',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter by region ID',
            required=False
        ),
    ],
    responses={200: PropertyListSerializer(many=True)}
)
@swagger_auto_schema(
    method='get',
    operation_description="Get featured properties (properties marked as featured). Supports optional filtering.",
    operation_summary="Get Featured Properties",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter('limit', openapi.IN_QUERY, description="Number of properties to return (default: all, max: 100)", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region ID", type=openapi.TYPE_INTEGER, required=False),
    ],
    responses={
        200: PropertyListSerializer(many=True)
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def featured_properties(request):
    """Get featured properties with optional filtering"""
    properties = Property.objects.filter(
        is_active=True,
        is_approved=True,
        is_featured=True
    ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities')
    
    # Filter by property_type ID (if provided)
    property_type_id = request.GET.get('property_type')
    if property_type_id:
        try:
            properties = properties.filter(property_type_id=int(property_type_id))
        except (ValueError, TypeError):
            pass
    
    # Filter by category name (if provided)
    category_name = request.GET.get('category')
    if category_name:
        category_name = category_name.lower().strip()
        properties = properties.filter(property_type__name__iexact=category_name)
    
    # Filter by region ID (if provided)
    region_id = request.GET.get('region')
    if region_id:
        try:
            properties = properties.filter(region_id=int(region_id))
        except (ValueError, TypeError):
            pass
    
    properties = properties.order_by('-created_at')
    
    # Optional limit
    limit = request.GET.get('limit')
    if limit:
        try:
            limit = int(limit)
            if limit > 100:
                limit = 100
            if limit > 0:
                properties = properties[:limit]
        except (ValueError, TypeError):
            pass
    
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular to detect parameters
@extend_schema(
    summary="Get Recent Properties",
    description="Get recently added properties (most recent first). Supports optional filtering.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter(
            name='limit',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Number of properties to return (default: 10, max: 100)',
            required=False
        ),
        OpenApiParameter(
            name='property_type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter by property type ID',
            required=False
        ),
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')",
            required=False
        ),
        OpenApiParameter(
            name='region',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter by region ID',
            required=False
        ),
    ],
    responses={200: PropertyListSerializer(many=True)}
)
@swagger_auto_schema(
    method='get',
    operation_description="Get recently added properties (most recent first). Supports optional filtering.",
    operation_summary="Get Recent Properties",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter('limit', openapi.IN_QUERY, description="Number of properties to return (default: 10, max: 100)", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter by property type ID", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category name (e.g., 'house', 'hotel', 'lodge', 'venue')", type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('region', openapi.IN_QUERY, description="Filter by region ID", type=openapi.TYPE_INTEGER, required=False),
    ],
    responses={
        200: PropertyListSerializer(many=True)
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def recent_properties(request):
    """Get recent properties with optional filtering"""
    properties = Property.objects.filter(
        is_active=True,
        is_approved=True
    ).select_related('property_type', 'region', 'owner').prefetch_related('images', 'amenities')
    
    # Filter by property_type ID (if provided)
    property_type_id = request.GET.get('property_type')
    if property_type_id:
        try:
            properties = properties.filter(property_type_id=int(property_type_id))
        except (ValueError, TypeError):
            pass
    
    # Filter by category name (if provided)
    category_name = request.GET.get('category')
    if category_name:
        category_name = category_name.lower().strip()
        properties = properties.filter(property_type__name__iexact=category_name)
    
    # Filter by region ID (if provided)
    region_id = request.GET.get('region')
    if region_id:
        try:
            properties = properties.filter(region_id=int(region_id))
        except (ValueError, TypeError):
            pass
    
    properties = properties.order_by('-created_at')
    
    # Apply limit
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 10
    except (ValueError, TypeError):
        limit = 10
    
    properties = properties[:limit]
    
    serializer = PropertyListSerializer(properties, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular to detect parameters
@extend_schema(
    summary="Get Property Statistics",
    description="Get property statistics including total properties, available properties, rented properties, average rent, and breakdowns by type and region. Supports optional filtering by region.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter(
            name='region',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter statistics by region ID (optional)',
            required=False
        ),
        OpenApiParameter(
            name='property_type',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Filter statistics by property type ID (optional)',
            required=False
        ),
    ],
    responses={
        200: {
            'description': 'Property statistics',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'total_properties': {'type': 'integer'},
                            'available_properties': {'type': 'integer'},
                            'rented_properties': {'type': 'integer'},
                            'under_maintenance': {'type': 'integer'},
                            'average_rent': {'type': 'number'},
                            'properties_by_type': {'type': 'object'},
                            'properties_by_region': {'type': 'object'},
                        }
                    }
                }
            }
        }
    }
)
@swagger_auto_schema(
    method='get',
    operation_description="Get property statistics including total properties, available properties, rented properties, average rent, and breakdowns by type and region. Supports optional filtering by region.",
    operation_summary="Get Property Statistics",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter('region', openapi.IN_QUERY, description="Filter statistics by region ID (optional)", type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('property_type', openapi.IN_QUERY, description="Filter statistics by property type ID (optional)", type=openapi.TYPE_INTEGER, required=False),
    ],
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
    """Get property statistics with optional filtering"""
    from django.db.models import Count, Avg
    
    # Base queryset
    base_filter = {'is_approved': True}
    
    # Optional region filter
    region_id = request.GET.get('region')
    if region_id:
        try:
            base_filter['region_id'] = int(region_id)
        except (ValueError, TypeError):
            pass
    
    # Optional property_type filter
    property_type_id = request.GET.get('property_type')
    if property_type_id:
        try:
            base_filter['property_type_id'] = int(property_type_id)
        except (ValueError, TypeError):
            pass
    
    total_properties = Property.objects.filter(**base_filter).count()
    available_properties = Property.objects.filter(status='available', is_active=True, **base_filter).count()
    rented_properties = Property.objects.filter(status='rented', **base_filter).count()
    under_maintenance = Property.objects.filter(status='under_maintenance', **base_filter).count()
    
    average_rent = Property.objects.filter(
        rent_amount__isnull=False,
        **base_filter
    ).aggregate(avg_rent=Avg('rent_amount'))['avg_rent'] or 0
    
    # Properties by type (with optional filter)
    type_filter = Q(properties__is_approved=True)
    if property_type_id:
        try:
            type_filter &= Q(properties__property_type_id=int(property_type_id))
        except (ValueError, TypeError):
            pass
    
    properties_by_type = PropertyType.objects.annotate(
        count=Count('properties', filter=type_filter)
    ).values('id', 'name', 'count')
    
    # Properties by region (with optional filter)
    region_filter = Q(properties__is_approved=True)
    if region_id:
        try:
            region_filter &= Q(properties__region_id=int(region_id))
        except (ValueError, TypeError):
            pass
    
    properties_by_region = Region.objects.annotate(
        count=Count('properties', filter=region_filter)
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
# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Booking Details",
    description="Get detailed information about a specific booking by ID. User must be the booking tenant or property owner.",
    tags=['Bookings'],
    parameters=[
        OpenApiParameter('booking_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Booking ID", required=True),
    ],
    responses={
        200: {'description': 'Booking details'},
        401: {'description': 'Authentication required'},
        403: {'description': 'Permission denied'},
        404: {'description': 'Booking not found'}
    }
)
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
    """Get booking details - handles both properties.Booking and documents.Booking"""
    try:
        # Try properties.Booking first (web admin bookings)
        from .models import Booking as PropertiesBooking
        try:
            booking = PropertiesBooking.objects.select_related('customer', 'property_obj', 'created_by').get(pk=booking_id)
            
            # Check permissions - created_by or property owner
            if booking.created_by != request.user and booking.property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
                return Response(
                    {"detail": "You do not have permission to view this booking."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return Response({
                'id': booking.id,
                'booking_reference': booking.booking_reference,
                'property': booking.property_obj.id,
                'property_title': booking.property_obj.title,
                'customer': {
                    'id': booking.customer.id,
                    'full_name': booking.customer.full_name,
                    'email': booking.customer.email,
                    'phone': booking.customer.phone,
                },
                'check_in_date': booking.check_in_date.strftime('%Y-%m-%d'),
                'check_out_date': booking.check_out_date.strftime('%Y-%m-%d'),
                'number_of_guests': booking.number_of_guests,
                'room_number': booking.room_number,
                'room_type': booking.room_type,
                'total_amount': float(booking.total_amount),
                'paid_amount': float(booking.paid_amount),
                'booking_status': booking.booking_status,
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else None,
            }, status=status.HTTP_200_OK)
        except PropertiesBooking.DoesNotExist:
            pass
        
        # Try documents.Booking (mobile app bookings)
        from documents.models import Booking as DocumentBooking
        booking = get_object_or_404(DocumentBooking, pk=booking_id)
        
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
            'check_in': booking.check_in.strftime('%Y-%m-%d') if booking.check_in else None,
            'check_out': booking.check_out.strftime('%Y-%m-%d') if booking.check_out else None,
            'total_amount': str(booking.total_amount),
            'status': booking.status,
            'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else None,
            'nights': booking.nights if hasattr(booking, 'nights') else None,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response(
            {"detail": f"Error retrieving booking: {str(e)}", "traceback": traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Update Booking Status",
    description="Update booking status. User must be property owner or admin. Can use either 'action' (confirm, check_in, check_out, cancel) or 'status' (pending, confirmed, checked_in, checked_out, cancelled).",
    tags=['Bookings'],
    parameters=[
        OpenApiParameter('booking_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Booking ID", required=True),
    ],
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'enum': ['confirm', 'check_in', 'check_out', 'cancel'],
                        'description': 'Action to perform (alternative to status)'
                    },
                    'status': {
                        'type': 'string',
                        'enum': ['pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'completed'],
                        'description': 'New booking status (alternative to action)'
                    }
                }
            }
        }
    },
    responses={
        200: {'description': 'Status updated successfully'},
        400: {'description': 'Invalid status or action'},
        401: {'description': 'Authentication required'},
        403: {'description': 'Permission denied'},
        404: {'description': 'Booking not found'}
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Update booking status. User must be property owner or admin. Can use either 'action' (confirm, check_in, check_out, cancel) or 'status' (pending, confirmed, checked_in, checked_out, cancelled).",
    operation_summary="Update Booking Status",
    tags=['Bookings'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'action': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['confirm', 'check_in', 'check_out', 'cancel'],
                description='Action to perform (alternative to status)'
            ),
            'status': openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=['pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'completed'],
                description='New booking status (alternative to action)'
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
        400: "Invalid status or action",
        401: "Authentication required",
        403: "Permission denied",
        404: "Booking not found"
    },
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def booking_status_update_api(request, booking_id):
    """Update booking status - handles both properties.Booking and documents.Booking"""
    try:
        # Get action or status from request
        action = request.data.get('action')
        new_status = request.data.get('status')
        
        # Map actions to statuses for properties.Booking
        action_to_status = {
            'confirm': 'confirmed',
            'check_in': 'checked_in',
            'check_out': 'checked_out',
            'cancel': 'cancelled'
        }
        
        # Try properties.Booking first (web admin bookings)
        from .models import Booking as PropertiesBooking
        try:
            booking = PropertiesBooking.objects.select_related('property_obj', 'created_by').get(pk=booking_id)
            
            # Check permissions - created_by or property owner
            if booking.created_by != request.user and booking.property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
                return Response(
                    {"detail": "You do not have permission to update this booking."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Determine new status
            if action and action in action_to_status:
                new_status = action_to_status[action]
            elif not new_status:
                return Response(
                    {"detail": "Either 'action' or 'status' must be provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate status
            valid_statuses = ['pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show']
            if new_status not in valid_statuses:
                return Response(
                    {"detail": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            booking.booking_status = new_status
            booking.save()
            
            # If booking is cancelled and has a room assigned, sync room status
            # This applies to both hotel and lodge bookings
            if new_status == 'cancelled' and booking.room_number and booking.property_obj:
                try:
                    from .models import Room
                    room = Room.objects.get(
                        property_obj=booking.property_obj,
                        room_number=booking.room_number
                    )
                    # Use the sync method to properly update room status based on all bookings
                    room.sync_status_from_bookings()
                except Room.DoesNotExist:
                    # Room might not exist (e.g., for house bookings), that's okay
                    pass
            
            return Response({
                'success': True,
                'id': booking.id,
                'status': booking.booking_status,
                'message': f'Booking status updated to {new_status}'
            }, status=status.HTTP_200_OK)
        except PropertiesBooking.DoesNotExist:
            pass
        
        # Try documents.Booking (mobile app bookings)
        from documents.models import Booking as DocumentBooking
        booking = get_object_or_404(DocumentBooking, pk=booking_id)
        
        # Check permissions - property owner or admin
        if booking.property_ref.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to update this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Determine new status
        if action and action in action_to_status:
            new_status = action_to_status[action]
        elif not new_status:
            return Response(
                {"detail": "Either 'action' or 'status' must be provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
            return Response(
                {"detail": "Invalid status. Must be one of: pending, confirmed, cancelled, completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = new_status
        booking.save()
        
        return Response({
            'success': True,
            'id': booking.id,
            'status': booking.status,
            'message': f'Booking status updated to {new_status}'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response(
            {"detail": f"Error updating booking: {str(e)}", "traceback": traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Edit Booking",
    description="Edit booking details. User must be property owner or admin.",
    tags=['Bookings'],
    parameters=[
        OpenApiParameter('booking_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Booking ID", required=True),
    ],
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'check_in': {'type': 'string', 'format': 'date', 'description': 'Check-in date (YYYY-MM-DD)'},
                    'check_out': {'type': 'string', 'format': 'date', 'description': 'Check-out date (YYYY-MM-DD)'},
                    'total_amount': {'type': 'number', 'description': 'Total booking amount'}
                }
            }
        }
    },
    responses={
        200: {'description': 'Booking updated successfully'},
        400: {'description': 'Validation error'},
        401: {'description': 'Authentication required'},
        403: {'description': 'Permission denied'},
        404: {'description': 'Booking not found'}
    }
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
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def booking_edit_api(request, booking_id):
    """Edit booking - handles both properties.Booking and documents.Booking"""
    try:
        from django.utils.dateparse import parse_date
        
        # Try properties.Booking first (web admin bookings)
        from .models import Booking as PropertiesBooking
        try:
            booking = PropertiesBooking.objects.select_related('customer', 'property_obj', 'created_by').get(pk=booking_id)
            
            # Check permissions - created_by or property owner
            if booking.created_by != request.user and booking.property_obj.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
                return Response(
                    {"detail": "You do not have permission to edit this booking."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # GET request - return booking data
            if request.method == 'GET':
                return Response({
                    'id': booking.id,
                    'booking_reference': booking.booking_reference,
                    'customer': {
                        'id': booking.customer.id,
                        'first_name': booking.customer.first_name,
                        'last_name': booking.customer.last_name,
                        'full_name': booking.customer.full_name,
                        'email': booking.customer.email,
                        'phone': booking.customer.phone,
                        'address': booking.customer.address,
                    },
                    'check_in_date': booking.check_in_date.strftime('%Y-%m-%d') if booking.check_in_date else None,
                    'check_out_date': booking.check_out_date.strftime('%Y-%m-%d') if booking.check_out_date else None,
                    'number_of_guests': booking.number_of_guests,
                    'room_number': booking.room_number,
                    'room_type': booking.room_type,
                    'total_amount': float(booking.total_amount),
                    'paid_amount': float(booking.paid_amount),
                    'booking_status': booking.booking_status,
                    'payment_status': booking.payment_status,
                    'special_requests': booking.special_requests,
                    'notes': getattr(booking, 'notes', ''),
                }, status=status.HTTP_200_OK)
            
            # POST request - update booking
            if 'check_in_date' in request.data:
                check_in = parse_date(request.data['check_in_date'])
                if check_in:
                    booking.check_in_date = check_in
            
            if 'check_out_date' in request.data:
                check_out = parse_date(request.data['check_out_date'])
                if check_out:
                    booking.check_out_date = check_out
            
            if 'number_of_guests' in request.data:
                try:
                    booking.number_of_guests = int(request.data['number_of_guests'])
                except (ValueError, TypeError):
                    pass
            
            if 'room_number' in request.data:
                booking.room_number = request.data['room_number']
            
            if 'room_type' in request.data:
                booking.room_type = request.data['room_type']
            
            if 'total_amount' in request.data:
                try:
                    booking.total_amount = float(request.data['total_amount'])
                except (ValueError, TypeError):
                    return Response(
                        {"detail": "Invalid total_amount"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if 'special_requests' in request.data:
                booking.special_requests = request.data['special_requests']
            
            if 'notes' in request.data:
                booking.notes = request.data['notes']
            
            # Update customer information if provided
            if 'customer' in request.data:
                customer_data = request.data['customer']
                customer = booking.customer
                
                try:
                    if 'first_name' in customer_data:
                        customer.first_name = customer_data['first_name'].strip() if customer_data['first_name'] else ''
                    if 'last_name' in customer_data:
                        customer.last_name = customer_data['last_name'].strip() if customer_data['last_name'] else ''
                    if 'email' in customer_data:
                        email = customer_data['email'].strip() if customer_data['email'] else ''
                        if email:
                            # Validate email uniqueness (excluding current customer)
                            from .models import Customer as CustomerModel
                            existing_customer = CustomerModel.objects.filter(email=email).exclude(id=customer.id).first()
                            if existing_customer:
                                return Response(
                                    {"detail": f"Email {email} is already in use by another customer ({existing_customer.full_name})."},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            customer.email = email
                    if 'phone' in customer_data:
                        # Validate phone uniqueness (excluding current customer)
                        phone = customer_data['phone'].strip() if customer_data['phone'] else ''
                        if phone:
                            # Check if phone already exists for another customer
                            from .models import Customer as CustomerModel
                            existing_customer = CustomerModel.objects.filter(phone=phone).exclude(id=customer.id).first()
                            if existing_customer:
                                return Response(
                                    {"detail": f"Phone number {phone} is already in use by another customer ({existing_customer.full_name})."},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            customer.phone = phone
                        elif not phone:
                            # Phone is required - don't allow empty phone
                            return Response(
                                {"detail": "Phone number is required and cannot be empty."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    if 'address' in customer_data:
                        customer.address = customer_data['address'].strip() if customer_data['address'] else None
                    
                    customer.save()
                except Exception as e:
                    import traceback
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error updating customer for booking {booking_id}: {str(e)}")
                    logger.error(traceback.format_exc())
                    return Response(
                        {"detail": f"Error updating customer information: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            booking.save()
            
            return Response({
                'success': True,
                'id': booking.id,
                'message': 'Booking updated successfully'
            }, status=status.HTTP_200_OK)
        except PropertiesBooking.DoesNotExist:
            pass
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating booking {booking_id}: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {"detail": f"Error updating booking: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Try documents.Booking (mobile app bookings)
        from documents.models import Booking as DocumentBooking
        booking = get_object_or_404(DocumentBooking, pk=booking_id)
        
        # Check permissions - property owner or admin
        if booking.property_ref.owner != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response(
                {"detail": "You do not have permission to edit this booking."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # GET request - return booking data
        if request.method == 'GET':
            return Response({
                'id': booking.id,
                'check_in': booking.check_in.strftime('%Y-%m-%d') if booking.check_in else None,
                'check_out': booking.check_out.strftime('%Y-%m-%d') if booking.check_out else None,
                'total_amount': str(booking.total_amount),
            }, status=status.HTTP_200_OK)
        
        # POST request - update booking
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
            'success': True,
            'id': booking.id,
            'check_in': booking.check_in.strftime('%Y-%m-%d') if booking.check_in else None,
            'check_out': booking.check_out.strftime('%Y-%m-%d') if booking.check_out else None,
            'total_amount': str(booking.total_amount),
            'message': 'Booking updated successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response(
            {"detail": f"Error editing booking: {str(e)}", "traceback": traceback.format_exc()},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ---------------------------------------------------------------------------
# Visit payment / property visit endpoints
# ---------------------------------------------------------------------------

# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Property Visit Status",
    description="Get property visit payment status. Check if visit payment has been made for a property.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter('property_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
    ],
    responses={
        200: {
            'description': 'Visit payment status',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'has_paid': {'type': 'boolean', 'description': 'Whether user has an active (non-expired) visit payment'},
                            'is_expired': {'type': 'boolean', 'description': 'Whether the visit payment has expired (72 hours from payment)'},
                            'visit_cost': {'type': 'number'},
                            'paid_at': {'type': 'string', 'format': 'date-time', 'description': 'When the payment was made'},
                            'expires_at': {'type': 'string', 'format': 'date-time', 'description': 'When the visit payment expires (72 hours after payment)'},
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'},
        404: {'description': 'Property not found'}
    }
)
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
                    'has_paid': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether user has an active (non-expired) visit payment'),
                    'is_expired': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the visit payment has expired (72 hours from payment)'),
                    'visit_cost': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'paid_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='When the payment was made'),
                    'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='When the visit payment expires (72 hours after payment)'),
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
    from django.utils import timezone
    
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Check if user has paid for visit
    from .models import PropertyVisitPayment
    visit_payment = PropertyVisitPayment.objects.filter(
        property=property_obj,
        user=request.user,
        status='completed'
    ).first()
    
    # Check if payment exists and is still active (not expired)
    has_paid = visit_payment is not None and visit_payment.is_active()
    is_expired = visit_payment is not None and visit_payment.is_expired() if visit_payment else False
    visit_cost = property_obj.visit_cost or 0
    
    response_data = {
        'has_paid': has_paid,
        'visit_cost': float(visit_cost) if visit_cost else 0,
        'is_expired': is_expired,
        'message': 'Visit payment completed' if has_paid else ('Visit payment expired. Please pay again.' if is_expired else 'Visit payment pending')
    }
    
    # Add expiration info if payment exists
    if visit_payment:
        expires_at = visit_payment.expires_at()
        response_data['paid_at'] = visit_payment.paid_at.isoformat() if visit_payment.paid_at else None
        response_data['expires_at'] = expires_at.isoformat() if expires_at else None
    
    return Response(response_data, status=status.HTTP_200_OK)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Initiate Property Visit Payment",
    description="Initiate a property visit payment. Creates a payment request for visiting the property.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter('property_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
    ],
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'properties': {
                    'payment_method': {
                        'type': 'string',
                        'description': 'Payment method (e.g., mobile_money, card)'
                    }
                }
            }
        }
    },
    responses={
        200: {'description': 'Payment initiated successfully'},
        400: {'description': 'Invalid request'},
        401: {'description': 'Authentication required'},
        404: {'description': 'Property not found'}
    }
)
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
    """
    Initiate property visit payment for house properties.
    
    Creates a payment record and initiates AZAM Pay gateway payment.
    Uses smart phone logic: Always uses the customer's own profile phone
    (since visit payments are always made by the customer themselves).
    
    Only available for house properties.
    """
    property_obj = get_object_or_404(Property, pk=property_id)
    
    # Only house properties support visit payments
    if property_obj.property_type.name.lower() != 'house':
        return Response(
            {"error": "Visit payment is only available for house properties."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not property_obj.visit_cost or property_obj.visit_cost <= 0:
        return Response(
            {"error": "Visit cost is not set for this property."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already paid and still active
    from .models import PropertyVisitPayment
    from payments.models import Payment, PaymentProvider, PaymentTransaction
    from payments.gateway_service import PaymentGatewayService
    from django.conf import settings
    from django.utils import timezone
    
    existing_payment = PropertyVisitPayment.objects.filter(
        property=property_obj,
        user=request.user,
        status='completed'
    ).first()
    
    # If payment exists and is still active (not expired), return success
    if existing_payment and existing_payment.is_active():
        return Response({
            'success': True,
            'message': 'Visit payment already completed and active',
            'payment_id': existing_payment.id,
            'status': 'completed',
            'expires_at': existing_payment.expires_at().isoformat() if existing_payment.expires_at() else None
        }, status=status.HTTP_200_OK)
    
    # If payment exists but expired, allow re-payment by resetting to pending
    if existing_payment and existing_payment.is_expired():
        # Reset to pending to allow new payment
        existing_payment.status = 'pending'
        existing_payment.paid_at = None
        existing_payment.transaction_id = None
        existing_payment.gateway_reference = None
        existing_payment.amount = property_obj.visit_cost  # Update amount in case it changed
        existing_payment.save()
        visit_payment = existing_payment
        created = False
    else:
        # Get or create pending visit payment
        visit_payment, created = PropertyVisitPayment.objects.get_or_create(
            property=property_obj,
            user=request.user,
            defaults={
                'amount': property_obj.visit_cost,
                'status': 'pending'
            }
        )
    
    # Get payment method from request (default: mobile_money)
    payment_method = request.data.get('payment_method', 'mobile_money')
    
    # Get mobile money provider if this is a mobile_money payment
    mobile_money_provider = None
    if payment_method == 'mobile_money':
        mobile_money_provider = request.data.get('mobile_money_provider', '').strip()
        if not mobile_money_provider:
            return Response({
                'error': 'Mobile Money Provider is required for mobile money payments. Please provide: AIRTEL, TIGO, MPESA, or HALOPESA'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create payment provider (AZAM Pay)
    provider, _ = PaymentProvider.objects.get_or_create(
        name='AZAM Pay',
        defaults={'description': 'AZAM Pay Payment Gateway'}
    )
    
    # Create or get payment record
    if visit_payment.payment:
        payment = visit_payment.payment
        payment.amount = visit_payment.amount
        payment.payment_method = payment_method
        if mobile_money_provider:
            payment.mobile_money_provider = mobile_money_provider.upper()
        payment.status = 'pending'
        payment.save()
    else:
        payment = Payment.objects.create(
            tenant=request.user,
            provider=provider,
            amount=visit_payment.amount,
            payment_method=payment_method,
            mobile_money_provider=mobile_money_provider.upper() if mobile_money_provider else None,
            status='pending',
            notes=f'Visit payment for property: {property_obj.title}',
            recorded_by=request.user
        )
        
        # Link visit payment to unified payment
        visit_payment.payment = payment
        visit_payment.save()
    
    # Get callback URL
    callback_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', None)
    if not callback_url:
        base_domain = getattr(settings, 'BASE_URL', 'https://portal.maishaapp.co.tz')
        callback_url = f"{base_domain}/api/v1/payments/webhook/azam-pay/"
    
    # Initiate payment with gateway (uses smart phone logic)
    # For visit payments, smart logic will use customer's own phone (payment.tenant.profile.phone)
    gateway_result = PaymentGatewayService.initiate_payment(
        payment=payment,
        provider_name='azam pay',
        callback_url=callback_url,
        payment_method='mobile_money'  # Visit payments always use mobile_money
    )
    
    if not gateway_result.get('success'):
        return Response({
            'error': gateway_result.get('error', 'Failed to initiate payment'),
            'details': gateway_result
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create PaymentTransaction record with the actual payload sent to AZAM Pay
    request_payload = gateway_result.get('request_payload', {})
    if not request_payload:
        request_payload = {'property_id': property_id, 'visit_payment_id': visit_payment.id}
    
    transaction = PaymentTransaction.objects.create(
        payment=payment,
        provider=provider,
        gateway_transaction_id=gateway_result.get('transaction_id'),
        azam_reference=gateway_result.get('reference'),
        status='initiated',
        request_payload=request_payload,  # Store actual payload sent to AZAM Pay (includes phone number)
        response_payload=gateway_result
    )
    
    # Update visit payment with transaction details
    visit_payment.transaction_id = gateway_result.get('transaction_id')
    visit_payment.gateway_reference = gateway_result.get('reference')
    visit_payment.save()
    
    # Extract phone number from request payload for response
    phone_number_used = request_payload.get('accountNumber') if isinstance(request_payload, dict) else None
    
    return Response({
        'success': True,
        'message': 'Payment initiated successfully. You will receive a payment prompt on your phone.',
        'payment_id': payment.id,
        'visit_payment_id': visit_payment.id,
        'transaction_id': transaction.id,
        'gateway_transaction_id': gateway_result.get('transaction_id'),
        'transaction_reference': gateway_result.get('reference'),
        'phone_number_used': phone_number_used,  # Phone number used for payment
        'amount': float(visit_payment.amount),
        'property_id': property_obj.id,
        'property_title': property_obj.title
    }, status=status.HTTP_201_CREATED)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Verify Property Visit Payment",
    description="Verify property visit payment. Confirms that payment has been completed.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter('property_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
    ],
    request={
        'application/json': {
            'schema': {
                'type': 'object',
                'required': ['payment_reference'],
                'properties': {
                    'payment_reference': {
                        'type': 'string',
                        'description': 'Payment reference/transaction ID'
                    }
                }
            }
        }
    },
    responses={
        200: {'description': 'Payment verified successfully'},
        400: {'description': 'Invalid payment reference'},
        401: {'description': 'Authentication required'},
        404: {'description': 'Property not found'}
    }
)
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
    """
    Verify property visit payment and retrieve owner contact information.
    
    After payment is completed, this endpoint verifies the payment and returns
    owner contact details and property location.
    """
    property_obj = get_object_or_404(Property, pk=property_id)
    
    transaction_id = request.data.get('transaction_id')
    if not transaction_id:
        return Response(
            {"error": "transaction_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    from .models import PropertyVisitPayment
    from payments.gateway_service import PaymentGatewayService
    from django.utils import timezone
    
    # Get visit payment
    visit_payment = PropertyVisitPayment.objects.filter(
        property=property_obj,
        user=request.user,
        transaction_id=transaction_id
    ).first()
    
    if not visit_payment:
        return Response({
            'error': 'Visit payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # If already completed and active, return contact info
    if visit_payment.status == 'completed' and visit_payment.is_active():
        owner = property_obj.owner
        owner_profile = getattr(owner, 'profile', None)
        
        expires_at = visit_payment.expires_at()
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
            'paid_at': visit_payment.paid_at.isoformat() if visit_payment.paid_at else None,
            'expires_at': expires_at.isoformat() if expires_at else None,
            'is_expired': False
        })
    
    # If payment exists but expired, prompt user to pay again
    if visit_payment.status == 'completed' and visit_payment.is_expired():
        expires_at = visit_payment.expires_at()
        return Response({
            'success': False,
            'error': 'Visit payment has expired. Please pay again to access property details.',
            'is_expired': True,
            'paid_at': visit_payment.paid_at.isoformat() if visit_payment.paid_at else None,
            'expires_at': expires_at.isoformat() if expires_at else None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify payment with gateway
    if visit_payment.payment:
        verification_result = PaymentGatewayService.verify_payment(
            visit_payment.payment,
            transaction_id
        )
        
        if verification_result.get('success') and verification_result.get('verified'):
            # Update visit payment status
            visit_payment.status = 'completed'
            visit_payment.paid_at = timezone.now()
            visit_payment.save()
            
            # Update unified payment
            if visit_payment.payment:
                visit_payment.payment.status = 'completed'
                visit_payment.payment.paid_date = timezone.now().date()
                visit_payment.payment.save()
            
            # Get owner contact info
            owner = property_obj.owner
            owner_profile = getattr(owner, 'profile', None)
            
            expires_at = visit_payment.expires_at()
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
                'paid_at': visit_payment.paid_at.isoformat(),
                'expires_at': expires_at.isoformat() if expires_at else None
            })
        else:
            return Response({
                'error': 'Payment verification failed',
                'status': 'failed',
                'details': verification_result
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'Payment record not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# New: property availability API (used by booking forms / tests)
# ---------------------------------------------------------------------------

# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Property Availability",
    description="Get property availability information including booked dates and next available date.",
    tags=['Properties'],
    parameters=[
        OpenApiParameter('property_id', OpenApiTypes.INT, OpenApiParameter.PATH, description="Property ID", required=True),
    ],
    responses={
        200: {'description': 'Property availability information'},
        401: {'description': 'Authentication required'},
        404: {'description': 'Property not found'}
    }
)
@swagger_auto_schema(
    method='get',
    operation_description="Get property availability information including booked dates and next available date.",
    operation_summary="Get Property Availability",
    tags=['Properties'],
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
            description="Property availability information",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        401: "Authentication required",
        404: "Property not found"
    },
    security=[{'Bearer': []}]
)
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


# ---------------------------------------------------------------------------
# Available Rooms API for Mobile App (Hotels/Lodges)
# ---------------------------------------------------------------------------

# Note: extend_schema, OpenApiParameter, and OpenApiTypes are already imported at the top of the file
# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular to detect parameters
@extend_schema(
    summary="Get Available Rooms",
    description="""
    Get available rooms for a hotel or lodge property.
    
    This endpoint returns rooms that are currently available for booking.
    Optionally filter by check-in and check-out dates to see which rooms
    are available for a specific date range.
    
    **Query Parameters:**
    - `property_id` (required): The ID of the hotel/lodge property
    - `check_in_date` (optional): Check-in date in YYYY-MM-DD format
    - `check_out_date` (optional): Check-out date in YYYY-MM-DD format
    
    **Response:**
    Returns a list of available rooms with details including:
    - Room number, type, floor, capacity
    - Bed type, amenities, base rate
    - Availability status
    """,
    tags=['Properties'],
    parameters=[
        OpenApiParameter(
            name='property_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Property ID (required)',
            required=True
        ),
        OpenApiParameter(
            name='check_in_date',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Check-in date (YYYY-MM-DD) - optional',
            required=False
        ),
        OpenApiParameter(
            name='check_out_date',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Check-out date (YYYY-MM-DD) - optional',
            required=False
        ),
    ],
    responses={
        200: {
            'description': 'List of available rooms',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'property_id': {'type': 'integer'},
                            'property_title': {'type': 'string'},
                            'property_type': {'type': 'string'},
                            'total_rooms': {'type': 'integer'},
                            'available_count': {'type': 'integer'},
                            'check_in_date': {'type': 'string', 'format': 'date', 'nullable': True},
                            'check_out_date': {'type': 'string', 'format': 'date', 'nullable': True},
                            'rooms': {
                                'type': 'array',
                                'items': {'type': 'object'}
                            }
                        }
                    }
                }
            }
        },
        400: {'description': 'Bad request'},
        404: {'description': 'Property not found'}
    }
)
@swagger_auto_schema(
    method='get',
    operation_description="""
    Get available rooms for a hotel or lodge property.
    
    This endpoint returns rooms that are currently available for booking.
    Optionally filter by check-in and check-out dates to see which rooms
    are available for a specific date range.
    
    Query Parameters:
    - property_id (required): The ID of the hotel/lodge property
    - check_in_date (optional): Check-in date in YYYY-MM-DD format
    - check_out_date (optional): Check-out date in YYYY-MM-DD format
    """,
    operation_summary="Get Available Rooms",
    tags=['Properties'],
    manual_parameters=[
        openapi.Parameter(
            'property_id',
            openapi.IN_QUERY,
            description="Property ID (required)",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'check_in_date',
            openapi.IN_QUERY,
            description="Check-in date (YYYY-MM-DD) - optional",
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'check_out_date',
            openapi.IN_QUERY,
            description="Check-out date (YYYY-MM-DD) - optional",
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of available rooms",
            schema=openapi.Schema(type=openapi.TYPE_OBJECT)
        ),
        400: "Bad request",
        404: "Property not found"
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])  # Public endpoint - customers need to see available rooms
def available_rooms_api(request):
    """
    REST API endpoint to get available rooms for hotels and lodges.
    
    This is specifically designed for mobile apps to display available rooms
    so customers can choose which room to book.
    
    Query Parameters:
    - property_id (required): ID of the property
    - check_in_date (optional): Filter by check-in date (YYYY-MM-DD)
    - check_out_date (optional): Filter by check-out date (YYYY-MM-DD)
    """
    from datetime import datetime
    
    try:
        # Get property_id from query parameters
        property_id = request.query_params.get('property_id')
        if not property_id:
            return Response(
                {"error": "property_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            property_id = int(property_id)
        except (ValueError, TypeError):
            return Response(
                {"error": "property_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the property
        property_obj = get_object_or_404(Property, pk=property_id)
        
        # Check if it's a hotel or lodge
        property_type_name = property_obj.property_type.name.lower() if property_obj.property_type else ''
        if property_type_name not in ['hotel', 'lodge']:
            return Response(
                {
                    "error": "This endpoint is only available for hotel and lodge properties",
                    "property_type": property_type_name
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse optional date parameters
        check_in_date = None
        check_out_date = None
        
        check_in_str = request.query_params.get('check_in_date')
        check_out_str = request.query_params.get('check_out_date')
        
        if check_in_str:
            try:
                check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "check_in_date must be in YYYY-MM-DD format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if check_out_str:
            try:
                check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return Response(
                    {"error": "check_out_date must be in YYYY-MM-DD format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate date range if both dates provided
        if check_in_date and check_out_date:
            if check_out_date <= check_in_date:
                return Response(
                    {"error": "check_out_date must be after check_in_date"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get all active rooms for this property
        rooms = Room.objects.filter(
            property_obj=property_obj,
            is_active=True
        ).order_by('room_number')
        
        # Filter available rooms
        available_rooms_list = []
        
        for room in rooms:
            # Sync room status to ensure it's up-to-date with bookings
            # This fixes cases where current_booking points to cancelled bookings
            room.sync_status_from_bookings()
            
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
                    property_obj=property_obj,
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
        serializer = RoomSerializer(available_rooms_list, many=True, context={'request': request})
        
        return Response(
            {
                "property_id": property_obj.id,
                "property_title": property_obj.title,
                "property_type": property_type_name,
                "total_rooms": rooms.count(),
                "available_count": len(available_rooms_list),
                "check_in_date": check_in_str if check_in_str else None,
                "check_out_date": check_out_str if check_out_str else None,
                "rooms": serializer.data
            },
            status=status.HTTP_200_OK
        )
        
    except Property.DoesNotExist:
        return Response(
            {"error": "Property not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch available rooms: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Create Booking (Hotel, Lodge, or Venue)",
    description="""
    REST API endpoint for creating bookings.
    Designed for mobile apps - accepts JSON and JWT Bearer token authentication.
    
    Supports:
    - **Hotel/Lodge bookings** with room assignment (room_number required)
    - **Venue bookings** without rooms (event_name, event_type, event_date required)
    
    **Request Body (Hotel/Lodge):**
    - property_id (required): Property ID
    - property_type (required): "hotel" or "lodge"
    - room_number (required): Specific room number (e.g., "10")
    - room_type (required): Room type
    - check_in_date (required): Check-in date (YYYY-MM-DD)
    - check_out_date (required): Check-out date (YYYY-MM-DD)
    - number_of_guests (required): Number of guests
    - total_amount (required): Total booking amount
    - customer_name (required): Customer full name
    - email (required): Customer email
    - phone (required): Customer phone number
    - special_requests (optional): Special requests or notes
    
    **Request Body (Venue):**
    - property_id (required): Property ID
    - property_type (required): "venue"
    - event_name (required): Event name
    - event_type (required): Event type
    - event_date (required): Event date (YYYY-MM-DD) - used as check_in_date
    - check_out_date (optional): Check-out date (defaults to event_date)
    - expected_guests (required): Number of expected guests
    - total_amount (required): Total booking amount
    - customer_name (required): Customer full name
    - email (required): Customer email
    - phone (required): Customer phone number
    - special_requests (optional): Special requests or notes
    """,
    tags=['Properties'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'property_id': {'type': 'integer'},
                'property_type': {'type': 'string', 'enum': ['hotel', 'lodge', 'venue']},
                'room_number': {'type': 'string'},
                'room_type': {'type': 'string'},
                'check_in_date': {'type': 'string', 'format': 'date'},
                'check_out_date': {'type': 'string', 'format': 'date'},
                'number_of_guests': {'type': 'integer'},
                'expected_guests': {'type': 'integer'},
                'event_name': {'type': 'string'},
                'event_type': {'type': 'string'},
                'event_date': {'type': 'string', 'format': 'date'},
                'total_amount': {'type': 'string'},
                'customer_name': {'type': 'string'},
                'email': {'type': 'string', 'format': 'email'},
                'phone': {'type': 'string'},
                'special_requests': {'type': 'string'}
            }
        }
    },
    responses={
        201: {
            'description': 'Booking created successfully',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean'},
                            'booking_id': {'type': 'integer'},
                            'booking_reference': {'type': 'string'},
                            'room_number': {'type': 'string'},
                            'room_type': {'type': 'string'},
                            'message': {'type': 'string'},
                            'room_message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {'description': 'Bad request - validation error'},
        404: {'description': 'Property or room not found'},
        401: {'description': 'Authentication required'}
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="""
    Create a booking for hotel, lodge, or venue properties.
    
    This endpoint is designed for mobile apps and accepts JSON data with JWT authentication.
    
    **For Hotel/Lodge:** Room number is mandatory and will be validated for availability.
    **For Venue:** Event details are required (event_name, event_type, event_date).
    """,
    operation_summary="Create Booking (Hotel, Lodge, or Venue)",
    tags=['Properties'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'property_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Property ID'),
            'property_type': openapi.Schema(
                type=openapi.TYPE_STRING, 
                enum=['hotel', 'lodge', 'venue'],
                description='Property type: hotel, lodge, or venue'
            ),
            'room_number': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description='Specific room number (required for hotel/lodge, e.g., "10")'
            ),
            'room_type': openapi.Schema(type=openapi.TYPE_STRING, description='Room type (required for hotel/lodge)'),
            'check_in_date': openapi.Schema(
                type=openapi.TYPE_STRING, 
                format=openapi.FORMAT_DATE,
                description='Check-in date (YYYY-MM-DD) - required for hotel/lodge'
            ),
            'check_out_date': openapi.Schema(
                type=openapi.TYPE_STRING, 
                format=openapi.FORMAT_DATE,
                description='Check-out date (YYYY-MM-DD) - required for hotel/lodge'
            ),
            'number_of_guests': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of guests (required for hotel/lodge)'),
            'event_name': openapi.Schema(type=openapi.TYPE_STRING, description='Event name (required for venue)'),
            'event_type': openapi.Schema(type=openapi.TYPE_STRING, description='Event type (required for venue)'),
            'event_date': openapi.Schema(
                type=openapi.TYPE_STRING, 
                format=openapi.FORMAT_DATE,
                description='Event date (YYYY-MM-DD) - required for venue, used as check_in_date'
            ),
            'expected_guests': openapi.Schema(type=openapi.TYPE_INTEGER, description='Expected guests (required for venue)'),
            'total_amount': openapi.Schema(type=openapi.TYPE_STRING, description='Total booking amount (required)'),
            'customer_name': openapi.Schema(type=openapi.TYPE_STRING, description='Customer full name (required)'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Customer email (required)'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Customer phone number (required)'),
            'special_requests': openapi.Schema(type=openapi.TYPE_STRING, description='Special requests (optional)')
        }
    ),
    responses={
        201: openapi.Response(
            description="Booking created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'booking_reference': openapi.Schema(type=openapi.TYPE_STRING),
                    'room_number': openapi.Schema(type=openapi.TYPE_STRING),
                    'room_type': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'room_message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: "Bad request - validation error",
        404: "Property or room not found",
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_booking_with_room_api(request):
    """
    REST API endpoint for creating bookings.
    
    Designed for mobile apps - accepts JSON and JWT Bearer token authentication.
    Supports:
    - Hotel and lodge bookings with room assignment
    - Venue bookings without rooms
    """
    from datetime import datetime
    from decimal import Decimal
    import re
    
    try:
        # Get data from JSON request body
        data = request.data
        
        # Extract and validate required fields
        property_id = data.get('property_id')
        property_type = data.get('property_type', '').strip().lower()
        customer_name = data.get('customer_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        special_requests = data.get('special_requests', '').strip()
        total_amount = data.get('total_amount')
        
        # Validate property_type
        if property_type not in ['hotel', 'lodge', 'venue']:
            return Response(
                {
                    'success': False,
                    'error': 'property_type must be "hotel", "lodge", or "venue"'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle venue bookings differently
        if property_type == 'venue':
            # Venue-specific fields
            event_name = data.get('event_name', '').strip()
            event_type = data.get('event_type', '').strip()
            event_date = data.get('event_date', '').strip()
            check_out_date = data.get('check_out_date', '').strip() or event_date
            expected_guests = data.get('expected_guests') or data.get('number_of_guests')
            number_of_guests = expected_guests
            check_in_date = event_date  # For venues, event_date is check_in_date
            room_type = event_type  # Use event_type as room_type for venues
            room_number = None  # Venues don't have rooms
            
            # Validate required fields for venue
            if not all([event_name, event_type, event_date, expected_guests, customer_name, phone, email, total_amount]):
                return Response(
                    {
                        'success': False,
                        'error': 'Please provide all required fields: event_name, event_type, event_date, expected_guests, customer_name, phone, email, total_amount'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Hotel/Lodge fields
            room_number = data.get('room_number', '').strip()
            room_type = data.get('room_type', '').strip()
            check_in_date = data.get('check_in_date', '').strip()
            check_out_date = data.get('check_out_date', '').strip()
            number_of_guests = data.get('number_of_guests')
            
            # Validate required fields for hotel/lodge
            if not all([customer_name, phone, email, room_type, room_number, 
                       check_in_date, check_out_date, total_amount]):
                return Response(
                    {
                        'success': False,
                        'error': 'Please provide all required fields: customer_name, phone, email, room_type, room_number, check_in_date, check_out_date, total_amount'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate property_id
        if not property_id:
            return Response(
                {
                    'success': False,
                    'error': 'property_id is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            property_id = int(property_id)
        except (ValueError, TypeError):
            return Response(
                {
                    'success': False,
                    'error': 'property_id must be a valid integer'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate number_of_guests
        try:
            number_of_guests = int(number_of_guests) if number_of_guests else 1
            if number_of_guests < 1:
                raise ValueError("Number of guests must be at least 1")
        except (ValueError, TypeError):
            return Response(
                {
                    'success': False,
                    'error': 'number_of_guests must be a valid integer greater than 0'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate total_amount
        try:
            total_amount = float(total_amount) if total_amount else 0
            if total_amount <= 0:
                raise ValueError("Total amount must be greater than 0")
            total_amount_decimal = Decimal(str(total_amount))
        except (ValueError, TypeError):
            return Response(
                {
                    'success': False,
                    'error': 'total_amount must be a valid number greater than 0'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate date format
        try:
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d').date()
            
            if check_out <= check_in:
                return Response(
                    {
                        'success': False,
                        'error': 'check_out_date must be after check_in_date'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD format for check_in_date and check_out_date'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return Response(
                {
                    'success': False,
                    'error': 'Please provide a valid email address'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get and validate property
        try:
            selected_property = Property.objects.get(
                id=property_id,
                property_type__name__iexact=property_type
            )
        except Property.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'error': f'Property with ID {property_id} and type "{property_type}" not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check property availability
        if not selected_property.is_available_for_booking(check_in, check_out):
            return Response(
                {
                    'success': False,
                    'error': 'Property is not available for the selected dates. Please choose different dates.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse customer name
        name_parts = customer_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create or get customer
        try:
            customer, created = Customer.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': phone,
                }
            )
            
            # Update customer info if already exists
            if not created:
                updated = False
                if customer.first_name != first_name or customer.last_name != last_name:
                    customer.first_name = first_name
                    customer.last_name = last_name
                    updated = True
                if customer.phone != phone:
                    customer.phone = phone
                    updated = True
                if updated:
                    customer.save()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating/updating customer: {str(e)}")
            return Response(
                {
                    'success': False,
                    'error': f'Error saving customer information: {str(e)}. Please check that the email is unique.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # For venue bookings, validate capacity
        if property_type == 'venue':
            if selected_property.capacity and number_of_guests > selected_property.capacity:
                return Response(
                    {
                        'success': False,
                        'error': f'Expected guests ({number_of_guests}) exceeds venue capacity ({selected_property.capacity}).'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For venues, use event_name in special_requests
            if event_name:
                special_requests = f"{event_name}" + (f" - {special_requests}" if special_requests else "")
        
        # Generate booking reference based on property type
        if property_type == 'lodge':
            booking_reference = f"LDG-{Booking.objects.count() + 1:06d}"
        elif property_type == 'venue':
            booking_reference = f"VEN-{Booking.objects.count() + 1:06d}"
        else:
            booking_reference = f"HTL-{Booking.objects.count() + 1:06d}"
        
        # Create booking
        booking = Booking.objects.create(
            property_obj=selected_property,
            customer=customer,
            booking_reference=booking_reference,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_guests=number_of_guests,
            room_type=room_type,
            total_amount=total_amount_decimal,
            special_requests=special_requests,
            created_by=request.user,
        )
        
        # Handle room assignment - only for hotel/lodge, not venues
        room_assigned = False
        room_message = ""
        
        if property_type != 'venue':
            # Validate and assign the selected room
            try:
            room = Room.objects.get(
                property_obj=selected_property,
                room_number=room_number,
                room_type=room_type
            )
            
            # Check if room is available
            room.sync_status_from_bookings()
            
            if room.status != 'available':
                # Delete the booking if room is not available
                booking.delete()
                return Response(
                    {
                        'success': False,
                        'error': f'Room {room_number} is not available (Status: {room.status}). Please select an available room.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check for date conflicts
            conflicting_bookings = Booking.objects.filter(
                property_obj=selected_property,
                room_number=room_number,
                booking_status__in=['pending', 'confirmed', 'checked_in'],
                check_in_date__lt=check_out,
                check_out_date__gt=check_in
            ).exclude(id=booking.id).exists()
            
            if conflicting_bookings:
                booking.delete()
                return Response(
                    {
                        'success': False,
                        'error': f'Room {room_number} is already booked for the selected dates. Please choose different dates or another room.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Assign the room to booking
            booking.room_number = room_number
            booking.save()
            
            # Update room status
            room.current_booking = booking
            room.status = 'occupied'
            room.save()
            
                room_message = f"Room {room_number} assigned successfully"
                room_assigned = True
                
            except Room.DoesNotExist:
                # Delete the booking if room doesn't exist
                booking.delete()
                return Response(
                    {
                        'success': False,
                        'error': f'Room {room_number} not found. Please select a valid room.'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Return success response
        response_data = {
            'success': True,
            'booking_id': booking.id,
            'booking_reference': booking.booking_reference,
            'message': f'Booking {booking.booking_reference} created successfully!'
        }
        
        # Add room info for hotel/lodge bookings
        if property_type != 'venue':
            response_data['room_number'] = booking.room_number
            response_data['room_type'] = booking.room_type
            response_data['room_message'] = room_message
        else:
            # Add event info for venue bookings
            response_data['event_name'] = event_name
            response_data['event_type'] = event_type
            response_data['event_date'] = event_date
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating booking: {str(e)}", exc_info=True)
        return Response(
            {
                'success': False,
                'error': f'Error creating booking: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
