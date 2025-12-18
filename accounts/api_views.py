from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
    authentication_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from accounts.models import Profile, CustomRole, UserRole, Notification
from accounts.serializers import (
    TenantSignupSerializer, 
    TenantLoginSerializer,
    UserProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    AdminApprovalSerializer,
    PendingUserSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)


# Custom throttle classes for specific endpoints
class AuthRateThrottle(UserRateThrottle):
    """Custom throttle for authentication endpoints"""
    rate = '10/minute'


class SearchRateThrottle(UserRateThrottle):
    """Custom throttle for search endpoints"""
    rate = '30/minute'


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
                'forgot_password': '/auth/forgot-password/',
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


@swagger_auto_schema(
    method='post',
    operation_description="Register a new user account as tenant or property owner. Account is automatically approved for immediate login.",
    operation_summary="User Signup (Tenant/Owner)",
    tags=['Authentication'],
    request_body=TenantSignupSerializer,
    responses={
        201: "Account created successfully - auto-approved",
        400: "Validation failed"
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([AuthRateThrottle])
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
    from django.db import transaction
    import traceback
    
    try:
        serializer = TenantSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            # Use transaction to ensure atomicity - rollback if anything fails
            try:
                with transaction.atomic():
                    user = serializer.save()
                    user_id = user.id  # Store ID for cleanup if needed
                    
                    # Verify role assignment for property owners
                    role = request.data.get('role', 'tenant')
                    if role == 'owner':
                        # Ensure Property Owner role is assigned
                        from accounts.models import CustomRole, UserRole
                        try:
                            property_owner_role = CustomRole.objects.get(name='Property Owner')
                            user_role_exists = UserRole.objects.filter(user=user, role=property_owner_role).exists()
                            if not user_role_exists:
                                # Assign the role if it wasn't assigned during signup
                                UserRole.objects.get_or_create(user=user, role=property_owner_role)
                                logger.info(f"Property Owner role assigned to {user.username} during signup verification")
                            
                            # Verify profile role is set correctly
                            if hasattr(user, 'profile') and user.profile.role != 'owner':
                                user.profile.role = 'owner'
                                user.profile.save()
                                logger.info(f"Profile role updated to 'owner' for {user.username}")
                        except CustomRole.DoesNotExist:
                            # Create Property Owner role if it doesn't exist
                            property_owner_role = CustomRole.objects.create(
                                name='Property Owner',
                                description='Property owner with mobile app access'
                            )
                            UserRole.objects.get_or_create(user=user, role=property_owner_role)
                            logger.warning(f"Property Owner role was missing and has been created for {user.username}")
                    
                    # Generate JWT tokens for immediate login (mobile app registrations are auto-approved)
                    tokens = get_tokens_for_user(user)
                    
                    # Refresh user to get latest profile data
                    user.refresh_from_db()
                    if hasattr(user, 'profile'):
                        user.profile.refresh_from_db()
                    
                    # Get user profile data
                    profile_serializer = UserProfileSerializer(user)
                    
                    # All mobile app registrations are auto-approved
                    is_approved = user.profile.is_approved if hasattr(user, 'profile') else True
                    
                    logger.info(f"New {role} registered via mobile app: {user.username} ({user.email}) - Auto-approved, Profile role: {user.profile.role if hasattr(user, 'profile') else 'N/A'}")
                    
                    return Response({
                        'success': True,
                        'message': 'Account created successfully. You can now login immediately.',
                        'user': profile_serializer.data,
                        'tokens': tokens,  # Return tokens for immediate authentication
                        'status': 'approved'
                    }, status=status.HTTP_201_CREATED)
            except IntegrityError as ie:
                # Handle database constraint violations (e.g., duplicate username, email, phone)
                error_trace = traceback.format_exc()
                logger.error(f"Database integrity error during signup: {str(ie)}\n{error_trace}")
                
                # Extract which field caused the violation
                error_msg = str(ie)
                if 'username' in error_msg.lower() or 'unique constraint' in error_msg.lower() and 'username' in error_msg:
                    field_error = 'username'
                elif 'email' in error_msg.lower() or 'unique constraint' in error_msg.lower() and 'email' in error_msg:
                    field_error = 'email'
                elif 'phone' in error_msg.lower() or 'unique constraint' in error_msg.lower() and 'phone' in error_msg:
                    field_error = 'phone'
                else:
                    field_error = 'unknown'
                
                return Response({
                    'success': False,
                    'message': f'Registration failed: {field_error.capitalize()} already exists',
                    'error_detail': f'Database constraint violation: {str(ie)}',
                    'field': field_error
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        error_trace = traceback.format_exc()
        logger.error(f"Signup error: {str(e)}\n{error_trace}")
        
        # Return detailed error for debugging (you can remove 'error_detail' in production)
        error_response = {
            'success': False,
            'message': 'An error occurred during registration',
            'error_detail': str(e)  # Include actual error for debugging
        }
        
        # In production, you might want to hide the error_detail
        # For now, we'll include it to help debug the issue
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Login with email+password or phone+password. Works for all registered mobile app users.",
    operation_summary="User Login (Tenant/Owner) via email or phone",
    tags=['Authentication'],
    request_body=TenantLoginSerializer,
    responses={
        200: "Login successful - returns user data and JWT tokens",
        400: "Login failed - invalid credentials"
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([AuthRateThrottle])
def tenant_login(request):
    """
    API endpoint for user login (tenant or owner) using email or phone number
    
    POST /api/v1/auth/login/
    Payload examples:
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }
        {
            "phone": "+255700000000",
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


@swagger_auto_schema(
    method='post',
    operation_description="Request password reset. Sends a notification to administrators who will reset your password to the default (DefaultPass@12).",
    operation_summary="Forgot Password Request",
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='User email address')
        }
    ),
    responses={
        200: "Password reset request submitted successfully",
        400: "Validation failed - email required"
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def forgot_password(request):
    """
    API endpoint for password reset request (mobile app)
    
    POST /api/v1/auth/forgot-password/
    {
        "email": "user@example.com"
    }
    
    Response:
    {
        "success": true,
        "message": "Your password reset request has been sent to the administrator. You will be notified once your password is reset."
    }
    """
    try:
        email = request.data.get('email', '').strip()
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email__iexact=email)
            
            # Create notification for admins
            Notification.objects.create(
                notification_type='password_reset',
                title=f'Password Reset Request from {user.get_full_name() or user.username}',
                message=f'User {user.get_full_name() or user.username} ({user.email}) has requested a password reset via mobile app. Please reset their password to the default: DefaultPass@12',
                related_user=user,
                metadata={
                    'email': user.email,
                    'username': user.username,
                    'user_id': user.id,
                    'request_source': 'mobile_app'
                }
            )
            
            logger.info(f"Password reset request from mobile app: {user.email}")
            
            return Response({
                'success': True,
                'message': 'Your password reset request has been sent to the administrator. You will be notified once your password is reset.'
            }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            return Response({
                'success': True,
                'message': 'If an account exists with this email, a password reset request has been sent to the administrator.'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error creating password reset request: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
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


@swagger_auto_schema(
    method='put',
    operation_description="Update user profile information. All fields are optional - only provided fields will be updated.",
    operation_summary="Update User Profile",
    tags=['Profile'],
    request_body=ProfileUpdateSerializer,
    responses={
        200: openapi.Response(
            description="Profile updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        400: openapi.Response(
            description="Validation failed",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        401: "Authentication required",
        500: "Internal server error"
    },
    security=[{'Bearer': []}]
)
@csrf_exempt
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


@swagger_auto_schema(
    method='post',
    operation_description="Change user password. Requires current password, new password, and password confirmation.",
    operation_summary="Change User Password",
    tags=['Authentication'],
    request_body=ChangePasswordSerializer,
    responses={
        200: openapi.Response(
            description="Password changed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: openapi.Response(
            description="Validation failed",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'errors': openapi.Schema(type=openapi.TYPE_OBJECT)
                }
            )
        ),
        401: "Authentication required",
        500: "Internal server error"
    },
    security=[{'Bearer': []}]
)
@csrf_exempt
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


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@throttle_classes([AuthRateThrottle])
def refresh_token(request):
    """
    API endpoint to refresh JWT token
    
    With ROTATE_REFRESH_TOKENS enabled, this will:
    - Blacklist the old refresh token
    - Issue a new access token
    - Issue a new refresh token (client must update both)
    """
    try:
        refresh_token_str = request.data.get('refresh')
        
        if not refresh_token_str:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create RefreshToken object - this validates the token
        refresh = RefreshToken(refresh_token_str)
        
        # Get user ID from the token payload
        user_id = refresh.payload.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'Invalid token: user ID not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user object
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Blacklist the old refresh token (required for security)
        refresh.blacklist()
        
        # Generate new tokens
        new_tokens = get_tokens_for_user(user)
        
        return Response({
            'success': True,
            'message': 'Token refreshed successfully',
            'access': new_tokens['access'],
            'refresh': new_tokens['refresh']  # Return new refresh token for rotation
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Token refresh failed. Token may be expired or invalid.'
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AuthRateThrottle])
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


@swagger_auto_schema(
    method='get',
    operation_description="Get all users waiting for admin approval. Admin access required.",
    operation_summary="Get Pending Users",
    tags=['Admin'],
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer <admin_access_token>",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: "List of pending users retrieved successfully",
        403: "Admin access required"
    }
)
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


@csrf_exempt
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


# ==================== MULTI-TENANCY: Admin Owner Management Endpoints ====================

@swagger_auto_schema(
    method='post',
    operation_description="Admin/Manager endpoint to register/create a new property owner account. Admin or Manager access required.",
    operation_summary="Register New Owner (Admin/Manager)",
    tags=['Admin', 'Multi-Tenancy'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'password', 'first_name', 'last_name'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username for the owner'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password (min 8 characters)'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number (optional)'),
        }
    ),
    responses={
        201: "Owner account created successfully",
        400: "Validation failed",
        403: "Admin or Manager access required"
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_register_owner(request):
    """
    MULTI-TENANCY: Admin/Manager endpoint to register/create a new property owner account
    
    POST /api/v1/admin/register-owner/
    {
        "username": "hotel_owner_1",
        "email": "owner1@example.com",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+255123456789"
    }
    """
    try:
        # Check if user is admin/superuser/staff OR has Manager role
        is_admin_or_staff = request.user.is_superuser or request.user.is_staff
        
        # Check for Manager role
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user) if not is_admin_or_staff else False
        
        if not (is_admin_or_staff or is_manager_user):
            return Response({
                'success': False,
                'message': 'Admin or Manager access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure role is set to 'owner' in request data for serializer
        # This ensures the serializer creates the user with owner role from the start
        request_data = request.data.copy()
        request_data['role'] = 'owner'  # Force owner role for this endpoint
        
        # Use the signup serializer but auto-approve
        serializer = TenantSignupSerializer(data=request_data)
        
        if serializer.is_valid():
            # Create user with owner role (serializer will handle role assignment)
            user = serializer.save()
            
            # Auto-approve and activate the owner account
            profile = user.profile
            profile.is_approved = True
            profile.role = 'owner'  # Ensure profile role is set
            profile.approved_by = request.user
            from django.utils import timezone
            profile.approved_at = timezone.now()
            profile.is_deactivated = False  # Ensure they're active
            profile.save()
            
            # Verify and ensure they have Property Owner CustomRole
            role_name = 'Property Owner'
            try:
                custom_role = CustomRole.objects.get(name=role_name)
            except CustomRole.DoesNotExist:
                custom_role = CustomRole.objects.create(
                    name=role_name,
                    description='Property owner with system access'
                )
                logger.warning(f"Property Owner role was missing and has been created during owner registration")
            
            # Assign role if not already assigned, and track who assigned it
            user_role, created = UserRole.objects.get_or_create(
                user=user, 
                role=custom_role,
                defaults={'assigned_by': request.user}
            )
            
            # Verify role assignment was successful
            if not UserRole.objects.filter(user=user, role=custom_role).exists():
                logger.error(f"Failed to assign Property Owner role to {user.username} during admin registration")
                # Try to assign again
                UserRole.objects.create(user=user, role=custom_role, assigned_by=request.user)
            
            # Refresh user and profile to get latest data
            user.refresh_from_db()
            profile.refresh_from_db()
            
            profile_serializer = UserProfileSerializer(user)
            
            # Log who registered the owner (admin or manager)
            registered_by = "admin" if is_admin_or_staff else "manager"
            role_assigned = UserRole.objects.filter(user=user, role=custom_role).exists()
            logger.info(f"Owner registered by {registered_by}: {user.username} ({user.email}) - Profile role: {profile.role}, Property Owner role assigned: {role_assigned}")
            
            return Response({
                'success': True,
                'message': f'Owner account created and activated successfully for {user.username}',
                'user': profile_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Owner registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except IntegrityError as ie:
        # Handle database constraint violations (e.g., duplicate username, email, phone)
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Database integrity error during owner registration: {str(ie)}\n{error_trace}")
        
        # Extract which field caused the violation
        error_msg = str(ie)
        if 'username' in error_msg.lower() or 'unique constraint' in error_msg.lower() and 'username' in error_msg:
            field_error = 'username'
        elif 'email' in error_msg.lower() or 'unique constraint' in error_msg.lower() and 'email' in error_msg:
            field_error = 'email'
        elif 'phone' in error_msg.lower() or 'unique constraint' in error_msg.lower() and 'phone' in error_msg:
            field_error = 'phone'
        else:
            field_error = 'unknown'
        
        return Response({
            'success': False,
            'message': f'Owner registration failed: {field_error.capitalize()} already exists',
            'error_detail': f'Database constraint violation: {str(ie)}',
            'field': field_error
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Owner registration error: {str(e)}\n{error_trace}")
        
        # Return detailed error for debugging
        error_response = {
            'success': False,
            'message': 'An error occurred during owner registration',
            'error_detail': str(e)  # Include actual error for debugging
        }
        
        return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Get all property owners. Admin sees all owners, Manager sees only owners they registered.",
    operation_summary="List All Owners (Admin/Manager)",
    tags=['Admin', 'Multi-Tenancy'],
    responses={
        200: "List of owners retrieved successfully",
        403: "Admin or Manager access required"
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_owners(request):
    """
    MULTI-TENANCY: Admin/Manager endpoint to get property owners
    - Admin: sees all owners
    - Manager: sees only owners they registered (via UserRole.assigned_by or Profile.approved_by)
    
    GET /api/v1/admin/list-owners/
    """
    try:
        # Check if user is admin/superuser/staff OR has Manager role
        is_admin_or_staff = request.user.is_superuser or request.user.is_staff
        
        # Check for Manager role
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user) if not is_admin_or_staff else False
        
        if not (is_admin_or_staff or is_manager_user):
            return Response({
                'success': False,
                'message': 'Admin or Manager access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get owners - filter by who registered them if Manager
        if is_manager_user and not is_admin_or_staff:
            # Manager: only see owners they registered
            from accounts.models import UserRole
            from django.db.models import Q
            
            # Get owners where Manager assigned the role OR approved the profile
            owner_user_ids = UserRole.objects.filter(
                role__name='Property Owner',
                assigned_by=request.user
            ).values_list('user_id', flat=True)
            
            owner_profiles = Profile.objects.filter(
                Q(role='owner') & (
                    Q(user_id__in=owner_user_ids) |
                    Q(approved_by=request.user)
                )
            ).select_related('user', 'approved_by', 'deactivated_by').order_by('-user__date_joined')
        else:
            # Admin/Staff: see all owners
            owner_profiles = Profile.objects.filter(
                role='owner'
            ).select_related('user', 'approved_by', 'deactivated_by').order_by('-user__date_joined')
        
        owners_data = []
        for profile in owner_profiles:
            owners_data.append({
                'id': profile.user.id,
                'username': profile.user.username,
                'email': profile.user.email,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'phone': profile.phone,
                'is_approved': profile.is_approved,
                'is_deactivated': profile.is_deactivated,
                'deactivation_reason': profile.deactivation_reason,
                'deactivated_at': profile.deactivated_at,
                'approved_at': profile.approved_at,
                'date_joined': profile.user.date_joined,
                # Count properties owned
                'properties_count': profile.user.owned_properties.count(),
            })
        
        return Response({
            'success': True,
            'message': 'Owners retrieved successfully',
            'owners': owners_data,
            'count': len(owners_data)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"List owners error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while retrieving owners'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Admin endpoint to activate or deactivate a property owner. Admin access required.",
    operation_summary="Activate/Deactivate Owner (Admin Only)",
    tags=['Admin', 'Multi-Tenancy'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['user_id', 'action'],
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Owner user ID'),
            'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['activate', 'deactivate'], description='Action to perform'),
            'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason for deactivation (required if action is deactivate)'),
        }
    ),
    responses={
        200: "Owner status updated successfully",
        400: "Invalid data",
        403: "Admin access required",
        404: "Owner not found"
    }
)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_activate_deactivate_owner(request):
    """
    MULTI-TENANCY: Admin endpoint to activate or deactivate a property owner
    
    POST /api/v1/admin/activate-deactivate-owner/
    {
        "user_id": 123,
        "action": "deactivate",  // or "activate"
        "reason": "Contract issues or some disagreement"  // required for deactivate
    }
    """
    try:
        # Check if user is admin/superuser
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({
                'success': False,
                'message': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        action = request.data.get('action')
        reason = request.data.get('reason', '')
        
        if not user_id or not action:
            return Response({
                'success': False,
                'message': 'user_id and action are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action not in ['activate', 'deactivate']:
            return Response({
                'success': False,
                'message': 'action must be either "activate" or "deactivate"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            
            # Verify this is an owner
            if profile.role != 'owner':
                return Response({
                    'success': False,
                    'message': 'User is not a property owner'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from django.utils import timezone
            
            if action == 'deactivate':
                if not reason:
                    return Response({
                        'success': False,
                        'message': 'reason is required when deactivating an owner'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                profile.is_deactivated = True
                profile.deactivation_reason = reason
                profile.deactivated_at = timezone.now()
                profile.deactivated_by = request.user
                profile.save()
                
                logger.info(f"Owner deactivated: {user.username} ({user.email}) by {request.user.username}. Reason: {reason}")
                
                return Response({
                    'success': True,
                    'message': f'Owner {user.username} has been deactivated successfully',
                    'owner': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_deactivated': True,
                        'deactivation_reason': reason
                    }
                }, status=status.HTTP_200_OK)
            
            elif action == 'activate':
                profile.is_deactivated = False
                profile.deactivation_reason = None
                profile.deactivated_at = None
                profile.deactivated_by = None
                profile.save()
                
                logger.info(f"Owner activated: {user.username} ({user.email}) by {request.user.username}")
                
                return Response({
                    'success': True,
                    'message': f'Owner {user.username} has been activated successfully',
                    'owner': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_deactivated': False
                    }
                }, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Owner not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Owner profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        logger.error(f"Activate/deactivate owner error: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred during owner activation/deactivation'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)