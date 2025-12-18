"""
Permission-based access control middleware for Maisha Backend.

This middleware enforces role-based access control by checking if users
have the required permissions to access specific pages/URLs.
"""

from django.shortcuts import redirect
from django.urls import resolve, reverse, Resolver404
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseForbidden
from django.template.response import TemplateResponse
import logging

logger = logging.getLogger(__name__)


class RolePermissionMiddleware:
    """
    Middleware to enforce role-based access control across the application.
    
    This middleware:
    1. Checks if the user is authenticated
    2. Verifies if the user has the required role/permissions for the URL
    3. Redirects unauthorized users to an appropriate page
    """
    
    # URLs that don't require authentication
    PUBLIC_URLS = [
        'login',
        'register',
        'logout',
        'password_reset',
        'password_reset_done',
        'password_reset_confirm',
        'password_reset_complete',
        'activate_account',
    ]
    
    # URLs that require specific permissions (URL name: required permission codename)
    PERMISSION_REQUIRED_URLS = {
        # Admin-only pages
        'role_list': 'accounts.view_customrole',
        'role_create': 'accounts.add_customrole',
        'role_edit': 'accounts.change_customrole',
        'role_delete': 'accounts.delete_customrole',
        'user_list': 'accounts.view_profile',
        'user_edit': 'accounts.change_profile',
        'user_delete': 'accounts.delete_profile',
        'system_logs': 'accounts.view_activitylog',
        
        # Property management
        'property_list': 'properties.view_property',
        'property_create': 'properties.add_property',
        'property_edit': 'properties.change_property',
        'property_delete': 'properties.delete_property',
        'manage_property_types': 'properties.change_propertytype',
        'manage_regions': 'properties.change_region',
        'manage_amenities': 'properties.change_amenity',
        'house_rent_reminder_settings': 'properties.view_houserentremindersetting',
        
        # Hotel management
        'hotel_dashboard': 'properties.view_property',
        'hotel_bookings': 'properties.view_booking',
        'hotel_rooms': 'properties.view_room',
        'hotel_customers': 'properties.view_booking',
        'hotel_payments': 'payments.view_payment',
        'hotel_reports': 'reports.view_report',
        
        # Lodge management
        'lodge_dashboard': 'properties.view_property',
        'lodge_bookings': 'properties.view_booking',
        'lodge_rooms': 'properties.view_room',
        'lodge_customers': 'properties.view_booking',
        'lodge_payments': 'payments.view_payment',
        'lodge_reports': 'reports.view_report',
        
        # Venue management
        'venue_dashboard': 'properties.view_property',
        'venue_bookings': 'properties.view_booking',
        'venue_availability': 'properties.view_property',
        'venue_customers': 'properties.view_booking',
        'venue_payments': 'payments.view_payment',
        'venue_reports': 'reports.view_report',
        
        # House management
        'house_dashboard': 'properties.view_property',
        'house_bookings': 'properties.view_booking',
        'house_tenants': 'documents.view_lease',
        'house_payments': 'payments.view_payment',
        'house_reports': 'reports.view_report',
        
        # Maintenance management
        'request_list': 'maintenance.view_maintenancerequest',
        'maintenance_list': 'maintenance.view_maintenancerequest',
        'maintenance_create': 'maintenance.add_maintenancerequest',
        'maintenance_edit': 'maintenance.change_maintenancerequest',
        'maintenance_delete': 'maintenance.delete_maintenancerequest',
        
        # Payment management
        'payment_list': 'payments.view_payment',
        'payment_create': 'payments.add_payment',
        'payment_edit': 'payments.change_payment',
        
        # Document management
        'document_list': 'documents.view_document',
        'document_upload': 'documents.add_document',
        'document_delete': 'documents.delete_document',
        
        # Rent management
        'rent_list': 'rent.view_rentpayment',
        'rent_create': 'rent.add_rentpayment',
        
        # Complaints
        'complaint_list': 'complaints.view_complaint',
        
        # Reports (typically admin/manager only)
        'reports_dashboard': 'reports.view_report',
    }
    
    # Role-based URL access (URL name: list of allowed role names)
    # NOTE: URLs in PERMISSION_REQUIRED_URLS take precedence over ROLE_REQUIRED_URLS
    # Only use ROLE_REQUIRED_URLS for URLs that don't have specific permission requirements
    ROLE_REQUIRED_URLS = {
        # Admin-only pages (no specific permissions, just role-based)
        'role_list': ['Admin'],
        'role_create': ['Admin'],
        'role_edit': ['Admin'],
        'role_delete': ['Admin'],
        'user_list': ['Admin', 'Manager'],
        'user_edit': ['Admin', 'Manager'],
        'system_logs': ['Admin'],
        
        # Note: property_list, property_create, property_edit are now in PERMISSION_REQUIRED_URLS
        # so they will be checked by permissions, not roles
        
        # Maintenance accessible by owners and tenants (if not in PERMISSION_REQUIRED_URLS)
        # 'maintenance_list': ['Admin', 'Manager', 'Property owner', 'Tenant'],
        # 'maintenance_create': ['Admin', 'Manager', 'Property owner', 'Tenant'],
        
        # Payments accessible by owners and tenants (if not in PERMISSION_REQUIRED_URLS)
        # 'payment_list': ['Admin', 'Manager', 'Property owner', 'Tenant'],
        
        # Reports for admin/manager/owners (if not in PERMISSION_REQUIRED_URLS)
        # 'reports_dashboard': ['Admin', 'Manager', 'Property owner'],
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check permissions before processing the view
        if not self._check_access(request):
            return self._handle_forbidden_access(request)
        
        response = self.get_response(request)
        
        # Ensure TemplateResponse is rendered before returning
        # This prevents ContentNotRenderedError when middleware tries to access response.content
        if isinstance(response, TemplateResponse) and not response.is_rendered:
            response.render()
        
        return response
    
    def _check_access(self, request):
        """
        Check if the user has access to the current URL.
        
        Returns:
            bool: True if access is allowed, False otherwise
        """
        # Skip middleware for static files and media
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return True
        
        # Skip middleware for API endpoints (they have their own permission classes)
        if request.path.startswith('/api/'):
            return True
        
        # Skip middleware for common non-route files (favicon, robots.txt, etc.)
        if request.path in ['/favicon.ico', '/robots.txt', '/apple-touch-icon.png']:
            return True
        
        try:
            # Resolve the current URL to get the URL name
            resolved = resolve(request.path)
            url_name = resolved.url_name
            
            # Allow access to public URLs
            if url_name in self.PUBLIC_URLS:
                return True
            
            # Check if user is authenticated
            if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
                # Redirect to login will be handled by _handle_forbidden_access
                return url_name in self.PUBLIC_URLS
            
            # Superusers have access to everything
            if request.user.is_superuser:
                return True
            
            # Check if the user's profile is approved
            if hasattr(request.user, 'profile'):
                # MULTI-TENANCY: Check if user is deactivated (admin control)
                if request.user.profile.is_deactivated:
                    # Only allow logout for deactivated users
                    if url_name not in ['logout']:
                        logger.warning(f"Deactivated user {request.user.username} attempted to access {url_name}")
                        return False
                
                if not request.user.profile.is_approved:
                    # Only allow access to dashboard and logout for unapproved users
                    if url_name not in ['dashboard', 'logout', 'profile']:
                        logger.warning(f"Unapproved user {request.user.username} attempted to access {url_name}")
                        return False
            
            # Check permission-based access FIRST (more granular)
            if url_name in self.PERMISSION_REQUIRED_URLS:
                required_permission = self.PERMISSION_REQUIRED_URLS[url_name]
                
                if not self._has_permission(request.user, required_permission):
                    logger.warning(
                        f"User {request.user.username} attempted to access {url_name} "
                        f"without permission: {required_permission}"
                    )
                    return False
                else:
                    # Permission check passed, allow access
                    return True
            
            # Check role-based access (fallback for URLs without specific permissions)
            if url_name in self.ROLE_REQUIRED_URLS:
                allowed_roles = self.ROLE_REQUIRED_URLS[url_name]
                user_role = self._get_user_primary_role(request.user)
                
                if user_role not in allowed_roles:
                    logger.warning(
                        f"User {request.user.username} with role '{user_role}' "
                        f"attempted to access {url_name} (requires: {allowed_roles})"
                    )
                    return False
            
            # Allow access if no specific restrictions
            return True
            
        except Resolver404:
            # URL not found in URLconf - this is normal for some requests (e.g., favicon.ico)
            # Allow access and don't log as an error
            return True
        except Exception as e:
            # Only log actual errors, not expected 404s
            # Use a concise error message instead of the full exception string
            logger.error(
                f"Error in permission middleware for path '{request.path}': {type(e).__name__}: {str(e)[:200]}"
            )
            # In case of error, allow access but log it
            return True
    
    def _get_user_primary_role(self, user):
        """Get the user's primary role."""
        if hasattr(user, 'profile'):
            return user.profile.get_primary_role()
        return None
    
    def _has_permission(self, user, permission_string):
        """
        Check if user has a specific permission.
        
        Args:
            user: Django User object
            permission_string: Permission in format 'app_label.permission_codename'
        
        Returns:
            bool: True if user has permission
        """
        # Django's built-in permission check
        if user.has_perm(permission_string):
            return True
        
        # Check custom role permissions
        if hasattr(user, 'profile'):
            user_roles = user.profile.get_user_roles()
            
            # Parse permission string
            try:
                app_label, codename = permission_string.split('.')
                
                # Check if any of the user's roles has this permission
                for role in user_roles:
                    if role.permissions.filter(
                        content_type__app_label=app_label,
                        codename=codename
                    ).exists():
                        return True
            except ValueError:
                logger.error(f"Invalid permission string format: {permission_string}")
        
        return False
    
    def _handle_forbidden_access(self, request):
        """
        Handle forbidden access attempts.
        
        Returns appropriate response based on user authentication status.
        """
        try:
            resolved = resolve(request.path)
            url_name = resolved.url_name
        except:
            url_name = request.path
        
        # If user is not authenticated, redirect to login
        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access this page.')
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        # If user is not approved
        if hasattr(request.user, 'profile') and not request.user.profile.is_approved:
            messages.error(
                request,
                'Your account is pending approval. Please wait for an administrator to approve your account.'
            )
            return redirect('accounts:dashboard')
        
        # If user lacks permissions, show forbidden page
        messages.error(
            request,
            'You do not have permission to access this page. Please contact an administrator if you believe this is an error.'
        )
        
        # Return a custom 403 forbidden page
        return self._render_forbidden_page(request)
    
    def _render_forbidden_page(self, request):
        """Render a custom 403 forbidden page."""
        from django.shortcuts import render
        from django.http import HttpResponse
        
        context = {
            'error_code': '403',
            'error_title': 'Access Forbidden',
            'error_message': 'You do not have permission to access this page.',
            'show_dashboard_link': True,
        }
        # Use render() instead of TemplateResponse to return a fully rendered HttpResponse
        response = render(request, 'accounts/403.html', context)
        response.status_code = 403
        return response


class SessionTimeoutMiddleware:
    """
    Middleware to enforce session timeout based on inactivity.
    
    This middleware tracks the last activity time and automatically logs out
    users who have been inactive for more than SESSION_COOKIE_AGE seconds.
    """
    
    # URLs to exclude from timeout checking (public endpoints)
    EXCLUDE_URLS = [
        '/login/',
        '/logout/',
        '/register/',
        '/api/',
        '/static/',
        '/media/',
        '/admin/login/',
        '/admin/logout/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check session timeout before processing the request
        session_expired = False
        if self._should_check_timeout(request):
            session_expired = self._check_session_timeout(request)
        
        # If session expired, redirect to login immediately
        if session_expired:
            from django.contrib import messages
            messages.warning(request, 'Your session has expired due to inactivity. Please log in again.')
            return redirect('accounts:login')
        
        response = self.get_response(request)
        
        # Update last activity time after successful request
        if self._should_update_activity(request):
            self._update_last_activity(request)
        
        return response
    
    def _should_check_timeout(self, request):
        """Determine if we should check session timeout for this request."""
        # Don't check for anonymous users
        if not request.user.is_authenticated:
            return False
        
        # Don't check excluded URLs
        for exclude_url in self.EXCLUDE_URLS:
            if request.path.startswith(exclude_url):
                return False
        
        return True
    
    def _should_update_activity(self, request):
        """Determine if we should update last activity time."""
        # Only update for authenticated users
        if not request.user.is_authenticated:
            return False
        
        # Don't update for excluded URLs
        for exclude_url in self.EXCLUDE_URLS:
            if request.path.startswith(exclude_url):
                return False
        
        return True
    
    def _check_session_timeout(self, request):
        """Check if session has expired due to inactivity. Returns True if session expired."""
        from django.conf import settings
        from django.utils import timezone
        from django.contrib.auth import logout
        
        # Get last activity time from session
        last_activity = request.session.get('last_activity')
        
        if last_activity:
            # Calculate time since last activity
            try:
                if isinstance(last_activity, str):
                    from datetime import datetime
                    last_activity_time = datetime.fromisoformat(last_activity)
                    # Make timezone-aware if it's not
                    if timezone.is_naive(last_activity_time):
                        last_activity_time = timezone.make_aware(last_activity_time)
                else:
                    last_activity_time = last_activity
                
                # Get session timeout from settings
                timeout_seconds = getattr(settings, 'SESSION_COOKIE_AGE', 1800)  # Default 30 minutes
                
                # Calculate elapsed time
                elapsed = (timezone.now() - last_activity_time).total_seconds()
                
                # If elapsed time exceeds timeout, expire the session
                if elapsed > timeout_seconds:
                    username = request.user.username if request.user.is_authenticated else 'Anonymous'
                    logger.info(f"Session expired for user {username} after {elapsed:.0f} seconds of inactivity")
                    # Logout the user first (before flushing session)
                    logout(request)
                    # Clear the session
                    request.session.flush()
                    return True
            except (ValueError, TypeError) as e:
                logger.warning(f"Error checking session timeout: {str(e)}")
                # If we can't parse the time, set it to now
                request.session['last_activity'] = timezone.now().isoformat()
        else:
            # If no last_activity is set, set it now (for new sessions)
            request.session['last_activity'] = timezone.now().isoformat()
        
        return False
    
    def _update_last_activity(self, request):
        """Update the last activity time in the session."""
        from django.utils import timezone
        request.session['last_activity'] = timezone.now().isoformat()
        # Mark session as modified to ensure it's saved
        request.session.modified = True


class ActivityLoggingMiddleware:
    """
    Middleware to automatically log user activities.
    
    This creates activity logs for important actions across the system.
    """
    
    # Methods that should trigger activity logging
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # URLs to exclude from logging
    EXCLUDE_URLS = [
        '/static/',
        '/media/',
        '/api/auth/token/refresh/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log activity after the response
        if self._should_log(request):
            self._log_activity(request, response)
        
        return response
    
    def _should_log(self, request):
        """Determine if this request should be logged."""
        # Don't log if user is not authenticated
        if not request.user.is_authenticated:
            return False
        
        # Don't log excluded URLs
        for exclude in self.EXCLUDE_URLS:
            if request.path.startswith(exclude):
                return False
        
        # Only log certain HTTP methods
        return request.method in self.LOGGED_METHODS
    
    def _log_activity(self, request, response):
        """Create an activity log entry."""
        try:
            from accounts.models import ActivityLog
            
            # Only log successful operations (2xx status codes)
            if 200 <= response.status_code < 300:
                resolved = resolve(request.path)
                url_name = resolved.url_name
                
                # Determine action type based on HTTP method
                action_map = {
                    'POST': 'create',
                    'PUT': 'update',
                    'PATCH': 'update',
                    'DELETE': 'delete',
                }
                action = action_map.get(request.method, 'update')
                
                # Create description based on URL
                description = self._generate_description(url_name, action, request)
                
                # Create activity log
                ActivityLog.objects.create(
                    user=request.user,
                    action=action,
                    description=description,
                    content_type=self._get_content_type(url_name),
                    priority='medium',
                )
                
        except Exception as e:
            # Don't let logging errors break the application
            logger.error(f"Error logging activity: {str(e)}")
    
    def _generate_description(self, url_name, action, request):
        """Generate a human-readable description of the activity."""
        action_verb = {
            'create': 'created',
            'update': 'updated',
            'delete': 'deleted',
        }.get(action, 'modified')
        
        # Extract resource type from URL name
        if url_name:
            resource = url_name.replace('_', ' ').title()
            return f"{action_verb.capitalize()} {resource}"
        
        return f"{action_verb.capitalize()} resource at {request.path}"
    
    def _get_content_type(self, url_name):
        """Determine content type from URL name."""
        if not url_name:
            return 'Unknown'
        
        # Map URL patterns to content types
        if 'property' in url_name.lower():
            return 'Property'
        elif 'maintenance' in url_name.lower():
            return 'Maintenance'
        elif 'payment' in url_name.lower():
            return 'Payment'
        elif 'document' in url_name.lower():
            return 'Document'
        elif 'lease' in url_name.lower():
            return 'Lease'
        elif 'user' in url_name.lower() or 'profile' in url_name.lower():
            return 'User'
        elif 'role' in url_name.lower():
            return 'Role'
        
        return 'General'
