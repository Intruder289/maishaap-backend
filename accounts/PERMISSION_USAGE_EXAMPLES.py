"""
Example Usage of Permission Middleware and Decorators

This file demonstrates how to use the custom permission system
in your views. Copy and adapt these examples to your own views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.decorators import (
    role_required,
    permission_required,
    approved_user_required,
    owner_or_admin_required,
    ajax_role_required,
    ajax_permission_required
)
from accounts.models import CustomRole, UserRole, Profile
from properties.models import Property
from maintenance.models import MaintenanceRequest


# ============================================================================
# BASIC USAGE EXAMPLES
# ============================================================================

@login_required
def public_dashboard(request):
    """
    Dashboard accessible to all authenticated users.
    Using Django's built-in @login_required is sufficient.
    """
    return render(request, 'accounts/dashboard.html')


@role_required('Admin', 'Manager')
def manage_users_view(request):
    """
    User management page - only accessible by Admin and Manager roles.
    The middleware will check, but decorator provides additional protection.
    """
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})


@permission_required('accounts.add_customrole')
def create_role_view(request):
    """
    Role creation - requires specific Django permission.
    """
    if request.method == 'POST':
        # Create role logic
        pass
    return render(request, 'accounts/role_form.html')


@approved_user_required
def premium_feature_view(request):
    """
    Feature only for approved users.
    Unapproved users will be redirected with a message.
    """
    return render(request, 'accounts/premium.html')


# ============================================================================
# COMBINING DECORATORS
# ============================================================================

@login_required
@role_required('Admin', 'Manager', 'Property owner')
@approved_user_required
def manage_properties_view(request):
    """
    Property management requiring:
    1. Authentication (@login_required)
    2. Specific role (@role_required)
    3. Approved account (@approved_user_required)
    
    Decorators are checked from bottom to top.
    """
    properties = Property.objects.all()
    return render(request, 'properties/property_list.html', {
        'properties': properties
    })


@login_required
@permission_required('properties.delete_property')
def delete_property_view(request, pk):
    """
    Delete property - requires specific permission.
    Only users with delete_property permission can access.
    """
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, 'Property deleted successfully.')
        return redirect('property_list')
    
    return render(request, 'properties/property_confirm_delete.html', {
        'property': property_obj
    })


# ============================================================================
# OWNER-BASED ACCESS CONTROL
# ============================================================================

@owner_or_admin_required
def edit_user_profile(request, user_id):
    """
    Edit user profile - accessible only by the user themselves or admins.
    The decorator checks if user_id matches request.user.id or if user is admin.
    """
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    if request.method == 'POST':
        # Update profile logic
        pass
    
    return render(request, 'accounts/profile_edit.html', {
        'profile_user': user,
        'profile': profile
    })


@login_required
def view_maintenance_request(request, pk):
    """
    View maintenance request with custom owner check.
    Users can only view their own requests unless they're admin/manager.
    """
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
    
    # Custom permission check
    user_role = None
    if hasattr(request.user, 'profile'):
        user_role = request.user.profile.get_primary_role()
    
    # Allow admins, managers, or the request creator
    if not request.user.is_superuser:
        if user_role not in ['Admin', 'Manager']:
            if maintenance_request.user != request.user:
                messages.error(request, 'You can only view your own maintenance requests.')
                return redirect('maintenance_list')
    
    return render(request, 'maintenance/request_detail.html', {
        'request': maintenance_request
    })


# ============================================================================
# AJAX VIEWS
# ============================================================================

@ajax_role_required('Admin', 'Manager')
def ajax_delete_user(request, user_id):
    """
    AJAX endpoint to delete a user.
    Returns JSON response instead of redirecting.
    """
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({'success': True, 'message': 'User deleted successfully'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@ajax_permission_required('properties.change_property')
def ajax_update_property(request, pk):
    """
    AJAX endpoint to update property.
    Requires change_property permission.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        property_obj = Property.objects.get(pk=pk)
        
        # Update property fields
        property_obj.name = request.POST.get('name', property_obj.name)
        property_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Property updated successfully',
            'property': {
                'id': property_obj.id,
                'name': property_obj.name
            }
        })
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Property not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============================================================================
# MANUAL PERMISSION CHECKS (IN VIEW LOGIC)
# ============================================================================

@login_required
def conditional_access_view(request):
    """
    View with conditional access based on complex business logic.
    Use when decorators are not flexible enough.
    """
    user_role = None
    if hasattr(request.user, 'profile'):
        user_role = request.user.profile.get_primary_role()
    
    # Complex permission logic
    can_edit = False
    can_delete = False
    
    if request.user.is_superuser:
        can_edit = True
        can_delete = True
    elif user_role == 'Admin':
        can_edit = True
        can_delete = True
    elif user_role == 'Manager':
        can_edit = True
        can_delete = False
    elif user_role == 'Property owner':
        can_edit = True
        can_delete = False
    
    # Check specific permissions
    if request.user.has_perm('properties.delete_property'):
        can_delete = True
    
    return render(request, 'properties/property_detail.html', {
        'can_edit': can_edit,
        'can_delete': can_delete,
        'user_role': user_role
    })


