from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission, UserRole
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users with different roles for testing navigation permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for the test user (default: testuser)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='testuser@example.com',
            help='Email for the test user (default: testuser@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test user (default: testpass123)'
        )
        parser.add_argument(
            '--role',
            type=str,
            default='Manager',
            help='Role name to create and assign (default: Manager)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        role_name = options['role']

        try:
            with transaction.atomic():
                # Create or get the test user
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': 'Test',
                        'last_name': 'User',
                        'is_active': True,
                    }
                )

                if created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created new user: {username}')
                    )
                else:
                    # Update password for existing user
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.WARNING(f'⚠ User {username} already exists, updated password')
                    )

                # Create or get the test role
                role, role_created = CustomRole.objects.get_or_create(
                    name=role_name,
                    defaults={
                        'description': f'Test role for {role_name} with limited navigation access'
                    }
                )

                if role_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created new role: {role_name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Role {role_name} already exists')
                    )

                # Assign some navigation permissions to the role
                # Get some navigation items to assign
                navigation_items = NavigationItem.objects.filter(
                    display_name__in=[
                        'Dashboard',
                        'Houses',
                        'User Management',
                        'Rent',
                        'Payment'
                    ]
                )

                # Clear existing navigation permissions for this role
                RoleNavigationPermission.objects.filter(role=role).delete()

                # Assign navigation permissions
                permissions_created = 0
                for nav_item in navigation_items:
                    permission, created = RoleNavigationPermission.objects.get_or_create(
                        role=role,
                        navigation_item=nav_item
                    )
                    if created:
                        permissions_created += 1

                self.stdout.write(
                    self.style.SUCCESS(f'✓ Assigned {permissions_created} navigation permissions to {role_name}')
                )

                # Assign the role to the user
                # Clear existing roles
                UserRole.objects.filter(user=user).delete()
                
                # Create new role assignment
                user_role, created = UserRole.objects.get_or_create(
                    user=user,
                    role=role,
                    defaults={'assigned_by': None}  # System assigned
                )

                self.stdout.write(
                    self.style.SUCCESS(f'✓ Assigned role "{role_name}" to user "{username}"')
                )

                # Display summary
                self.stdout.write('\n' + '='*50)
                self.stdout.write(self.style.SUCCESS('TEST USER CREATED SUCCESSFULLY!'))
                self.stdout.write('='*50)
                self.stdout.write(f'Username: {username}')
                self.stdout.write(f'Email: {email}')
                self.stdout.write(f'Password: {password}')
                self.stdout.write(f'Role: {role_name}')
                self.stdout.write(f'Navigation permissions: {permissions_created} items')
                self.stdout.write('\nAvailable navigation items for this user:')
                
                for nav_item in navigation_items:
                    self.stdout.write(f'  • {nav_item.display_name}')
                
                self.stdout.write('\n' + self.style.WARNING('You can now login with these credentials to test navigation permissions!'))
                self.stdout.write('='*50)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating test user: {str(e)}')
            )
            raise e