from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from accounts.models import CustomRole, UserRole, RoleNavigationPermission, NavigationItem
from django.db.models import Q


class Command(BaseCommand):
    help = 'Check and fix test user permissions and role assignments'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('CHECKING TEST USER PERMISSIONS')
        self.stdout.write('=' * 60)
        
        try:
            # Get test user
            user = User.objects.get(username='testuser')
            self.stdout.write(f'\n[1] User: {user.username}')
            self.stdout.write(f'   - Is Superuser: {user.is_superuser}')
            self.stdout.write(f'   - Is Active: {user.is_active}')
            
            # Check assigned roles
            user_roles = UserRole.objects.filter(user=user)
            self.stdout.write(f'\n[2] Assigned Roles: {user_roles.count()}')
            for ur in user_roles:
                self.stdout.write(f'   - {ur.role.name}')
            
            if not user_roles.exists():
                self.stdout.write(self.style.ERROR('   [ERROR] No roles assigned!'))
                # Try to assign Test Limited Role
                try:
                    role = CustomRole.objects.get(name='Test Limited Role')
                    UserRole.objects.get_or_create(user=user, role=role)
                    self.stdout.write(self.style.SUCCESS('   [FIXED] Assigned Test Limited Role'))
                except CustomRole.DoesNotExist:
                    self.stdout.write(self.style.ERROR('   [ERROR] Test Limited Role not found!'))
            else:
                # Check permissions for the first role
                role = user_roles.first().role
                self.stdout.write(f'\n[3] Checking Role: {role.name}')
                
                # Check navigation permissions
                nav_perms = RoleNavigationPermission.objects.filter(role=role)
                nav_names = [np.navigation_item.name for np in nav_perms]
                self.stdout.write(f'   Navigation Permissions: {len(nav_names)}')
                self.stdout.write(f'   - dashboard: {"[OK]" if "dashboard" in nav_names else "[MISSING]"}')
                self.stdout.write(f'   - property_list: {"[OK]" if "property_list" in nav_names else "[MISSING]"}')
                
                # Check system permissions
                sys_perms = role.permissions.all()
                sys_perm_codenames = [p.codename for p in sys_perms]
                self.stdout.write(f'\n   System Permissions: {len(sys_perm_codenames)}')
                
                # Check for property-related permissions
                property_perms = [p for p in sys_perm_codenames if 'property' in p.lower()]
                self.stdout.write(f'   Property-related permissions: {len(property_perms)}')
                for perm in property_perms:
                    self.stdout.write(f'     - {perm}')
                
                # Check if view_property exists
                has_view_property = 'view_property' in sys_perm_codenames
                self.stdout.write(f'   - view_property: {"[OK]" if has_view_property else "[MISSING]"}')
                
                if not has_view_property:
                    self.stdout.write(self.style.WARNING('\n   [WARNING] Missing properties.view_property permission!'))
                    self.stdout.write('   Adding properties.view_property permission...')
                    
                    try:
                        view_property_perm = Permission.objects.get(
                            codename='view_property',
                            content_type__app_label='properties'
                        )
                        role.permissions.add(view_property_perm)
                        self.stdout.write(self.style.SUCCESS('   [FIXED] Added properties.view_property'))
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.ERROR('   [ERROR] Permission not found!'))
                
                # Also check view_booking
                has_view_booking = 'view_booking' in sys_perm_codenames
                self.stdout.write(f'   - view_booking: {"[OK]" if has_view_booking else "[MISSING]"}')
                
                if not has_view_booking:
                    try:
                        view_booking_perm = Permission.objects.get(
                            codename='view_booking',
                            content_type__app_label='properties'
                        )
                        role.permissions.add(view_booking_perm)
                        self.stdout.write(self.style.SUCCESS('   [FIXED] Added properties.view_booking'))
                    except Permission.DoesNotExist:
                        pass
                
                # Check maintenance permissions
                has_view_maintenance = 'view_maintenancerequest' in sys_perm_codenames
                self.stdout.write(f'\n   Maintenance Permissions:')
                self.stdout.write(f'   - view_maintenancerequest: {"[OK]" if has_view_maintenance else "[MISSING]"}')
                
                if not has_view_maintenance:
                    try:
                        view_maintenance_perm = Permission.objects.get(
                            codename='view_maintenancerequest',
                            content_type__app_label='maintenance'
                        )
                        role.permissions.add(view_maintenance_perm)
                        self.stdout.write(self.style.SUCCESS('   [FIXED] Added maintenance.view_maintenancerequest'))
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.ERROR('   [ERROR] Permission not found!'))
                
                # Check if maintenance navigation permission exists
                has_maintenance_nav = 'maintenance' in nav_names or 'request_list' in nav_names
                self.stdout.write(f'\n   Navigation Permissions:')
                self.stdout.write(f'   - maintenance/request_list: {"[OK]" if has_maintenance_nav else "[MISSING]"}')
                
                if not has_maintenance_nav:
                    # Try to find maintenance navigation item
                    try:
                        maintenance_nav = NavigationItem.objects.filter(
                            Q(name='maintenance') | Q(name='request_list'),
                            is_active=True
                        ).first()
                        if maintenance_nav:
                            RoleNavigationPermission.objects.get_or_create(
                                role=role,
                                navigation_item=maintenance_nav,
                                defaults={'can_access': True}
                            )
                            self.stdout.write(self.style.SUCCESS(f'   [FIXED] Added navigation permission: {maintenance_nav.name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   [ERROR] Could not add navigation permission: {str(e)}'))
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('CHECK COMPLETE!'))
            self.stdout.write('=' * 60)
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test user not found!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

