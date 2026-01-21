from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from accounts.models import Notification
import json
import os

@login_required
@require_http_methods(["GET"])
def user_search_api(request):
    """AJAX API for searching users"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 5))
    
    # Check if user is Manager - Managers can only see users they created
    from accounts.views import is_manager
    is_manager_user = is_manager(request.user)
    
    # Start with all users or filtered by creator for Managers
    if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
        # Managers can only see users they created
        users = User.objects.filter(
            Q(user_roles__assigned_by=request.user) |
            Q(profile__approved_by=request.user)
        ).distinct().select_related('profile').prefetch_related('user_roles__role')
    else:
        # Admin/Staff: see all users
        users = User.objects.select_related('profile').prefetch_related('user_roles__role').all()
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'approved':
        users = users.filter(profile__is_approved=True)
    elif status_filter == 'pending':
        users = users.filter(profile__is_approved=False)
    
    # Apply role filter
    if role_filter:
        if role_filter == 'tenant':
            users = users.filter(profile__role='tenant')
        elif role_filter == 'owner':
            users = users.filter(profile__role='owner')
        elif role_filter == 'admin':
            users = users.filter(is_superuser=True)
        elif role_filter == 'staff':
            users = users.filter(is_staff=True)
    
    # Order by date joined (newest first)
    users = users.order_by('-date_joined')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, per_page)
    page_obj = paginator.get_page(page)
    
    # Convert users to JSON format
    users_data = []
    for user in page_obj:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name(),
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined.strftime('%b %d, %Y'),
            'profile': None
        }
        
        if user.profile:
            user_data['profile'] = {
                'role': user.profile.role,
                'phone': user.profile.phone,
                'is_approved': user.profile.is_approved,
                'image': user.profile.image.url if user.profile.image else None
            }
        
        users_data.append(user_data)
    
    return JsonResponse({
        'users': users_data,
        'total_count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def user_toggle_status_api(request, user_id):
    """AJAX API for toggling user status - Managers can only toggle their created users"""
    try:
        from accounts.models import UserRole
        from accounts.views import is_manager
        
        # Check if user is Manager - Managers can only toggle status of users they created
        is_manager_user = is_manager(request.user)
        
        user = User.objects.get(id=user_id)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            # Check if this user was created by the Manager
            user_created_by_manager = (
                UserRole.objects.filter(user=user, assigned_by=request.user).exists() or
                (hasattr(user, 'profile') and user.profile.approved_by == request.user)
            )
            
            if not user_created_by_manager:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only toggle status of users you created.'
                }, status=403)
        
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'new_status': {
                'class': 'bg-success-subtle text-success' if user.is_active else 'bg-danger-subtle text-danger',
                'text': 'Active' if user.is_active else 'Inactive'
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def user_reset_password_api(request, user_id):
    """AJAX API for resetting user password to default - Managers can only reset for their created users"""
    try:
        from accounts.models import UserRole
        
        DEFAULT_PASSWORD = 'DefaultPass@12'
        
        # Check if user is Manager - Managers can only reset passwords for users they created
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user)
        
        user = User.objects.get(id=user_id)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            # Check if this user was created by the Manager
            user_created_by_manager = (
                UserRole.objects.filter(user=user, assigned_by=request.user).exists() or
                (hasattr(user, 'profile') and user.profile.approved_by == request.user)
            )
            
            if not user_created_by_manager:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only reset passwords for users you created.'
                }, status=403)
        
        # Reset password to default
        user.set_password(DEFAULT_PASSWORD)
        user.save()
        
        # Create notification that password was reset (mark as read since admin just did it)
        from django.utils import timezone
        Notification.objects.create(
            notification_type='password_reset',
            title=f'Password Reset Completed for {user.get_full_name() or user.username}',
            message=f'Password has been reset to default for {user.get_full_name() or user.username} ({user.email}) by {request.user.get_full_name() or request.user.username}.',
            related_user=user,
            is_read=True,  # Mark as read since admin just did it
            read_at=timezone.now(),
            read_by=request.user,
            metadata={
                'email': user.email,
                'username': user.username,
                'user_id': user.id,
                'reset_by': request.user.id
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Password has been reset to default for {user.get_full_name()}. New password: {DEFAULT_PASSWORD}',
            'default_password': DEFAULT_PASSWORD
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def user_toggle_approval_api(request, user_id):
    """AJAX API for toggling user approval status - Managers can only approve their created users"""
    try:
        from accounts.models import Profile, UserRole
        from django.utils import timezone
        
        # Check if user is Manager - Managers can only approve users they created
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user)
        
        user = User.objects.get(id=user_id)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            # Check if this user was created by the Manager
            user_created_by_manager = (
                UserRole.objects.filter(user=user, assigned_by=request.user).exists() or
                (hasattr(user, 'profile') and user.profile.approved_by == request.user)
            )
            
            if not user_created_by_manager:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only approve users you created.'
                }, status=403)
        
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Toggle approval status
        profile.is_approved = not profile.is_approved
        
        if profile.is_approved:
            # Set approval metadata
            profile.approved_by = request.user
            profile.approved_at = timezone.now()
        else:
            # Clear approval metadata
            profile.approved_by = None
            profile.approved_at = None
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'is_approved': profile.is_approved,
            'new_status': {
                'class': 'bg-success' if profile.is_approved else 'bg-warning text-dark',
                'text': 'Approved' if profile.is_approved else 'Pending',
                'icon': 'fa-check' if profile.is_approved else 'fa-clock'
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def user_delete_api(request, user_id):
    """AJAX API for deleting users - Managers cannot delete"""
    try:
        # Managers cannot delete users
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'message': 'Managers cannot delete users.'
            }, status=403)
        
        user = User.objects.get(id=user_id)
        
        # Prevent deleting superusers (unless current user is also superuser)
        # Allow superusers to delete other accounts, but prevent non-superusers from deleting superusers
        if user.is_superuser and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete superuser accounts. Only superusers can delete other superuser accounts.'
            }, status=403)
        
        # Prevent deleting self
        if user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'Cannot delete your own account'
            }, status=403)
        
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'User deleted successfully'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def profile_update_api(request):
    """AJAX API for updating user profile"""
    try:
        import os
        user = request.user
        updated_fields = []
        has_changes = False
        
        # Get or create profile once at the start
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update basic user fields - only if value is different
        if 'first_name' in request.POST:
            new_first_name = request.POST.get('first_name', '')
            if new_first_name != user.first_name:
                user.first_name = new_first_name
                updated_fields.append('first_name')
                has_changes = True
        
        if 'last_name' in request.POST:
            new_last_name = request.POST.get('last_name', '')
            if new_last_name != user.last_name:
                user.last_name = new_last_name
                updated_fields.append('last_name')
                has_changes = True
        
        if 'email' in request.POST:
            new_email = request.POST.get('email', '')
            if new_email != user.email:
                # Check if email is already taken by another user
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'Email is already taken'
                    })
                user.email = new_email
                updated_fields.append('email')
                has_changes = True
        
        if 'username' in request.POST:
            new_username = request.POST.get('username', '')
            if new_username != user.username:
                # Check if username is already taken by another user
                if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'Username is already taken'
                    })
                user.username = new_username
                updated_fields.append('username')
                has_changes = True
        
        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            # Verify current password
            if not authenticate(username=user.username, password=current_password):
                return JsonResponse({
                    'success': False,
                    'message': 'Current password is incorrect'
                })
            
            # Check if new passwords match
            if new_password != confirm_password:
                return JsonResponse({
                    'success': False,
                    'message': 'New passwords do not match'
                })
            
            # Set new password
            user.set_password(new_password)
            updated_fields.append('password')
            has_changes = True
        
        # Handle profile picture upload
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            
            # Validate file size (max 5MB)
            if photo.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': 'Profile picture size must be less than 5MB'
                })
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if photo.content_type not in allowed_types:
                return JsonResponse({
                    'success': False,
                    'message': 'Please upload a valid image file (JPEG, PNG, GIF, WebP)'
                })
            
            # Delete old profile picture if exists
            if profile.image:
                try:
                    if os.path.isfile(profile.image.path):
                        os.remove(profile.image.path)
                except:
                    pass
            
            # Save new profile picture
            profile.image = photo
            updated_fields.append('photo')
            has_changes = True
        
        # Update phone field - only if value is different
        if 'phone' in request.POST:
            new_phone = request.POST.get('phone', '').strip()
            if new_phone != profile.phone:
                # Check if phone is already taken by another user (phone field is unique)
                if new_phone:
                    existing_profile = Profile.objects.filter(phone=new_phone).exclude(user=user).first()
                    if existing_profile:
                        return JsonResponse({
                            'success': False,
                            'message': f'Phone number {new_phone} is already taken by user {existing_profile.user.username}'
                        })
                    profile.phone = new_phone
                else:
                    # Allow clearing phone number (set to None for unique constraint)
                    profile.phone = None
                updated_fields.append('phone')
                has_changes = True
        
        # Only save if there were actual changes
        if has_changes:
            user.save()
            profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Profile updated successfully! Updated: {", ".join(updated_fields) if updated_fields else "no changes"}',
            'profile_photo_url': profile.image.url if profile.image else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def notification_mark_all_read_api(request):
    """API to mark all notifications as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        from django.utils import timezone
        unread_notifications = Notification.objects.filter(is_read=False)
        count = unread_notifications.count()
        
        if count > 0:
            unread_notifications.update(
                is_read=True,
                read_at=timezone.now(),
                read_by=request.user
            )
        
        # Get updated unread count
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notifications marked as read',
            'count': count,
            'unread_count': unread_count
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in notification_mark_all_read_api: {error_trace}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)



