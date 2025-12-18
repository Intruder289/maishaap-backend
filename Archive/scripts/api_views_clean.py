from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from accounts.models import Profile, CustomRole, UserRole
from accounts.serializers import (
    TenantSignupSerializer, 
    TenantLoginSerializer,
    UserProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    AdminApprovalSerializer,
    PendingUserSerializer
)
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint - returns available endpoints
    """
    return Response({
        'message': 'Maisha Backend API v1 - Role-based Authentication for Flutter App',
        'endpoints': {
            'auth': {
                'signup': '/auth/signup/',
                'login': '/auth/login/',
                'logout': '/auth/logout/',
                'profile': '/auth/profile/',
                'refresh': '/auth/refresh/',
                'verify': '/auth/verify/'
            },
            'admin': {
                'pending_users': '/admin/pending-users/',
                'approve_user': '/admin/approve-user/'
            }
        },
        'authentication': 'JWT Bearer Token required for protected endpoints',
        'roles': ['tenant', 'owner'],
        'approval_required': True
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_test(request):
    """Simple test endpoint"""
    return Response({
        'message': 'API is working!',
        'timestamp': '2025-10-01'
    })


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def tenant_signup(request):
    """
    API endpoint for user registration (tenant or owner)
    
    POST /api/v1/auth/signup/
    {
        "username": "username",
        "email": "user@example.com",
        "password": "securepassword123",
        "confirm_password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+254712345678",
        "role": "tenant"  // or "owner"
    }
    """
    try:
        serializer = TenantSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Get user profile data (no tokens since approval is required)
            profile_serializer = UserProfileSerializer(user)
            
            role = request.data.get('role', 'tenant')
            logger.info(f"New {role} registered: {user.username} ({user.email}) - Pending approval")
            
            return Response({
                'success': True,
                'message': 'Account created successfully. Your account is pending admin approval. You will be able to login once approved.',
                'user': profile_serializer.data,
                'status': 'pending_approval'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during registration'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def tenant_login(request):
    """
    API endpoint for user login (tenant or owner)
    
    POST /api/v1/auth/login/
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    """
    try:
        serializer = TenantLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            tokens = get_tokens_for_user(user)
            
            # Get user profile data
            profile_serializer = UserProfileSerializer(user)
            
            role = user.profile.get_role_display() if hasattr(user, 'profile') else 'User'
            logger.info(f"{role} logged in: {user.username} ({user.email})")
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': profile_serializer.data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Login failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during login'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tenant_logout(request):
    """
    API endpoint for user logout
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during logout'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_profile(request):
    """
    API endpoint to get user profile
    """
    try:
        serializer = UserProfileSerializer(request.user)
        
        return Response({
            'success': True,
            'message': 'Profile retrieved successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while retrieving profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_tenant_profile(request):
    """
    API endpoint to update user profile
    """
    try:
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            user = serializer.save()
            profile_serializer = UserProfileSerializer(user)
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'user': profile_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Profile update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during profile update'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    API endpoint to change user password
    """
    try:
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Password change failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during password change'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    API endpoint to refresh JWT token
    """
    try:
        refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        
        return Response({
            'success': True,
            'message': 'Token refreshed successfully',
            'access': str(token.access_token)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Token refresh failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    API endpoint to verify JWT token
    """
    try:
        return Response({
            'success': True,
            'message': 'Token is valid',
            'user_id': request.user.id,
            'username': request.user.username
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Token verification failed'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_users(request):
    """
    API endpoint to get all pending users (admin only)
    
    GET /api/v1/admin/pending-users/
    """
    try:
        # Check if user is admin/superuser
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all pending users
        pending_profiles = Profile.objects.filter(is_approved=False).select_related('user').order_by('-user__date_joined')
        serializer = PendingUserSerializer(pending_profiles, many=True)
        
        return Response({
            'success': True,
            'message': 'Pending users retrieved successfully',
            'pending_users': serializer.data,
            'count': len(serializer.data)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Get pending users error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while retrieving pending users'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_user(request):
    """
    API endpoint for admin to approve/reject users
    
    POST /api/v1/admin/approve-user/
    {
        "user_id": 123,
        "action": "approve"  // or "reject"
    }
    """
    try:
        # Check if user is admin/superuser
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AdminApprovalSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            action = serializer.validated_data['action']
            
            user = User.objects.get(id=user_id)
            profile = user.profile
            
            if action == 'approve':
                profile.is_approved = True
                profile.approved_by = request.user
                from django.utils import timezone
                profile.approved_at = timezone.now()
                profile.save()
                
                logger.info(f"User approved: {user.username} ({user.email}) by {request.user.username}")
                
                return Response({
                    'success': True,
                    'message': f'User {user.username} has been approved successfully'
                }, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                # Delete the user and profile
                username = user.username
                email = user.email
                user.delete()  # This will cascade delete the profile
                
                logger.info(f"User rejected and deleted: {username} ({email}) by {request.user.username}")
                
                return Response({
                    'success': True,
                    'message': f'User {username} has been rejected and removed from the system'
                }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"User approval error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during user approval'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)