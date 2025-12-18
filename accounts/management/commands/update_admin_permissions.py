from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission


class Command(BaseCommand):
    help = 'Update existing Admin roles to have all permissions'

    def handle(self, *args, **options):
        self.stdout.write('Updating Admin roles to have all permissions...')
        
        # Find all Admin roles
        admin_roles = CustomRole.objects.filter(
            name__icontains='admin'
        ).exclude(
            name__icontains='property'
        )
        
        if not admin_roles.exists():
            self.stdout.write(
                self.style.WARNING('No Admin roles found. Create an Admin role first.')
            )
            return
        
        # Get all permissions
        all_permissions = Permission.objects.all()
        all_navigation_items = NavigationItem.objects.filter(is_active=True)
        
        updated_count = 0
        
        for role in admin_roles:
            self.stdout.write(f'Updating role: {role.name}')
            
            # Assign all permissions
            role.permissions.set(all_permissions)
            
            # Assign all navigation permissions
            for nav_item in all_navigation_items:
                RoleNavigationPermission.objects.get_or_create(
                    role=role,
                    navigation_item=nav_item,
                    defaults={'can_access': True}
                )
            
            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✅ Updated {role.name} with {all_permissions.count()} permissions and {all_navigation_items.count()} navigation items')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully updated {updated_count} Admin role(s) with all permissions!')
        )
