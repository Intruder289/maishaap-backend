from accounts.models import NavigationItem, RoleNavigationPermission, UserRole, Profile, Notification

def navigation_permissions(request):
    """
    Context processor to provide navigation permissions and user profile for the current user
    """
    if not request.user.is_authenticated:
        return {
            'user_navigation_permissions': [],
            'user_navigation_permissions_set': set(),
            'user_has_all_navigation': False,
            'profile': None,
            'notification_count': 0
        }
    
    # Get or create user profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get notification count for admins
    notification_count = 0
    if request.user.is_superuser or request.user.is_staff:
        notification_count = Notification.get_unread_count(request.user)
    
    # If user is superuser, give access to all navigation items
    if request.user.is_superuser:
        all_nav_items = NavigationItem.objects.filter(is_active=True)
        permitted_nav_names = list(all_nav_items.values_list('name', flat=True))
        return {
            'user_navigation_permissions': permitted_nav_names,
            'user_navigation_permissions_set': set(permitted_nav_names),
            'user_has_all_navigation': True,
            'profile': profile,
            'notification_count': notification_count
        }
    
    # Get user's roles
    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
    
    # Get navigation permissions for all user's roles
    navigation_permissions = RoleNavigationPermission.objects.filter(
        role__in=[ur.role for ur in user_roles]
    ).select_related('navigation_item')
    
    # Extract navigation item names
    permitted_nav_names = list(navigation_permissions.values_list('navigation_item__name', flat=True))
    
    return {
        'user_navigation_permissions': permitted_nav_names,
        'user_navigation_permissions_set': set(permitted_nav_names),
        'user_has_all_navigation': False,
        'profile': profile,
        'notification_count': notification_count
    }


def user_has_navigation_permission(user, nav_name):
    """
    Helper function to check if user has permission for a specific navigation item
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Get user's roles
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    
    # Check if user has permission for this navigation item
    return RoleNavigationPermission.objects.filter(
        role__in=[ur.role for ur in user_roles],
        navigation_item__name=nav_name
    ).exists()


def user_has_any_child_permission(user, parent_nav_name):
    """
    Helper function to check if user has permission for any child navigation item
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    try:
        parent_item = NavigationItem.objects.get(name=parent_nav_name, is_active=True)
        child_items = NavigationItem.objects.filter(parent=parent_item, is_active=True)
        
        if not child_items.exists():
            return False
        
        # Get user's roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        
        # Check if user has permission for any child item
        return RoleNavigationPermission.objects.filter(
            role__in=[ur.role for ur in user_roles],
            navigation_item__in=child_items
        ).exists()
    except NavigationItem.DoesNotExist:
        return False