from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.models import CustomRole, RoleNavigationPermission, NavigationItem


class Command(BaseCommand):
    help = 'Add maintenance permissions to Test Limited Role'

    def handle(self, *args, **options):
        self.stdout.write('Adding maintenance permissions to Test Limited Role...')
        
        try:
            # Get the role
            role = CustomRole.objects.get(name='Test Limited Role')
            
            # Add system permission
            view_maintenance_perm = Permission.objects.filter(
                codename='view_maintenancerequest',
                content_type__app_label='maintenance'
            ).first()
            
            if view_maintenance_perm:
                if view_maintenance_perm not in role.permissions.all():
                    role.permissions.add(view_maintenance_perm)
                    self.stdout.write(self.style.SUCCESS('Added: maintenance.view_maintenancerequest'))
                else:
                    self.stdout.write('Already has: maintenance.view_maintenancerequest')
            else:
                self.stdout.write(self.style.ERROR('Permission not found: maintenance.view_maintenancerequest'))
            
            # Add navigation permissions
            # First, add the parent "maintenance" navigation item
            maintenance_nav = NavigationItem.objects.filter(name='maintenance', is_active=True).first()
            if maintenance_nav:
                RoleNavigationPermission.objects.get_or_create(
                    role=role,
                    navigation_item=maintenance_nav,
                    defaults={'can_access': True}
                )
                self.stdout.write(self.style.SUCCESS('Added navigation: maintenance'))
            else:
                self.stdout.write(self.style.ERROR('Navigation item not found: maintenance'))
            
            # Then, add the child "request_list" navigation item
            request_list_nav = NavigationItem.objects.filter(name='request_list', is_active=True).first()
            if request_list_nav:
                RoleNavigationPermission.objects.get_or_create(
                    role=role,
                    navigation_item=request_list_nav,
                    defaults={'can_access': True}
                )
                self.stdout.write(self.style.SUCCESS('Added navigation: request_list'))
            else:
                self.stdout.write(self.style.ERROR('Navigation item not found: request_list'))
            
            self.stdout.write(self.style.SUCCESS('\nMaintenance permissions added successfully!'))
            
        except CustomRole.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test Limited Role not found!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