# ============================================================================
# CHECKING PERMISSIONS IN TEMPLATES
# ============================================================================

def property_list_view(request):
    """
    Property list with permission checks passed to template.
    Template can show/hide UI elements based on permissions.
    """
    properties = Property.objects.all()
    
    # Check permissions
    can_add = request.user.has_perm('properties.add_property')
    can_delete = request.user.has_perm('properties.delete_property')
    
    # Get user role
    user_role = None
    if hasattr(request.user, 'profile'):
        user_role = request.user.profile.get_primary_role()
    
    return render(request, 'properties/property_list.html', {
        'properties': properties,
        'can_add': can_add,
        'can_delete': can_delete,
        'user_role': user_role,
        'is_admin': user_role in ['Admin', 'Manager']
    })


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_user_permissions(user):
    """
    Helper function to get all user permissions.
    Useful for debugging and displaying permissions.
    """
    permissions = []
    
    # Django permissions
    for perm in user.user_permissions.all():
        permissions.append(f"{perm.content_type.app_label}.{perm.codename}")
    
    # Group permissions
    for group in user.groups.all():
        for perm in group.permissions.all():
            perm_str = f"{perm.content_type.app_label}.{perm.codename}"
            if perm_str not in permissions:
                permissions.append(perm_str)
    
    # Custom role permissions
    if hasattr(user, 'profile'):
        for role in user.profile.get_user_roles():
            for perm in role.permissions.all():
                perm_str = f"{perm.content_type.app_label}.{perm.codename}"
                if perm_str not in permissions:
                    permissions.append(perm_str)
    
    return sorted(permissions)


@login_required
@role_required('Admin')
def debug_permissions_view(request, user_id=None):
    """
    Debug view to see all permissions for a user.
    Admin-only for security.
    """
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user
    
    permissions = get_user_permissions(user)
    
    user_role = None
    if hasattr(user, 'profile'):
        user_role = user.profile.get_primary_role()
    
    return render(request, 'accounts/debug_permissions.html', {
        'debug_user': user,
        'permissions': permissions,
        'user_role': user_role,
        'is_superuser': user.is_superuser,
    })


# ============================================================================
# TEMPLATE USAGE EXAMPLES
# ============================================================================

"""
In your templates, you can use:

<!-- Check if user is authenticated -->
{% if user.is_authenticated %}
    <a href="{% url 'dashboard' %}">Dashboard</a>
{% endif %}

<!-- Check specific permission -->
{% if perms.properties.add_property %}
    <a href="{% url 'property_create' %}" class="btn btn-primary">Add Property</a>
{% endif %}

<!-- Check if user is superuser -->
{% if user.is_superuser %}
    <a href="{% url 'admin:index' %}">Admin Panel</a>
{% endif %}

<!-- Use context variables passed from view -->
{% if can_edit %}
    <button class="btn btn-warning">Edit</button>
{% endif %}

{% if can_delete %}
    <button class="btn btn-danger">Delete</button>
{% endif %}

<!-- Show content based on role -->
{% if user_role == 'Admin' %}
    <div class="admin-panel">
        <!-- Admin-only content -->
    </div>
{% elif user_role == 'Manager' %}
    <div class="manager-panel">
        <!-- Manager content -->
    </div>
{% endif %}

<!-- Check approval status -->
{% if user.profile.is_approved %}
    <p class="text-success">✓ Account Approved</p>
{% else %}
    <p class="text-warning">⏳ Pending Approval</p>
{% endif %}
"""


# ============================================================================
# NOTES
# ============================================================================

"""
DECORATOR ORDER MATTERS!
Always place decorators in this order (top to bottom):

1. @login_required  (if needed, though middleware handles this)
2. @role_required
3. @permission_required
4. @approved_user_required
5. @owner_or_admin_required
6. Your view function

MIDDLEWARE VS DECORATORS:
- Middleware: Global protection for all URLs
- Decorators: Additional view-specific protection
- Use both for defense in depth

PERFORMANCE:
- Middleware checks run on EVERY request
- Keep middleware checks fast and efficient
- Use decorators for complex permission logic
- Cache permission results when possible

SECURITY BEST PRACTICES:
1. Never trust client-side checks alone
2. Always validate permissions server-side
3. Use HTTPS in production
4. Log permission denials for security audits
5. Regularly review and update permissions
6. Use Django's permission system when possible
7. Create custom permissions for specific features
"""