@login_required
@csrf_exempt
@require_http_methods(["POST"])
def user_create_api(request):
    """AJAX API for creating users - Managers cannot use this"""
    # Managers cannot create users via AJAX - only via mobile API
    from accounts.views import is_manager
    is_manager_user = is_manager(request.user)
    
    if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Managers can only create Property Owner accounts via the mobile API (/api/v1/admin/register-owner/).'
        }, status=403)
    
    try:
        # Get form data with sanitization
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        phone = request.POST.get('phone', '').strip()
        role = request.POST.get('role', '').strip()
        is_approved = request.POST.get('is_approved') == 'on'
        
        errors = []
        
        # Validate required fields
        if not first_name:
            errors.append('First name is required.')
        if not last_name:
            errors.append('Last name is required.')
        if not username:
            errors.append('Username is required.')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        elif len(username) > 150:
            errors.append('Username must be less than 150 characters.')
        elif not username.replace('_', '').replace('.', '').isalnum():
            errors.append('Username can only contain letters, numbers, underscores, and periods.')
        
        if not email:
            errors.append('Email is required.')
        else:
            # Email format validation
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        else:
            # Password strength validation
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            if not (has_upper and has_lower and has_digit):
                errors.append('Password must contain at least one uppercase letter, one lowercase letter, and one number.')
        
        if not role:
            errors.append('Role is required.')
        
        if not phone:
            errors.append('Phone number is required.')
        elif phone:
            # Check phone uniqueness
            from accounts.models import Profile
            if Profile.objects.filter(phone=phone).exists():
                errors.append('Phone number already exists. Please use a different phone number.')
        
        # Check if username already exists
        if username and User.objects.filter(username=username).exists():
            errors.append('Username already exists.')
        
        # Check if email already exists
        if email and User.objects.filter(email__iexact=email).exists():
            errors.append('Email already exists.')
        
        if errors:
            return JsonResponse({
                'success': False,
                'message': ' '.join(errors)
            })
        
        # Create user (set as active by default)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        
        # Create profile
        from accounts.models import Profile, CustomRole, UserRole
        from django.utils import timezone
        
        profile = Profile.objects.create(
            user=user,
            phone=phone,
            role=role,
            is_approved=is_approved
        )
        
        # If approved, set approval metadata
        if is_approved:
            profile.approved_at = timezone.now()
            profile.approved_by = request.user
            profile.save()
        
        # Assign custom role based on selection
        role_name = 'Tenant' if role == 'tenant' else 'Property Owner'
        try:
            custom_role = CustomRole.objects.get(name=role_name)
        except CustomRole.DoesNotExist:
            # Create role if it doesn't exist
            description = 'Property tenant with mobile app access' if role == 'tenant' else 'Property owner with mobile app access'
            custom_role = CustomRole.objects.create(
                name=role_name,
                description=description
            )
        
        # Ensure role is assigned (use get_or_create to avoid duplicates)
        UserRole.objects.get_or_create(user=user, role=custom_role, defaults={'assigned_by': request.user})
        
        return JsonResponse({
            'success': True,
            'message': f'User {user.get_full_name()} created successfully',
            'user_id': user.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@require_http_methods(["GET"])
def role_search_api(request):
    """AJAX API for searching roles"""
    search_query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 5))
    
    # Start with all roles
    from accounts.models import CustomRole
    roles = CustomRole.objects.prefetch_related('permissions', 'userrole_set').all()
    
    # Apply search filter
    if search_query:
        roles = roles.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Order by name
    roles = roles.order_by('name')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(roles, per_page)
    page_obj = paginator.get_page(page)
    
    # Convert roles to JSON format
    roles_data = []
    for role in page_obj:
        role_data = {
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions_count': role.permissions.count(),
            'users_count': role.userrole_set.count(),
            'created_at': role.created_at.strftime('%b %d, %Y') if hasattr(role, 'created_at') else 'N/A'
        }
        roles_data.append(role_data)
    
    return JsonResponse({
        'roles': roles_data,
        'total_count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def role_create_api(request):
    """AJAX API for creating roles"""
    try:
        # Get form data
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        permissions = request.POST.getlist('permissions')
        navigation_permissions = request.POST.getlist('navigation_permissions')
        
        # Validate required fields
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Role name is required'
            })
        
        # Check if role name already exists
        from accounts.models import CustomRole
        if CustomRole.objects.filter(name=name).exists():
            return JsonResponse({
                'success': False,
                'message': 'Role name already exists'
            })
        
        # Create role
        role = CustomRole.objects.create(
            name=name,
            description=description
        )
        
        # If this is an Admin role, assign all permissions automatically
        if name.lower() in ['admin', 'administrator', 'system administrator']:
            from django.contrib.auth.models import Permission
            all_permissions = Permission.objects.all()
            role.permissions.set(all_permissions)
            
            # Also assign all navigation permissions
            from accounts.models import NavigationItem, RoleNavigationPermission
            all_navigation_items = NavigationItem.objects.filter(is_active=True)
            for nav_item in all_navigation_items:
                RoleNavigationPermission.objects.get_or_create(
                    role=role,
                    navigation_item=nav_item,
                    defaults={'can_access': True}
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Admin role "{role.name}" created with ALL permissions automatically!',
                'role_id': role.id
            })
        else:
            # For non-admin roles, use the selected permissions
            if permissions:
                from django.contrib.auth.models import Permission
                permission_objects = Permission.objects.filter(id__in=permissions)
                role.permissions.set(permission_objects)
            
            # Handle navigation permissions
            if navigation_permissions:
                from accounts.models import NavigationItem, RoleNavigationPermission
                for nav_item_id in navigation_permissions:
                    try:
                        nav_item = NavigationItem.objects.get(id=nav_item_id)
                        RoleNavigationPermission.objects.create(
                            role=role,
                            navigation_item=nav_item,
                            can_access=True
                        )
                    except NavigationItem.DoesNotExist:
                        continue
            
            return JsonResponse({
                'success': True,
                'message': f'Role "{role.name}" created successfully',
                'role_id': role.id
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@require_http_methods(["GET"])
def user_detail_api(request):
    """AJAX API for getting user details - Managers can only see their created users"""
    try:
        from accounts.models import UserRole
        
        user_id = request.GET.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'User ID is required'
            })
        
        user = User.objects.select_related('profile').get(id=user_id)
        
        # Check if user is Manager - Managers can only see details of users they created
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            # Check if this user was created by the Manager
            user_created_by_manager = (
                UserRole.objects.filter(user=user, assigned_by=request.user).exists() or
                (hasattr(user, 'profile') and user.profile.approved_by == request.user)
            )
            
            if not user_created_by_manager:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only view details of users you created.'
                }, status=403)
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'profile': None
        }
        
        if user.profile:
            user_data['profile'] = {
                'role': user.profile.role,
                'phone': user.profile.phone,
                'is_approved': user.profile.is_approved
            }
        
        return JsonResponse({
            'success': True,
            'user': user_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@csrf_exempt
@require_http_methods(["POST"])
def user_update_api(request):
    """AJAX API for updating users - Managers can only update their created users"""
    try:
        from accounts.models import UserRole
        
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'User ID is required'
            })
        
        user = User.objects.get(id=user_id)
        
        # Check if user is Manager - Managers can only update users they created
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            # Check if this user was created by the Manager
            user_created_by_manager = (
                UserRole.objects.filter(user=user, assigned_by=request.user).exists() or
                (hasattr(user, 'profile') and user.profile.approved_by == request.user)
            )
            
            if not user_created_by_manager:
                return JsonResponse({
                    'success': False,
                    'message': 'You can only update users you created.'
                }, status=403)
        
        # Update basic user fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.username = request.POST.get('username', user.username)
        
        # Check if username is already taken by another user
        if User.objects.filter(username=user.username).exclude(id=user.id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username is already taken'
            })
        
        # Check if email is already taken by another user
        if User.objects.filter(email=user.email).exclude(id=user.id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email is already taken'
            })
        
        # Update profile (only phone - role and approval are managed separately)
        from accounts.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        if 'phone' in request.POST:
            new_phone = request.POST.get('phone', '').strip()
            # Check if phone is already taken by another user (phone field is unique)
            if new_phone:
                existing_profile = Profile.objects.filter(phone=new_phone).exclude(user=user).first()
                if existing_profile:
                    return JsonResponse({
                        'success': False,
                        'message': f'Phone number {new_phone} is already taken by user {existing_profile.user.username}'
                    })
                profile.phone = new_phone
            else:
                # Allow clearing phone number (set to None for unique constraint)
                profile.phone = None
        # Note: role and is_approved are NOT updated here - they have dedicated actions:
        # - Role: Use "Assign Roles" from dropdown menu
        # - Approval: Use "Approve/Unapprove" from dropdown menu
        
        # Save changes
        user.save()
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': f'User {user.get_full_name()} updated successfully'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@require_http_methods(["GET"])
def role_detail_api(request):
    """AJAX API for getting role details"""
    try:
        role_id = request.GET.get('role_id')
        if not role_id:
            return JsonResponse({
                'success': False,
                'message': 'Role ID is required'
            })
        
        from accounts.models import CustomRole, UserRole
        role = CustomRole.objects.prefetch_related('permissions', 'userrole_set__user').get(id=role_id)
        
        # Get permissions data
        permissions_data = []
        for permission in role.permissions.all():
            permissions_data.append({
                'id': permission.id,
                'name': permission.name,
                'codename': permission.codename
            })
        
        # Get users data
        users_data = []
        for user_role in role.userrole_set.all():
            users_data.append({
                'id': user_role.user.id,
                'username': user_role.user.username,
                'email': user_role.user.email,
                'full_name': user_role.user.get_full_name()
            })
        
        role_data = {
            'id': role.id,
            'name': role.name,
            'description': role.description,
            'permissions_count': role.permissions.count(),
            'users_count': role.userrole_set.count(),
            'permissions': permissions_data,
            'users': users_data,
            'created_at': role.created_at.strftime('%B %d, %Y at %I:%M %p') if hasattr(role, 'created_at') else 'N/A'
        }
        
        return JsonResponse({
            'success': True,
            'role': role_data
        })
        
    except CustomRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Role not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@csrf_exempt
