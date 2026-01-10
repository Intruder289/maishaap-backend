from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from complaints.models import Complaint, ComplaintResponse, Feedback
from complaints.serializers import (
    ComplaintSerializer, ComplaintCreateUpdateSerializer, ComplaintStatusUpdateSerializer,
    ComplaintResponseSerializer, FeedbackSerializer, FeedbackCreateSerializer
)


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for staff
        if request.user.is_staff:
            return True
        
        # Write permissions are only allowed to the owner of the complaint/feedback
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class ComplaintViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Complaint management
    
    list: Get all complaints (filtered by user role)
    retrieve: Get a specific complaint
    create: Create a new complaint
    update: Update a complaint (limited fields for users)
    partial_update: Partially update a complaint
    destroy: Delete a complaint (owner or staff only)
    """
    queryset = Complaint.objects.select_related(
        'user', 'property', 'resolved_by'
    ).prefetch_related('responses').all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'priority', 'property']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create']:
            return ComplaintCreateUpdateSerializer
        elif self.action in ['update_status']:
            return ComplaintStatusUpdateSerializer
        elif self.action in ['update', 'partial_update']:
            # Only allow limited updates for non-staff users
            if not self.request.user.is_staff:
                return ComplaintCreateUpdateSerializer
            return ComplaintSerializer
        return ComplaintSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        
        user = self.request.user
        queryset = self.queryset
        
        if user.is_staff:
            # Staff can see all complaints
            return queryset
        else:
            # Regular users can only see their own complaints
            return queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """Set user when creating complaint"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Handle updates with proper permissions"""
        if not self.request.user.is_staff:
            # Non-staff users can only update limited fields
            allowed_fields = ['title', 'description', 'category', 'priority', 'rating']
            for field in list(serializer.validated_data.keys()):
                if field not in allowed_fields:
                    serializer.validated_data.pop(field)
        serializer.save()
    
    @swagger_auto_schema(
        method='post',
        operation_description="Add a response to a complaint. Staff only. Creates a ComplaintResponse record.",
        operation_summary="Add Complaint Response",
        tags=['Complaints'],
        request_body=ComplaintResponseSerializer,
        responses={
            201: ComplaintResponseSerializer,
            400: "Validation error",
            403: "Permission denied (staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_response(self, request, pk=None):
        """Add a response to a complaint"""
        complaint = self.get_object()
        
        # Only staff can add responses
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can add responses'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ComplaintResponseSerializer(
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(complaint=complaint)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        method='patch',
        operation_description="Update complaint status. Staff only. Allows updating status, resolved_by, and resolution_notes.",
        operation_summary="Update Complaint Status",
        tags=['Complaints'],
        request_body=ComplaintStatusUpdateSerializer,
        responses={
            200: ComplaintSerializer,
            400: "Validation error",
            403: "Permission denied (staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        """Update complaint status (staff only)"""
        complaint = self.get_object()
        
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can update status'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ComplaintStatusUpdateSerializer(
            complaint, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(ComplaintSerializer(complaint).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all complaints for the current user. Returns only complaints created by the current user.",
        operation_summary="Get My Complaints",
        tags=['Complaints'],
        responses={
            200: ComplaintSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def my_complaints(self, request):
        """Get current user's complaints"""
        complaints = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(complaints)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get complaint statistics including counts by status, category, and priority. Staff only.",
        operation_summary="Get Complaint Statistics",
        tags=['Complaints'],
        responses={
            200: openapi.Response(
                description="Complaint statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_complaints': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'pending': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'in_progress': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'resolved': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'closed': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'by_category': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'by_priority': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            403: "Permission denied (staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get complaint statistics (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can view statistics'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        stats = {
            'total_complaints': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'closed': queryset.filter(status='closed').count(),
            'by_category': {},
            'by_priority': {},
        }
        
        # Category breakdown
        for category_code, category_name in Complaint.CATEGORY_CHOICES:
            stats['by_category'][category_name] = queryset.filter(category=category_code).count()
        
        # Priority breakdown
        for priority_code, priority_name in Complaint.PRIORITY_CHOICES:
            stats['by_priority'][priority_name] = queryset.filter(priority=priority_code).count()
        
        return Response(stats)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Feedback management
    
    list: Get all feedback (staff) or user's feedback
    retrieve: Get specific feedback
    create: Create new feedback
    update: Update feedback (owner only)
    destroy: Delete feedback (owner or staff)
    """
    queryset = Feedback.objects.select_related('user', 'property').all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['feedback_type', 'rating', 'property']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action in ['create']:
            return FeedbackCreateSerializer
        return FeedbackSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        
        user = self.request.user
        queryset = self.queryset
        
        if user.is_staff:
            # Staff can see all feedback
            return queryset
        else:
            # Regular users can only see their own feedback
            return queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """Set user when creating feedback"""
        serializer.save(user=self.request.user)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all feedback submitted by the current user. Returns only feedback created by the current user.",
        operation_summary="Get My Feedback",
        tags=['Feedback'],
        responses={
            200: FeedbackSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def my_feedback(self, request):
        """Get current user's feedback"""
        feedback = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(feedback)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(feedback, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get feedback statistics including average rating, counts by type and rating. Staff only.",
        operation_summary="Get Feedback Statistics",
        tags=['Feedback'],
        responses={
            200: openapi.Response(
                description="Feedback statistics",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_feedback': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'average_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'by_type': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'by_rating': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            403: "Permission denied (staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get feedback statistics (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can view statistics'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        stats = {
            'total_feedback': queryset.count(),
            'average_rating': queryset.filter(rating__isnull=False).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'by_type': {},
            'by_rating': {},
        }
        
        # Type breakdown
        for type_code, type_name in Feedback.FEEDBACK_TYPE_CHOICES:
            stats['by_type'][type_name] = queryset.filter(feedback_type=type_code).count()
        
        # Rating breakdown
        for rating in range(1, 6):
            stats['by_rating'][f'{rating}_star'] = queryset.filter(rating=rating).count()
        
        return Response(stats)


class ComplaintResponseViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Complaint Response management
    
    list: Get all complaint responses (filtered by user permissions)
    retrieve: Get a specific complaint response
    create: Create a new complaint response (staff only)
    update: Update a complaint response (staff only)
    partial_update: Partially update a complaint response (staff only)
    destroy: Delete a complaint response (staff only)
    
    Note: Only staff can create responses. Regular users can only view responses to their own complaints.
    """
    queryset = ComplaintResponse.objects.select_related('complaint', 'responder').all()
    serializer_class = ComplaintResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['complaint', 'response_type', 'is_visible_to_user']
    ordering = ['created_at']
    
    def get_queryset(self):
        """Filter based on user permissions"""
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        
        user = self.request.user
        queryset = self.queryset
        
        if user.is_staff:
            return queryset
        else:
            # Regular users can only see responses to their own complaints
            # and only visible responses
            return queryset.filter(
                complaint__user=user,
                is_visible_to_user=True
            )
    
    def perform_create(self, serializer):
        """Only staff can create responses"""
        if not self.request.user.is_staff:
            raise permissions.PermissionDenied("Only staff members can create responses")
        serializer.save(responder=self.request.user)