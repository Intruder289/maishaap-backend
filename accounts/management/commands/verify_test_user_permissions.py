from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission, UserRole, Profile
from accounts.context_processors import user_has_navigation_permission
from accounts.templatetags.navigation_tags import has_nav_permission


class Command(BaseCommand):
    help = 'Verify that test user permissions are working correctly'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('VERIFYING TEST USER PERMISSIONS')
        self.stdout.write('=' * 60)
        
        try:
            # Get test user
            user = User.objects.get(username='testuser')
            self.stdout.write(f'\n[1/6] Found test user: {user.username}')
            self.stdout.write(f'   - Is Superuser: {user.is_superuser} (should be False)')
            self.stdout.write(f'   - Is Staff: {user.is_staff} (should be False)')
            self.stdout.write(f'   - Is Active: {user.is_active} (should be True)')
            
            if user.is_superuser:
                self.stdout.write(self.style.ERROR('   [ERROR] User is a superuser! Permissions will be bypassed.'))
                return
            
            # Check profile
            profile = Profile.objects.get(user=user)
            self.stdout.write(f'\n[2/6] Profile status:')
            self.stdout.write(f'   - Is Approved: {profile.is_approved} (should be True)')
            
            if not profile.is_approved:
                self.stdout.write(self.style.ERROR('   [ERROR] Profile is not approved!'))
            
            # Check role assignment
            user_roles = UserRole.objects.filter(user=user)
            self.stdout.write(f'\n[3/6] Role assignments:')
            for ur in user_roles:
                self.stdout.write(f'   - {ur.role.name}')
            
            if not user_roles.exists():
                self.stdout.write(self.style.ERROR('   [ERROR] No roles assigned!'))
                return
            
            # Check navigation permissions
            role = user_roles.first().role
            nav_permissions = RoleNavigationPermission.objects.filter(role=role)
            self.stdout.write(f'\n[4/6] Navigation permissions for role "{role.name}":')
            
            expected_nav = ['dashboard', 'property_list']
            found_nav = []
            for np in nav_permissions:
                nav_name = np.navigation_item.name
                found_nav.append(nav_name)
                status = '[OK]' if nav_name in expected_nav else '[EXTRA]'
                self.stdout.write(f'   {status} {nav_name}')
            
            # Verify expected permissions
            missing = [n for n in expected_nav if n not in found_nav]
            if missing:
                self.stdout.write(self.style.ERROR(f'   [ERROR] Missing permissions: {missing}'))
            else:
                self.stdout.write(self.style.SUCCESS('   [OK] All expected permissions found'))
            
            # Test permission checking functions
            self.stdout.write(f'\n[5/6] Testing permission check functions:')
            
            # Test dashboard permission
            has_dashboard = user_has_navigation_permission(user, 'dashboard')
            self.stdout.write(f'   - dashboard: {has_dashboard} (should be True)')
            if not has_dashboard:
                self.stdout.write(self.style.ERROR('     [ERROR] Dashboard permission check failed!'))
            
            # Test property_list permission
            has_property_list = user_has_navigation_permission(user, 'property_list')
            self.stdout.write(f'   - property_list: {has_property_list} (should be True)')
            if not has_property_list:
                self.stdout.write(self.style.ERROR('     [ERROR] Property list permission check failed!'))
            
            # Test restricted permission (should be False)
            has_user_management = user_has_navigation_permission(user, 'user_management')
            self.stdout.write(f'   - user_management: {has_user_management} (should be False)')
            if has_user_management:
                self.stdout.write(self.style.ERROR('     [ERROR] User management permission should NOT be granted!'))
            else:
                self.stdout.write(self.style.SUCCESS('     [OK] Correctly restricted'))
            
            # Test system permissions
            self.stdout.write(f'\n[6/6] Testing system permissions:')
            has_view_property = user.has_perm('properties.view_property')
            self.stdout.write(f'   - properties.view_property: {has_view_property} (should be True)')
            if not has_view_property:
                self.stdout.write(self.style.ERROR('     [ERROR] View property permission check failed!'))
            
            has_add_property = user.has_perm('properties.add_property')
            self.stdout.write(f'   - properties.add_property: {has_add_property} (should be False)')
            if has_add_property:
                self.stdout.write(self.style.ERROR('     [ERROR] Add property permission should NOT be granted!'))
            else:
                self.stdout.write(self.style.SUCCESS('     [OK] Correctly restricted'))
            
            # Summary
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('VERIFICATION COMPLETE!'))
            self.stdout.write('=' * 60)
            self.stdout.write('\nTEST USER IS READY FOR TESTING!')
            self.stdout.write('\nLogin credentials:')
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write('   Password: testpass123')
            self.stdout.write('\nExpected behavior:')
            self.stdout.write('   - Only Dashboard and Properties should be visible in menu')
            self.stdout.write('   - "Add Property" button should NOT appear')
            self.stdout.write('   - Accessing /roles/ should be blocked')
            self.stdout.write('=' * 60 + '\n')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test user not found! Run: python manage.py create_test_user_with_limited_permissions'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