@require_http_methods(["POST"])
def role_update_api(request):
    """AJAX API for updating roles"""
    try:
        role_id = request.POST.get('role_id')
        if not role_id:
            return JsonResponse({
                'success': False,
                'message': 'Role ID is required'
            })
        
        from accounts.models import CustomRole
        role = CustomRole.objects.get(id=role_id)
        
        # Update role fields
        role.name = request.POST.get('name', role.name)
        role.description = request.POST.get('description', role.description)
        
        # Check if role name already exists
        if CustomRole.objects.filter(name=role.name).exclude(id=role.id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Role name already exists'
            })
        
        # Save changes
        role.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Role "{role.name}" updated successfully'
        })
        
    except CustomRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Role not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@require_http_methods(["GET"])
def role_permissions_detail_api(request):
    """AJAX API for getting role permissions"""
    try:
        role_id = request.GET.get('role_id')
        if not role_id:
            return JsonResponse({
                'success': False,
                'message': 'Role ID is required'
            })
        
        from accounts.models import CustomRole, RoleNavigationPermission
        role = CustomRole.objects.prefetch_related('permissions').get(id=role_id)
        
        # Get permission IDs
        permission_ids = list(role.permissions.values_list('id', flat=True))
        
        # Get navigation permission IDs
        nav_permission_ids = list(RoleNavigationPermission.objects.filter(role=role).values_list('navigation_item_id', flat=True))
        
        role_data = {
            'id': role.id,
            'name': role.name,
            'permissions': permission_ids,
            'navigation_permissions': nav_permission_ids
        }
        
        return JsonResponse({
            'success': True,
            'role': role_data
        })
        
    except CustomRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Role not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@csrf_exempt
