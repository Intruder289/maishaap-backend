from django.core.management.base import BaseCommand
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Assign all permissions and navigation items to Admin role'

    def handle(self, *args, **options):
        self.stdout.write('Assigning all permissions to Admin role...')
        
        try:
            # Find Admin role (case-insensitive)
            admin_role = CustomRole.objects.filter(
                name__iexact='admin'
            ).first()
            
            if not admin_role:
                # Try other variations
                admin_role = CustomRole.objects.filter(
                    name__iexact='administrator'
                ).first()
            
            if not admin_role:
                self.stdout.write(
                    self.style.ERROR('Admin role not found! Please create it first.')
                )
                return
            
            self.stdout.write(f'Found Admin role: {admin_role.name}')
            
            # Assign all system permissions
            all_permissions = Permission.objects.all()
            admin_role.permissions.set(all_permissions)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Assigned {all_permissions.count()} system permissions')
            )
            
            # Assign all navigation permissions
            all_navigation_items = NavigationItem.objects.filter(is_active=True)
            assigned_count = 0
            for nav_item in all_navigation_items:
                RoleNavigationPermission.objects.get_or_create(
                    role=admin_role,
                    navigation_item=nav_item,
                    defaults={'can_access': True}
                )
                assigned_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Assigned {assigned_count} navigation permissions')
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully assigned ALL permissions to "{admin_role.name}" role!'
                )
            )
            self.stdout.write(
                '\nNote: Superusers bypass permission checks, but this ensures the Admin role'
                '\nhas all permissions for non-superuser users assigned to it.'
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )

