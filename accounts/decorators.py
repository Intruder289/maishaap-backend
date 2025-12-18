"""
Custom decorators for permission and role-based access control.

These decorators can be used in views to enforce specific permission
or role requirements beyond what the middleware provides.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template.response import TemplateResponse
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


def role_required(*allowed_roles):
    """
    Decorator to restrict view access to specific roles.
    
    Usage:
        @role_required('Admin', 'Manager')
        def my_view(request):
            ...
    
    Args:
        *allowed_roles: Variable number of role names that are allowed
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect(f"{reverse('accounts:login')}?next={request.path}")
            
            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Get user's primary role
            user_role = None
            if hasattr(request.user, 'profile'):
                user_role = request.user.profile.get_primary_role()
            
            # Check if user has required role
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Access denied
            logger.warning(
                f"User {request.user.username} with role '{user_role}' "
                f"attempted to access {view_func.__name__} (requires: {allowed_roles})"
            )
            messages.error(
                request,
                f'Access denied. This page requires one of the following roles: {", ".join(allowed_roles)}'
            )
            
            context = {
                'error_code': '403',
                'error_title': 'Access Forbidden',
                'error_message': f'This page requires one of the following roles: {", ".join(allowed_roles)}',
                'show_dashboard_link': True,
            }
            return TemplateResponse(request, 'accounts/403.html', context, status=403)
        
        return wrapper
    return decorator


def permission_required(permission_string):
    """
    Decorator to restrict view access to users with specific permissions.
    
    Usage:
        @permission_required('properties.add_property')
        def create_property(request):
            ...
    
    Args:
        permission_string: Permission in format 'app_label.permission_codename'
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.warning(request, 'Please log in to access this page.')
                return redirect(f"{reverse('accounts:login')}?next={request.path}")
            
            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check Django permission
            if request.user.has_perm(permission_string):
                return view_func(request, *args, **kwargs)
            
            # Check custom role permissions
            if hasattr(request.user, 'profile'):
                try:
                    app_label, codename = permission_string.split('.')
                    user_roles = request.user.profile.get_user_roles()
                    
                    for role in user_roles:
                        if role.permissions.filter(
                            content_type__app_label=app_label,
                            codename=codename
                        ).exists():
                            return view_func(request, *args, **kwargs)
                except ValueError:
                    logger.error(f"Invalid permission string format: {permission_string}")
            
            # Access denied
            logger.warning(
                f"User {request.user.username} attempted to access {view_func.__name__} "
                f"without permission: {permission_string}"
            )
            messages.error(
                request,
                'Access denied. You do not have the required permissions to access this page.'
            )
            
            context = {
                'error_code': '403',
                'error_title': 'Permission Required',
                'error_message': 'You do not have the required permissions to access this page.',
                'show_dashboard_link': True,
            }
            return TemplateResponse(request, 'accounts/403.html', context, status=403)
        
        return wrapper
    return decorator


def approved_user_required(view_func):
    """
    Decorator to restrict view access to approved users only.
    
    Usage:
        @approved_user_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user is approved
        if hasattr(request.user, 'profile'):
            if not request.user.profile.is_approved:
                messages.error(
                    request,
                    'Your account is pending approval. Please wait for an administrator to approve your account.'
                )
                return redirect('accounts:dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def ajax_role_required(*allowed_roles):
    """
    Decorator for AJAX views that require specific roles.
    Returns JSON response instead of redirecting.
    
    Usage:
        @ajax_role_required('Admin', 'Manager')
        def my_ajax_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from django.http import JsonResponse
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required'
                }, status=401)
            
            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Get user's primary role
            user_role = None
            if hasattr(request.user, 'profile'):
                user_role = request.user.profile.get_primary_role()
            
            # Check if user has required role
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Access denied
            logger.warning(
                f"User {request.user.username} with role '{user_role}' "
                f"attempted AJAX access to {view_func.__name__} (requires: {allowed_roles})"
            )
            return JsonResponse({
                'success': False,
                'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'
            }, status=403)
        
        return wrapper
    return decorator


def ajax_permission_required(permission_string):
    """
    Decorator for AJAX views that require specific permissions.
    Returns JSON response instead of redirecting.
    
    Usage:
        @ajax_permission_required('properties.add_property')
        def my_ajax_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from django.http import JsonResponse
            
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required'
                }, status=401)
            
            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check Django permission
            if request.user.has_perm(permission_string):
                return view_func(request, *args, **kwargs)
            
            # Check custom role permissions
            if hasattr(request.user, 'profile'):
                try:
                    app_label, codename = permission_string.split('.')
                    user_roles = request.user.profile.get_user_roles()
                    
                    for role in user_roles:
                        if role.permissions.filter(
                            content_type__app_label=app_label,
                            codename=codename
                        ).exists():
                            return view_func(request, *args, **kwargs)
                except ValueError:
                    logger.error(f"Invalid permission string format: {permission_string}")
            
            # Access denied
            logger.warning(
                f"User {request.user.username} attempted AJAX access to {view_func.__name__} "
                f"without permission: {permission_string}"
            )
            return JsonResponse({
                'success': False,
                'error': 'Access denied. Insufficient permissions.'
            }, status=403)
        
        return wrapper
    return decorator


def owner_or_admin_required(view_func):
    """
    Decorator that allows access only to the owner of the resource or admins.
    The view must accept an 'owner_id' or 'user_id' parameter.
    
    Usage:
        @owner_or_admin_required
        def edit_profile(request, user_id):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        # Superusers and admins always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        if hasattr(request.user, 'profile'):
            user_role = request.user.profile.get_primary_role()
            if user_role in ['Admin', 'Manager']:
                return view_func(request, *args, **kwargs)
        
        # Check if user is the owner
        owner_id = kwargs.get('user_id') or kwargs.get('owner_id')
        if owner_id and int(owner_id) == request.user.id:
            return view_func(request, *args, **kwargs)
        
        # Access denied
        logger.warning(
            f"User {request.user.username} attempted to access resource "
            f"belonging to user {owner_id}"
        )
        messages.error(request, 'You can only access your own resources.')
        
        context = {
            'error_code': '403',
            'error_title': 'Access Forbidden',
            'error_message': 'You can only access your own resources.',
            'show_dashboard_link': True,
        }
        return TemplateResponse(request, 'accounts/403.html', context, status=403)
    
    return wrapper

