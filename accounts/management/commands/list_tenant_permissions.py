from django.core.management.base import BaseCommand
from accounts.models import CustomRole, RoleNavigationPermission, UserRole


class Command(BaseCommand):
    help = 'List all permissions assigned to Tenant role'

    def handle(self, *args, **options):
        try:
            tenant_role = CustomRole.objects.get(name='Tenant')
        except CustomRole.DoesNotExist:
            self.stdout.write(self.style.ERROR('Tenant role does not exist!'))
            return
        
        # Get all navigation permissions
        permissions = RoleNavigationPermission.objects.filter(
            role=tenant_role,
            can_access=True
        ).select_related('navigation_item').order_by(
            'navigation_item__order',
            'navigation_item__display_name'
        )
        
        # Get users with this role
        users_with_role = UserRole.objects.filter(role=tenant_role).select_related('user')
        
        # Display results
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('PERMISSIONS ASSIGNED TO TENANT ROLE')
        self.stdout.write('=' * 70)
        self.stdout.write(f'\nRole Name: {tenant_role.name}')
        self.stdout.write(f'Description: {tenant_role.description}')
        self.stdout.write(f'\nTotal Navigation Items Assigned: {permissions.count()}')
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('NAVIGATION ITEMS (Web Interface Access)')
        self.stdout.write('-' * 70)
        
        if permissions.count() == 0:
            self.stdout.write(self.style.WARNING('  No navigation items assigned!'))
            self.stdout.write('  Run: python manage.py assign_tenant_permissions')
        else:
            for perm in permissions:
                nav = perm.navigation_item
                parent_info = f" (under {nav.parent.display_name})" if nav.parent else ""
                self.stdout.write(f'  [{nav.order:2d}] {nav.display_name:40s} ({nav.name}){parent_info}')
        
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('MOBILE APP ACCESS')
        self.stdout.write('-' * 70)
        self.stdout.write('  [OK] Tenants can access ALL mobile app APIs if:')
        self.stdout.write('       - They have "Tenant" role (auto-assigned on mobile registration)')
        self.stdout.write('       - They are approved (is_approved=True)')
        self.stdout.write('       - They are authenticated (logged in via API)')
        self.stdout.write('  [INFO] No Navigation Items needed for mobile app access')
        
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('USERS WITH TENANT ROLE')
        self.stdout.write('-' * 70)
        self.stdout.write(f'Total Users: {users_with_role.count()}\n')
        
        if users_with_role.count() == 0:
            self.stdout.write(self.style.WARNING('  No users have Tenant role assigned'))
        else:
            for ur in users_with_role[:20]:
                profile = getattr(ur.user, 'profile', None)
                approved_status = '[APPROVED]' if profile and profile.is_approved else '[PENDING]'
                self.stdout.write(f'  {approved_status} {ur.user.username:20s} ({ur.user.email})')
            
            if users_with_role.count() > 20:
                self.stdout.write(f'  ... and {users_with_role.count() - 20} more users')
        
        self.stdout.write('\n' + '=' * 70 + '\n')

