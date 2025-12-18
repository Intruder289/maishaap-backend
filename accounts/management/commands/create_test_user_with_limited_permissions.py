from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission, UserRole, Profile
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Create a test user with limited permissions for testing the permission system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testuser',
            help='Username for the test user (default: testuser)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Password for the test user (default: testpass123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='testuser@example.com',
            help='Email for the test user'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        self.stdout.write('=' * 60)
        self.stdout.write('Creating Test User with Limited Permissions')
        self.stdout.write('=' * 60)
        
        # Step 1: Ensure navigation items exist
        self.stdout.write('\n[1/5] Checking navigation items...')
        nav_count = NavigationItem.objects.filter(is_active=True).count()
        if nav_count == 0:
            self.stdout.write(
                self.style.WARNING('[WARNING] No navigation items found! Running populate_navigation...')
            )
            from django.core.management import call_command
            call_command('populate_navigation')
            nav_count = NavigationItem.objects.filter(is_active=True).count()
            self.stdout.write(
                self.style.SUCCESS(f'Created {nav_count} navigation items')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Found {nav_count} navigation items')
            )
        
        # Step 2: Create or get the limited test role
        self.stdout.write('\n[2/5] Creating "Test Limited Role"...')
        role, created = CustomRole.objects.get_or_create(
            name='Test Limited Role',
            defaults={
                'description': 'Test role with limited permissions for testing the permission system'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created "Test Limited Role"'))
        else:
            self.stdout.write(self.style.WARNING('Role already exists, updating permissions...'))
            # Clear existing permissions
            role.permissions.clear()
            RoleNavigationPermission.objects.filter(role=role).delete()
        
        # Step 3: Assign limited system permissions
        self.stdout.write('\n[3/5] Assigning limited system permissions...')
        
        # Only assign view permissions for properties
        limited_permissions = Permission.objects.filter(
            codename__in=[
                'view_property',
                'view_booking',
            ],
            content_type__app_label='properties'
        )
        
        role.permissions.set(limited_permissions)
        self.stdout.write(
            self.style.SUCCESS(f'Assigned {limited_permissions.count()} system permissions')
        )
        self.stdout.write('  - properties.view_property')
        self.stdout.write('  - properties.view_booking')
        
        # Step 4: Assign limited navigation permissions
        self.stdout.write('\n[4/5] Assigning limited navigation permissions...')
        
        # Get only dashboard and property_list navigation items
        dashboard_nav = NavigationItem.objects.filter(name='dashboard', is_active=True).first()
        property_list_nav = NavigationItem.objects.filter(name='property_list', is_active=True).first()
        
        nav_items_assigned = []
        if dashboard_nav:
            RoleNavigationPermission.objects.get_or_create(
                role=role,
                navigation_item=dashboard_nav,
                defaults={'can_access': True}
            )
            nav_items_assigned.append('dashboard')
            self.stdout.write(self.style.SUCCESS('  [OK] Assigned: dashboard'))
        else:
            self.stdout.write(self.style.ERROR('  [ERROR] dashboard navigation item not found!'))
        
        if property_list_nav:
            RoleNavigationPermission.objects.get_or_create(
                role=role,
                navigation_item=property_list_nav,
                defaults={'can_access': True}
            )
            nav_items_assigned.append('property_list')
            self.stdout.write(self.style.SUCCESS('  [OK] Assigned: property_list'))
        else:
            self.stdout.write(self.style.ERROR('  [ERROR] property_list navigation item not found!'))
        
        if not nav_items_assigned:
            self.stdout.write(
                self.style.ERROR('[ERROR] No navigation items assigned! Please run: python manage.py populate_navigation')
            )
            return
        
        # Step 5: Create test user
        self.stdout.write('\n[5/5] Creating test user...')
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'[WARNING] User "{username}" already exists. Deleting and recreating...')
            )
            User.objects.filter(username=username).delete()
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User',
            is_superuser=False,  # IMPORTANT: Not a superuser
            is_staff=False,      # Not staff either
            is_active=True
        )
        
        # Create profile and approve it
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'is_approved': True}
        )
        if not profile.is_approved:
            profile.is_approved = True
            profile.save()
        
        # Assign the limited role to the user
        UserRole.objects.get_or_create(
            user=user,
            role=role
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Assigned role: {role.name}'))
        self.stdout.write(self.style.SUCCESS(f'Profile approved: {profile.is_approved}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('TEST USER CREATED SUCCESSFULLY!'))
        self.stdout.write('=' * 60)
        self.stdout.write('\nTEST USER CREDENTIALS:')
        self.stdout.write(f'   Username: {self.style.SUCCESS(username)}')
        self.stdout.write(f'   Password: {self.style.SUCCESS(password)}')
        self.stdout.write(f'   Email: {email}')
        self.stdout.write(f'   Is Superuser: {self.style.ERROR("NO")} (Important!)')
        self.stdout.write(f'   Role: {role.name}')
        
        self.stdout.write('\nPERMISSIONS ASSIGNED:')
        self.stdout.write('   System Permissions:')
        for perm in limited_permissions:
            self.stdout.write(f'     - {perm.codename}')
        self.stdout.write('   Navigation Permissions:')
        for nav in nav_items_assigned:
            self.stdout.write(f'     - {nav}')
        
        self.stdout.write('\nEXPECTED BEHAVIOR WHEN LOGGED IN:')
        self.stdout.write('   [OK] Dashboard menu item should be visible')
        self.stdout.write('   [OK] Properties menu item should be visible')
        self.stdout.write('   [NO] Manage Properties should NOT be visible')
        self.stdout.write('   [NO] User Management should NOT be visible')
        self.stdout.write('   [NO] Maintenance should NOT be visible')
        self.stdout.write('   [NO] Complaints should NOT be visible')
        self.stdout.write('   [NO] "Add Property" button should NOT appear')
        self.stdout.write('   [NO] Accessing /roles/ should be blocked')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('TESTING INSTRUCTIONS:')
        self.stdout.write('=' * 60)
        self.stdout.write('1. Log out from your admin account')
        self.stdout.write(f'2. Log in with username: {username}')
        self.stdout.write(f'3. Use password: {password}')
        self.stdout.write('4. Verify the navigation menu shows only Dashboard and Properties')
        self.stdout.write('5. Check that action buttons are hidden')
        self.stdout.write('6. Try accessing /roles/ - should be blocked')
        self.stdout.write('=' * 60 + '\n')

