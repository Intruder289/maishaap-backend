from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.models import CustomRole, RoleNavigationPermission, NavigationItem


class Command(BaseCommand):
    help = 'Fix maintenance permissions for all roles - ensures roles with navigation permission also have system permission'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('FIXING MAINTENANCE PERMISSIONS FOR ALL ROLES')
        self.stdout.write('=' * 60)
        
        # Get the required system permission
        view_maintenance_perm = Permission.objects.filter(
            codename='view_maintenancerequest',
            content_type__app_label='maintenance'
        ).first()
        
        if not view_maintenance_perm:
            self.stdout.write(self.style.ERROR('ERROR: maintenance.view_maintenancerequest permission not found!'))
            return
        
        # Get all roles that have maintenance navigation permission
        maintenance_nav_items = NavigationItem.objects.filter(
            name__in=['maintenance', 'request_list'],
            is_active=True
        )
        
        # Get role IDs that have these navigation permissions
        role_ids_with_nav = RoleNavigationPermission.objects.filter(
            navigation_item__in=maintenance_nav_items
        ).values_list('role_id', flat=True).distinct()
        
        roles_with_nav = CustomRole.objects.filter(id__in=role_ids_with_nav)
        
        self.stdout.write(f'\nFound {roles_with_nav.count()} roles with maintenance navigation permission')
        
        fixed_count = 0
        already_ok_count = 0
        
        for role in roles_with_nav:
            has_perm = view_maintenance_perm in role.permissions.all()
            
            if not has_perm:
                role.permissions.add(view_maintenance_perm)
                self.stdout.write(self.style.SUCCESS(f'  [FIXED] {role.name} - Added maintenance.view_maintenancerequest'))
                fixed_count += 1
            else:
                self.stdout.write(f'  [OK] {role.name} - Already has permission')
                already_ok_count += 1
        
        # Also ensure navigation permissions are complete
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('Checking navigation permissions...')
        
        nav_fixed_count = 0
        for role in roles_with_nav:
            # Check if role has both parent and child navigation items
            has_maintenance_nav = RoleNavigationPermission.objects.filter(
                role=role,
                navigation_item__name='maintenance',
                navigation_item__is_active=True
            ).exists()
            
            has_request_list_nav = RoleNavigationPermission.objects.filter(
                role=role,
                navigation_item__name='request_list',
                navigation_item__is_active=True
            ).exists()
            
            maintenance_nav_item = NavigationItem.objects.filter(name='maintenance', is_active=True).first()
            request_list_nav_item = NavigationItem.objects.filter(name='request_list', is_active=True).first()
            
            if maintenance_nav_item and not has_maintenance_nav:
                RoleNavigationPermission.objects.get_or_create(
                    role=role,
                    navigation_item=maintenance_nav_item,
                    defaults={'can_access': True}
                )
                self.stdout.write(self.style.SUCCESS(f'  [FIXED] {role.name} - Added maintenance navigation'))
                nav_fixed_count += 1
            
            if request_list_nav_item and not has_request_list_nav:
                RoleNavigationPermission.objects.get_or_create(
                    role=role,
                    navigation_item=request_list_nav_item,
                    defaults={'can_access': True}
                )
                self.stdout.write(self.style.SUCCESS(f'  [FIXED] {role.name} - Added request_list navigation'))
                nav_fixed_count += 1
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'  - Roles checked: {roles_with_nav.count()}')
        self.stdout.write(f'  - System permissions fixed: {fixed_count}')
        self.stdout.write(f'  - System permissions already OK: {already_ok_count}')
        self.stdout.write(f'  - Navigation permissions fixed: {nav_fixed_count}')
        self.stdout.write('=' * 60)
        
        if fixed_count > 0 or nav_fixed_count > 0:
            self.stdout.write(self.style.SUCCESS('\nAll maintenance permissions have been fixed!'))
        else:
            self.stdout.write('\nAll roles already have correct permissions.')

