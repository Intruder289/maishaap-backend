from django.core.management.base import BaseCommand
from accounts.models import NavigationItem, RoleNavigationPermission, CustomRole


class Command(BaseCommand):
    help = 'Add Owner Management navigation item to the navigation system'

    def handle(self, *args, **options):
        self.stdout.write('Adding Owner Management to navigation...')
        
        # Get or create the parent "User Management" navigation item
        try:
            user_management = NavigationItem.objects.get(name='user_management')
        except NavigationItem.DoesNotExist:
            self.stdout.write(self.style.ERROR('User Management navigation item not found. Please run populate_navigation first.'))
            return
        
        # Create or get the Owner Management navigation item
        owner_list, created = NavigationItem.objects.get_or_create(
            name='owner_list',
            defaults={
                'display_name': 'Owner Management',
                'url_name': 'accounts:owner_list',
                'icon': '',
                'order': 2,  # After "All Users" (order 1)
                'parent': user_management,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'[OK] Created navigation item: {owner_list.display_name}'))
        else:
            # Update existing item
            owner_list.display_name = 'Owner Management'
            owner_list.url_name = 'accounts:owner_list'
            owner_list.order = 2
            owner_list.parent = user_management
            owner_list.is_active = True
            owner_list.save()
            self.stdout.write(self.style.SUCCESS(f'[OK] Updated navigation item: {owner_list.display_name}'))
        
        # Assign navigation permission to Admin role (if exists)
        try:
            admin_role = CustomRole.objects.get(name='Admin')
            RoleNavigationPermission.objects.get_or_create(
                role=admin_role,
                navigation_item=owner_list,
                defaults={'can_access': True}
            )
            self.stdout.write(self.style.SUCCESS('[OK] Assigned Owner Management permission to Admin role'))
        except CustomRole.DoesNotExist:
            self.stdout.write(self.style.WARNING('Admin role not found. Skipping permission assignment.'))
        
        # Also assign to all roles that have user_management permission
        roles_with_user_mgmt = RoleNavigationPermission.objects.filter(
            navigation_item=user_management
        ).values_list('role', flat=True).distinct()
        
        for role_id in roles_with_user_mgmt:
            role = CustomRole.objects.get(id=role_id)
            RoleNavigationPermission.objects.get_or_create(
                role=role,
                navigation_item=owner_list,
                defaults={'can_access': True}
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Assigned Owner Management permission to {role.name} role'))
        
        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Owner Management navigation item added successfully!'))
        self.stdout.write('\nTo see it in the sidebar:')
        self.stdout.write('1. Make sure you have Admin role or role with User Management permission')
        self.stdout.write('2. Refresh your browser')
        self.stdout.write('3. Look under "User Management" menu in the sidebar')

