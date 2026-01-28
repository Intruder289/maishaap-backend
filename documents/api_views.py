from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from documents.models import Lease, Booking, Document
from documents.serializers import (
    LeaseSerializer, BookingSerializer, DocumentSerializer,
    LeaseCreateSerializer, BookingCreateSerializer
)
# Swagger documentation - using drf-spectacular
# Import extend_schema for explicit documentation
try:
    from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
    from drf_spectacular.types import OpenApiTypes
except ImportError:
    # Fallback if drf-spectacular is not available
    extend_schema = lambda *args, **kwargs: lambda func: func  # No-op decorator
    OpenApiParameter = None
    OpenApiTypes = None
    OpenApiResponse = None

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


class LeaseViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Lease management
    
    list: Get all leases (filtered by user role)
    retrieve: Get a specific lease
    create: Create a new lease
    update: Update a lease
    partial_update: Partially update a lease
    destroy: Delete a lease
    """
    queryset = Lease.objects.select_related('property_ref', 'tenant').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'property_ref', 'tenant']
    search_fields = ['property_ref__name', 'tenant__username', 'tenant__email']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return LeaseCreateSerializer
        return LeaseSerializer
    
    @extend_schema(
        summary="List Leases",
        description="""
        Get list of leases filtered by user role.
        
        **Permissions:**
        - **Admin/Staff**: See ALL leases (all properties, all owners)
        - **Property Owners**: See only leases for their own properties
        - **Tenants**: See only their own leases
        
        **Response includes:**
        - `payment_status`: Payment status field showing 'paid', 'partial', or 'unpaid' (similar to bookings API)
        - All lease details with nested property and tenant information
        
        Supports filtering by status, property_ref, tenant, search, and ordering.
        """,
        tags=['Leases'],
        parameters=[
            OpenApiParameter(
                'status',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by lease status (e.g., 'pending', 'active', 'terminated')",
                required=False
            ),
            OpenApiParameter(
                'property_ref',
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by property ID",
                required=False
            ),
            OpenApiParameter(
                'tenant',
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by tenant user ID",
                required=False
            ),
            OpenApiParameter(
                'search',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Search leases by property name, tenant username, or tenant email",
                required=False
            ),
            OpenApiParameter(
                'ordering',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Order results by field. Use '-' prefix for descending. Options: created_at, start_date, end_date (e.g., '-created_at' for newest first)",
                required=False
            ),
        ],
        responses={
            200: OpenApiResponse(response=LeaseSerializer, description='List of leases with payment_status field'),
            401: {'description': 'Authentication required'}
        }
    )
    @swagger_auto_schema(
        method='get',
        operation_description="""
        Get list of leases filtered by user role.
        
        **Permissions:**
        - Admin/Staff: See ALL leases (all properties, all owners)
        - Property Owners: See only leases for their own properties
        - Tenants: See only their own leases
        
        **Response includes:**
        - `payment_status`: Payment status field showing 'paid', 'partial', or 'unpaid' (similar to bookings API)
        - All lease details with nested property and tenant information
        
        Supports filtering by status, property_ref, tenant, search, and ordering.
        """,
        operation_summary="List Leases",
        tags=['Leases'],
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by lease status (e.g., 'pending', 'active', 'terminated')",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'property_ref',
                openapi.IN_QUERY,
                description="Filter by property ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'tenant',
                openapi.IN_QUERY,
                description="Filter by tenant user ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search leases by property name, tenant username, or tenant email",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order results by field. Use '-' prefix for descending. Options: created_at, start_date, end_date (e.g., '-created_at' for newest first)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of leases with payment_status field",
                schema=LeaseSerializer(many=True)
            ),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @extend_schema(
        summary="Retrieve Lease",
        description="""
        Get details of a specific lease.
        
        **Response includes:**
        - `id`: Lease ID
        - `payment_status`: Payment status field showing 'paid', 'partial', or 'unpaid'
        - All lease details with nested property and tenant information
        
        **Payment Status Calculation:**
        - Calculated from all payments (invoice-based + lease-only)
        - `paid`: Total paid >= total due
        - `partial`: Some payment made but not full
        - `unpaid`: No payments made
        """,
        tags=['Leases'],
        responses={
            200: OpenApiResponse(response=LeaseSerializer, description='Lease details with payment_status field'),
            404: {'description': 'Lease not found'},
            401: {'description': 'Authentication required'}
        }
    )
    @swagger_auto_schema(
        method='get',
        operation_description="""
        Get details of a specific lease.
        
        **Response includes:**
        - `payment_status`: Payment status field showing 'paid', 'partial', or 'unpaid'
        - All lease details with nested property and tenant information
        """,
        operation_summary="Retrieve Lease",
        tags=['Leases'],
        responses={
            200: LeaseSerializer,
            404: "Lease not found",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific lease.
        
        Returns lease details including payment_status field.
        """
        return super().retrieve(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        """
        List leases with filtering and search support.
        
        This method is overridden to add explicit Swagger documentation.
        The actual implementation is handled by the parent ViewSet.
        """
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        MULTI-TENANCY: Filter queryset based on user role for data isolation
        - Property owners see leases for their properties
        - Tenants see only their own leases
        - Admins/staff see all leases
        """
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
            
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        
        # Check if user is a property owner
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                # Property owners see leases for their properties
                return self.queryset.filter(property_ref__owner=user)
        except Profile.DoesNotExist:
            pass
        
        # Tenants see only their own leases
        return self.queryset.filter(tenant=user)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all leases for the current user (tenant). Returns only leases where the current user is the tenant.",
        operation_summary="Get My Leases",
        tags=['Leases'],
        responses={
            200: LeaseSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def my_leases(self, request):
        """Get current user's leases"""
        leases = self.queryset.filter(tenant=request.user)
        serializer = self.get_serializer(leases, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all active leases. Returns leases with status 'active' filtered by user role.",
        operation_summary="Get Active Leases",
        tags=['Leases'],
        responses={
            200: LeaseSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def active_leases(self, request):
        """Get all active leases"""
        leases = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(leases, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Create Lease",
        description="""
        Create a new lease agreement.
        
        **Important Notes:**
        - Non-staff users can only create leases for themselves (tenant is automatically set to current user)
        - Non-staff users' leases are automatically set to 'active' status
        - Staff/admin users can set custom tenant and status
        - **Response includes the lease ID** and all lease details including payment_status
        
        **Response includes:**
        - `id`: The generated lease ID (required for creating payments)
        - `payment_status`: Payment status ('paid', 'partial', or 'unpaid')
        - All other lease fields with nested property and tenant details
        """,
        tags=['Leases'],
        request=LeaseCreateSerializer,
        responses={
            201: OpenApiResponse(response=LeaseSerializer, description='Lease created successfully'),
            400: {'description': 'Validation error'},
            401: {'description': 'Authentication required'}
        }
    )
    @swagger_auto_schema(
        method='post',
        operation_description="""
        Create a new lease agreement.
        
        **Important Notes:**
        - Non-staff users can only create leases for themselves (tenant is automatically set to current user)
        - Non-staff users' leases are automatically set to 'active' status
        - Staff/admin users can set custom tenant and status
        - **Response includes the lease ID** and all lease details including payment_status
        
        **Response includes:**
        - `id`: The generated lease ID (required for creating payments)
        - `payment_status`: Payment status ('paid', 'partial', or 'unpaid')
        - All other lease fields with nested property and tenant details
        """,
        operation_summary="Create Lease",
        tags=['Leases'],
        request_body=LeaseCreateSerializer,
        responses={
            201: openapi.Response(
                description="Lease created successfully",
                schema=LeaseSerializer
            ),
            400: "Validation error",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def create(self, request, *args, **kwargs):
        """Override create to return full serializer with ID"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.request.user
        # Ensure non-staff users can only create leases for themselves
        if not (user.is_staff or user.is_superuser):
            # Force tenant to current user and auto-confirm
            lease = serializer.save(tenant=user, status='active')
        else:
            # Staff can set custom tenant and status
            tenant = serializer.validated_data.get('tenant', user)
            lease = serializer.save(tenant=tenant)
        
        # Return full serializer with ID and all fields
        response_serializer = LeaseSerializer(lease)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """
        Set tenant to current user and auto-confirm leases created via mobile app.
        Mobile app users (non-staff) get 'active' status automatically.
        Staff/admin can still set custom status.
        Note: This method is now only used internally by create() override.
        """
        user = self.request.user
        # Ensure non-staff users can only create leases for themselves
        if not (user.is_staff or user.is_superuser):
            # Force tenant to current user and auto-confirm
            serializer.save(tenant=user, status='active')
        else:
            # Staff can set custom tenant and status
            tenant = serializer.validated_data.get('tenant', user)
            serializer.save(tenant=tenant)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all pending lease requests. Admin/staff only.",
        operation_summary="Get Pending Leases",
        tags=['Leases'],
        responses={
            200: LeaseSerializer(many=True),
            403: "Permission denied (admin/staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def pending_leases(self, request):
        """Get all pending lease requests (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied. Only staff can view pending leases.'},
                status=status.HTTP_403_FORBIDDEN
            )
        leases = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(leases, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Approve a pending lease request. Changes lease status to 'active'. Admin/staff only.",
        operation_summary="Approve Lease",
        tags=['Leases'],
        responses={
            200: openapi.Response(
                description="Lease approved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'lease': LeaseSerializer
                    }
                )
            ),
            400: "Lease is not pending",
            403: "Permission denied (admin/staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending lease request (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied. Only staff can approve leases.'},
                status=status.HTTP_403_FORBIDDEN
            )
        lease = self.get_object()
        if lease.status != 'pending':
            return Response(
                {'error': f'Lease is not pending. Current status: {lease.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        lease.status = 'active'
        lease.save()
        serializer = self.get_serializer(lease)
        return Response({
            'message': 'Lease approved successfully',
            'lease': serializer.data
        })
    
    @swagger_auto_schema(
        method='post',
        operation_description="Reject a pending lease request. Changes lease status to 'rejected'. Admin/staff only.",
        operation_summary="Reject Lease",
        tags=['Leases'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Rejection reason (optional)')
            }
        ),
        responses={
            200: openapi.Response(
                description="Lease rejected",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'reason': openapi.Schema(type=openapi.TYPE_STRING),
                        'lease': LeaseSerializer
                    }
                )
            ),
            400: "Lease is not pending",
            403: "Permission denied (admin/staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending lease request (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied. Only staff can reject leases.'},
                status=status.HTTP_403_FORBIDDEN
            )
        lease = self.get_object()
        if lease.status != 'pending':
            return Response(
                {'error': f'Lease is not pending. Current status: {lease.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        rejection_reason = request.data.get('reason', 'No reason provided')
        lease.status = 'rejected'
        lease.save()
        serializer = self.get_serializer(lease)
        return Response({
            'message': 'Lease rejected',
            'reason': rejection_reason,
            'lease': serializer.data
        })
    
    @swagger_auto_schema(
        method='post',
        operation_description="Terminate a lease. Changes lease status to 'terminated'.",
        operation_summary="Terminate Lease",
        tags=['Leases'],
        responses={
            200: LeaseSerializer,
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a lease"""
        lease = self.get_object()
        lease.status = 'terminated'
        lease.save()
        serializer = self.get_serializer(lease)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Booking management
    
    list: Get all bookings (filtered by user role)
    retrieve: Get a specific booking
    create: Create a new booking
    update: Update a booking
    partial_update: Partially update a booking
    destroy: Delete a booking
    """
    queryset = Booking.objects.select_related('property_ref', 'tenant').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'property_ref', 'tenant']
    search_fields = ['property_ref__name', 'tenant__username', 'tenant__email']
    ordering_fields = ['created_at', 'check_in', 'check_out']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create', 'update', 'partial_update']:
            return BookingCreateSerializer
        return BookingSerializer
    
    def get_queryset(self):
        """
        MULTI-TENANCY: Filter queryset based on user role for data isolation
        - Property owners see bookings for their properties
        - Tenants see only their own bookings
        - Admins/staff see all bookings
        """
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
            
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return self.queryset
        
        # Check if user is a property owner
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                # Property owners see bookings for their properties
                return self.queryset.filter(property_ref__owner=user)
        except Profile.DoesNotExist:
            pass
        
        # Tenants see only their own bookings
        return self.queryset.filter(tenant=user)
    
    # CRITICAL: @extend_schema must be BEFORE the method for drf-spectacular
    @extend_schema(
        summary="List Bookings (House Properties)",
        description="""
        Get list of bookings for house properties.
        
        **Permissions:**
        - **Admin/Staff**: See ALL bookings (all properties, all owners)
        - **Property Owners**: See only bookings for their own properties
        - **Tenants**: See only their own bookings
        
        Returns bookings from documents.Booking model (for house/rental properties).
        Supports filtering by status, property_ref, tenant, search, and ordering.
        """,
        tags=['Bookings'],
        parameters=[
            OpenApiParameter(
                'status',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by booking status (e.g., 'pending', 'confirmed', 'cancelled')",
                required=False
            ),
            OpenApiParameter(
                'property_ref',
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by property ID",
                required=False
            ),
            OpenApiParameter(
                'tenant',
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by tenant user ID",
                required=False
            ),
            OpenApiParameter(
                'search',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Search bookings by property name, tenant username, or tenant email",
                required=False
            ),
            OpenApiParameter(
                'ordering',
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Order results by field. Use '-' prefix for descending. Options: created_at, check_in, check_out (e.g., '-created_at' for newest first)",
                required=False
            ),
        ],
        responses={
            200: OpenApiResponse(response=BookingSerializer, description='List of bookings for house properties'),
            401: {'description': 'Authentication required'}
        }
    )
    @swagger_auto_schema(
        method='get',
        operation_description="""
        Get list of bookings for house properties.
        
        **Permissions:**
        - Admin/Staff: See ALL bookings (all properties, all owners)
        - Property Owners: See only bookings for their own properties
        - Tenants: See only their own bookings
        
        Returns bookings from documents.Booking model (for house/rental properties).
        Supports filtering by status, property_ref, tenant, search, and ordering.
        """,
        operation_summary="List Bookings (House Properties)",
        tags=['Bookings'],
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by booking status (e.g., 'pending', 'confirmed', 'cancelled')",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'property_ref',
                openapi.IN_QUERY,
                description="Filter by property ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'tenant',
                openapi.IN_QUERY,
                description="Filter by tenant user ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search bookings by property name, tenant username, or tenant email",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order results by field. Use '-' prefix for descending. Options: created_at, check_in, check_out (e.g., '-created_at' for newest first)",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of bookings",
                schema=BookingSerializer(many=True)
            ),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    def list(self, request, *args, **kwargs):
        """
        List bookings with filtering and search support.
        
        This method is overridden to add explicit Swagger documentation.
        The actual implementation is handled by the parent ViewSet.
        """
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all bookings for the current user (tenant). Returns only bookings where the current user is the tenant.",
        operation_summary="Get My Bookings",
        tags=['Bookings'],
        responses={
            200: BookingSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get current user's bookings"""
        bookings = self.queryset.filter(tenant=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """
        Auto-confirm all bookings - bookings are automatically set to 'confirmed' status.
        All users (staff and non-staff) get 'confirmed' status automatically.
        """
        user = self.request.user
        
        # Get property and dates from validated data
        property_ref = serializer.validated_data.get('property_ref')
        check_in = serializer.validated_data.get('check_in')
        check_out = serializer.validated_data.get('check_out')
        
        # Check property availability before creating booking
        if property_ref and check_in and check_out:
            if not property_ref.is_available_for_booking(check_in, check_out):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'property_ref': 'Property is not available for the selected dates. Please choose different dates.'
                })
        
        # Ensure non-staff users can only create bookings for themselves
        if not (user.is_staff or user.is_superuser):
            # Force tenant to current user and auto-confirm
            serializer.save(tenant=user, status='confirmed')
        else:
            # Staff can set custom tenant, but booking is still auto-confirmed
            tenant = serializer.validated_data.get('tenant', user)
            serializer.save(tenant=tenant, status='confirmed')
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all pending bookings. Returns bookings with status 'pending' filtered by user role.",
        operation_summary="Get Pending Bookings",
        tags=['Bookings'],
        responses={
            200: BookingSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def pending_bookings(self, request):
        """Get all pending bookings"""
        bookings = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Confirm a booking. Changes booking status to 'confirmed'.",
        operation_summary="Confirm Booking",
        tags=['Bookings'],
        responses={
            200: BookingSerializer,
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking"""
        booking = self.get_object()
        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Cancel a booking. Changes booking status to 'cancelled'.",
        operation_summary="Cancel Booking",
        tags=['Bookings'],
        responses={
            200: BookingSerializer,
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        booking.status = 'cancelled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Document management
    
    list: Get all documents (filtered by user role)
    retrieve: Get a specific document
    create: Upload a new document
    update: Update a document
    partial_update: Partially update a document
    destroy: Delete a document
    """
    queryset = Document.objects.select_related('lease', 'booking', 'property_ref', 'user').all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lease', 'booking', 'property_ref', 'user']
    search_fields = ['file_name']
    ordering_fields = ['uploaded_at']
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
            
        user = self.request.user
        if user.is_staff:
            return self.queryset
        # Users see only their own documents and documents related to their leases/bookings
        return self.queryset.filter(
            models.Q(user=user) | 
            models.Q(lease__tenant=user) | 
            models.Q(booking__tenant=user)
        ).distinct()
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all documents uploaded by the current user.",
        operation_summary="Get My Documents",
        tags=['Documents'],
        responses={
            200: DocumentSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def my_documents(self, request):
        """Get current user's documents"""
        documents = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all documents associated with a specific lease. Requires 'lease_id' query parameter.",
        operation_summary="Get Lease Documents",
        tags=['Documents'],
        manual_parameters=[
            openapi.Parameter('lease_id', openapi.IN_QUERY, description="Lease ID", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: DocumentSerializer(many=True),
            400: "lease_id parameter is required",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def lease_documents(self, request):
        """Get documents for a specific lease"""
        lease_id = request.query_params.get('lease_id')
        if not lease_id:
            return Response(
                {'error': 'lease_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        documents = self.get_queryset().filter(lease_id=lease_id)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all documents associated with a specific booking. Requires 'booking_id' query parameter.",
        operation_summary="Get Booking Documents",
        tags=['Documents'],
        manual_parameters=[
            openapi.Parameter('booking_id', openapi.IN_QUERY, description="Booking ID", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: DocumentSerializer(many=True),
            400: "booking_id parameter is required",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def booking_documents(self, request):
        """Get documents for a specific booking"""
        booking_id = request.query_params.get('booking_id')
        if not booking_id:
            return Response(
                {'error': 'booking_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        documents = self.get_queryset().filter(booking_id=booking_id)
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