@require_http_methods(["POST"])
def role_permissions_api(request):
    """AJAX API for updating role permissions"""
    try:
        role_id = request.POST.get('role_id')
        if not role_id:
            return JsonResponse({
                'success': False,
                'message': 'Role ID is required'
            })
        
        from accounts.models import CustomRole, RoleNavigationPermission
        role = CustomRole.objects.get(id=role_id)
        
        # Get selected permissions and navigation items
        permissions = request.POST.getlist('permissions')
        navigation_permissions = request.POST.getlist('navigation_permissions')
        
        # Update permissions
        if permissions:
            from django.contrib.auth.models import Permission
            permission_objects = Permission.objects.filter(id__in=permissions)
            role.permissions.set(permission_objects)
        else:
            role.permissions.clear()
        
        # Update navigation permissions
        # First, remove all existing navigation permissions for this role
        RoleNavigationPermission.objects.filter(role=role).delete()
        
        # Then add the new ones
        if navigation_permissions:
            from accounts.models import NavigationItem
            from django.contrib.auth.models import Permission
            
            # Mapping of navigation items to required system permissions
            # This ensures that when a navigation permission is granted, the required system permission is also granted
            # This prevents the issue where users can see menu items but can't access the pages
            NAV_TO_SYSTEM_PERM_MAP = {
                # Properties
                'property_list': 'properties.view_property',
                'properties': 'properties.view_property',
                
                # Maintenance
                'request_list': 'maintenance.view_maintenancerequest',
                'maintenance': 'maintenance.view_maintenancerequest',
                
                # Complaints
                'complaint_list': 'complaints.view_complaint',
                'complaints': 'complaints.view_complaint',
                
                # User Management
                'user_list': 'accounts.view_user',
                'all_users': 'accounts.view_user',
                
                # Payments
                'payment_list': 'payments.view_payment',
                'payments': 'payments.view_payment',
                
                # Bookings
                'hotel_bookings': 'properties.view_booking',
                'lodge_bookings': 'properties.view_booking',
                'venue_bookings': 'properties.view_booking',
                'house_bookings': 'properties.view_booking',
            }
            
            required_permissions_to_add = set()
            
            for nav_item_id in navigation_permissions:
                try:
                    nav_item = NavigationItem.objects.get(id=nav_item_id)
                    RoleNavigationPermission.objects.create(
                        role=role,
                        navigation_item=nav_item,
                        can_access=True
                    )
                    
                    # Check if this navigation item requires a system permission
                    nav_name = nav_item.name
                    if nav_name in NAV_TO_SYSTEM_PERM_MAP:
                        perm_string = NAV_TO_SYSTEM_PERM_MAP[nav_name]
                        app_label, codename = perm_string.split('.')
                        try:
                            required_perm = Permission.objects.get(
                                codename=codename,
                                content_type__app_label=app_label
                            )
                            required_permissions_to_add.add(required_perm)
                        except Permission.DoesNotExist:
                            pass  # Permission doesn't exist, skip
                            
                except NavigationItem.DoesNotExist:
                    continue
            
            # Automatically add required system permissions
            if required_permissions_to_add:
                for perm in required_permissions_to_add:
                    if perm not in role.permissions.all():
                        role.permissions.add(perm)
        
        return JsonResponse({
            'success': True,
            'message': f'Permissions for role "{role.name}" updated successfully'
        })
        
    except CustomRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Role not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@require_http_methods(["GET"])
