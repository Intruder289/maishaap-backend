from django import template
from accounts.models import NavigationItem, RoleNavigationPermission, UserRole

register = template.Library()

@register.simple_tag
def test_tag():
    """Simple test tag to verify template tags are working"""
    return "Template tags working!"

@register.filter
def has_nav_permission(user, nav_name):
    """
    Template filter to check if user has permission for a specific navigation item
    Usage: {% if user|has_nav_permission:"dashboard" %}
    
    For property owners, automatically grants access to property management sections
    if they own properties of that type (hotel_management, venue_management, etc.)
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Get user's roles
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    
    # Check if user has permission for this navigation item via role permissions
    has_role_permission = RoleNavigationPermission.objects.filter(
        role__in=[ur.role for ur in user_roles],
        navigation_item__name=nav_name
    ).exists()
    
    if has_role_permission:
        return True
    
    # AUTO-GRANT: For property owners, automatically show property management sections
    # if they own properties of that type
    if not (user.is_staff or user.is_superuser):
        # Check if user is a Property Owner
        is_property_owner = user_roles.filter(
            role__name__in=['Property Owner', 'Property owner']
        ).exists()
        
        # Also check profile role for backward compatibility
        if not is_property_owner and hasattr(user, 'profile'):
            is_property_owner = user.profile.role == 'owner'
        
        if is_property_owner:
            # Check if this is a property management navigation item
            property_management_map = {
                'hotel_management': 'hotel',
                'lodge_management': 'lodge',
                'venue_management': 'venue',
                'house_management': 'house',
            }
            
            if nav_name in property_management_map:
                property_type_name = property_management_map[nav_name]
                try:
                    from properties.models import Property
                    # Check if owner has properties of this type
                    has_properties = Property.objects.filter(
                        owner=user,
                        property_type__name__iexact=property_type_name
                    ).exists()
                    if has_properties:
                        return True
                except ImportError:
                    pass  # Properties app not available
    
    return False

@register.simple_tag
def user_nav_permissions(user):
    """
    Template tag to get all navigation permissions for a user
    Usage: {% user_nav_permissions user as nav_perms %}
    """
    if not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return list(NavigationItem.objects.filter(is_active=True).values_list('name', flat=True))
    
    # Get user's roles
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    
    # Get navigation permissions for all user's roles
    navigation_permissions = RoleNavigationPermission.objects.filter(
        role__in=[ur.role for ur in user_roles]
    ).select_related('navigation_item')
    
    return list(navigation_permissions.values_list('navigation_item__name', flat=True))


@register.filter
def has_any_child_permission(user, parent_nav_name):
    """
    Template filter to check if user has permission for any child navigation item
    Usage: {% if user|has_any_child_permission:"properties" %}
    
    For property owners, automatically grants access if they own any properties
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    try:
        from accounts.models import NavigationItem, RoleNavigationPermission, UserRole
        
        parent_item = NavigationItem.objects.get(name=parent_nav_name, is_active=True)
        child_items = NavigationItem.objects.filter(parent=parent_item, is_active=True)
        
        if not child_items.exists():
            return False
        
        # Get user's roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        
        # Check if user has permission for any child item via role permissions
        has_role_permission = RoleNavigationPermission.objects.filter(
            role__in=[ur.role for ur in user_roles],
            navigation_item__in=child_items
        ).exists()
        
        if has_role_permission:
            return True
        
        # AUTO-GRANT: For property owners, automatically show "Manage Properties" 
        # if they own any properties
        if not (user.is_staff or user.is_superuser):
            # Check if user is a Property Owner
            is_property_owner = user_roles.filter(
                role__name__in=['Property Owner', 'Property owner']
            ).exists()
            
            # Also check profile role for backward compatibility
            if not is_property_owner and hasattr(user, 'profile'):
                is_property_owner = user.profile.role == 'owner'
            
            if is_property_owner and parent_nav_name == 'manage_properties':
                try:
                    from properties.models import Property
                    # Check if owner has any properties
                    has_any_properties = Property.objects.filter(owner=user).exists()
                    if has_any_properties:
                        return True
                except ImportError:
                    pass  # Properties app not available
        
        return False
    except NavigationItem.DoesNotExist:
        return False