from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission, UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Create an admin user with full navigation access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the admin user (default: admin)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@maisha.com',
            help='Email for the admin user (default: admin@maisha.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the admin user (default: admin123)',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Updating permissions...')
            )
            user = User.objects.get(username=username)
        else:
            # Create admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='System',
                last_name='Administrator',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {username}')
            )

        # Create or get Admin role
        admin_role, created = CustomRole.objects.get_or_create(
            name='System Administrator',
            defaults={
                'description': 'Full system administrator with access to all features and navigation tabs'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created "System Administrator" role')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Using existing "System Administrator" role')
            )

        # Add all permissions to admin role
        all_permissions = Permission.objects.all()
        admin_role.permissions.set(all_permissions)
        self.stdout.write(
            self.style.SUCCESS(f'Added {all_permissions.count()} permissions to admin role')
        )

        # Add all navigation items to admin role
        all_navigation_items = NavigationItem.objects.all()
        
        # Clear existing navigation permissions for this role
        RoleNavigationPermission.objects.filter(role=admin_role).delete()
        
        # Add all navigation permissions
        navigation_permissions = []
        for nav_item in all_navigation_items:
            navigation_permissions.append(
                RoleNavigationPermission(role=admin_role, navigation_item=nav_item)
            )
        
        RoleNavigationPermission.objects.bulk_create(navigation_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(f'Added {all_navigation_items.count()} navigation permissions to admin role')
        )

        # Assign admin role to user
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=admin_role,
            defaults={'assigned_by': user}  # Self-assigned for admin
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Assigned "System Administrator" role to {username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'User {username} already has "System Administrator" role')
            )

        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('ADMIN USER CREATED SUCCESSFULLY!'))
        self.stdout.write('='*50)
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'Role: System Administrator')
        self.stdout.write(f'Permissions: {all_permissions.count()} system permissions')
        self.stdout.write(f'Navigation Access: {all_navigation_items.count()} navigation tabs')
        self.stdout.write('='*50)
        self.stdout.write('\nYou can now:')
        self.stdout.write('1. Login with these credentials')
        self.stdout.write('2. Access all navigation tabs')
        self.stdout.write('3. Create roles and assign navigation permissions to other users')
        self.stdout.write('4. Manage all system features')