def user_roles_api(request, user_id):
    """AJAX API for getting user roles"""
    try:
        from accounts.models import UserRole
        
        user = User.objects.get(id=user_id)
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        
        roles_data = []
        for user_role in user_roles:
            roles_data.append({
                'id': user_role.id,
                'role': {
                    'id': user_role.role.id,
                    'name': user_role.role.name,
                    'description': user_role.role.description
                },
                'assigned_at': user_role.assigned_at.strftime('%B %d, %Y')
            })
        
        return JsonResponse({
            'success': True,
            'user_roles': roles_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)




@login_required
@csrf_exempt
@require_http_methods(["POST"])
def role_delete_api(request, role_id):
    """AJAX API for deleting roles"""
    try:
        from .models import CustomRole
        role = CustomRole.objects.get(id=role_id)
        role_name = role.name
        role.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Role "{role_name}" deleted successfully'
        })
    except CustomRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Role not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


def user_roles_update_api(request, user_id):
    """AJAX API for updating user roles"""
    try:
        from accounts.models import UserRole, CustomRole
        
        # Check if user is Manager - Managers cannot assign/update roles
        from accounts.views import is_manager
        is_manager_user = is_manager(request.user)
        
        if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'message': 'Managers cannot assign or update user roles'
            }, status=403)
        
        user = User.objects.get(id=user_id)
        selected_roles = request.POST.getlist('roles')
        
        # Get current user roles
        current_roles = set(UserRole.objects.filter(user=user).values_list('role_id', flat=True))
        new_roles = set(int(role_id) for role_id in selected_roles if role_id)
        
        # Roles to add
        roles_to_add = new_roles - current_roles
        # Roles to remove
        roles_to_remove = current_roles - new_roles
        
        # Add new roles
        for role_id in roles_to_add:
            try:
                role = CustomRole.objects.get(id=role_id)
                UserRole.objects.get_or_create(
                    user=user, 
                    role=role,
                    defaults={'assigned_by': request.user if hasattr(request, 'user') else None}
                )
            except CustomRole.DoesNotExist:
                continue
            except Exception as e:
                # Handle case where role already exists (shouldn't happen due to unique_together, but just in case)
                continue
        
        # Remove roles
        if roles_to_remove:
            UserRole.objects.filter(user=user, role_id__in=roles_to_remove).delete()
        
        # Prepare response message
        messages = []
        if roles_to_add:
            messages.append(f"Added {len(roles_to_add)} role(s)")
        if roles_to_remove:
            messages.append(f"Removed {len(roles_to_remove)} role(s)")
        
        if not messages:
            messages.append("No changes made")
        
        return JsonResponse({
            'success': True,
            'message': '; '.join(messages)
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# Notification API endpoints
@login_required
@require_http_methods(["GET"])
def notification_count_api(request):
    """API to get unread notification count"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'count': 0
        })
    
    count = Notification.get_unread_count(request.user)
    return JsonResponse({
        'success': True,
        'count': count
    })


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_mark_read_api(request, notification_id):
    """API to mark a notification as read"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read(request.user)
        
        # Get updated unread count after marking as read
        unread_count = Notification.get_unread_count(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': unread_count
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def notification_delete_api(request, notification_id):
    """API to delete a notification"""
    if not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        }, status=403)
    
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


