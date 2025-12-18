from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from accounts.models import Profile, CustomRole, UserRole


class Command(BaseCommand):
    help = 'Create sample users for the Maisha Backend application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-only',
            action='store_true',
            help='Create only admin user',
        )
        parser.add_argument(
            '--custom-user',
            nargs=5,
            metavar=('USERNAME', 'EMAIL', 'FIRST_NAME', 'LAST_NAME', 'ROLE'),
            help='Create a custom user with specified details',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Creating users for Maisha Backend...')
        )

        # Create custom roles first
        self.create_custom_roles()

        if options['admin_only']:
            self.create_admin_user()
        elif options['custom_user']:
            username, email, first_name, last_name, role = options['custom_user']
            self.create_custom_user(username, email, first_name, last_name, role)
        else:
            self.create_all_sample_users()

        self.display_login_info()

    def create_custom_roles(self):
        """Create custom roles for the system"""
        roles_data = [
            {'name': 'Admin', 'description': 'Full system administrator'},
            {'name': 'Property Manager', 'description': 'Manages properties and tenants'},
            {'name': 'Property Owner', 'description': 'Owns properties and views reports'},
            {'name': 'Tenant', 'description': 'Property tenant with limited access'},
            {'name': 'Maintenance Staff', 'description': 'Handles maintenance requests'},
        ]

        for role_data in roles_data:
            role, created = CustomRole.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(f"✅ Created role: {role.name}")

    def create_admin_user(self):
        """Create only the admin user"""
        self.create_user_with_role(
            username='admin',
            email='admin@maisha.com',
            first_name='Admin',
            last_name='User',
            password='admin123!',
            role='Admin',
            is_superuser=True,
            is_staff=True,
            phone='+254700000000'
        )

    def create_all_sample_users(self):
        """Create all sample users"""
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@maisha.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'password': 'admin123!',
                'role': 'Admin',
                'is_superuser': True,
                'is_staff': True,
                'phone': '+254700000000'
            },
            {
                'username': 'manager1',
                'email': 'manager@maisha.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'password': 'manager123!',
                'role': 'Property Manager',
                'is_superuser': False,
                'is_staff': True,
                'phone': '+254700000001'
            },
            {
                'username': 'owner1',
                'email': 'owner@maisha.com',
                'first_name': 'Sarah',
                'last_name': 'Owner',
                'password': 'owner123!',
                'role': 'Property Owner',
                'is_superuser': False,
                'is_staff': False,
                'phone': '+254700000002'
            },
            {
                'username': 'tenant1',
                'email': 'tenant1@maisha.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'password': 'tenant123!',
                'role': 'Tenant',
                'is_superuser': False,
                'is_staff': False,
                'phone': '+254700000003'
            },
            {
                'username': 'tenant2',
                'email': 'tenant2@maisha.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'tenant123!',
                'role': 'Tenant',
                'is_superuser': False,
                'is_staff': False,
                'phone': '+254700000004'
            }
        ]

        for user_data in users_data:
            self.create_user_with_role(**user_data)

    def create_custom_user(self, username, email, first_name, last_name, role):
        """Create a custom user"""
        self.create_user_with_role(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password='password123!',
            role=role,
            is_superuser=False,
            is_staff=False,
            phone='+254700000999'
        )

    def create_user_with_role(self, username, email, first_name, last_name, 
                             password, role, is_superuser=False, is_staff=False, 
                             phone=''):
        """Create a user with profile and role"""
        try:
            with transaction.atomic():
                # Create or get user
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'is_superuser': is_superuser,
                        'is_staff': is_staff,
                        'is_active': True
                    }
                )

                if created:
                    # Set password
                    user.set_password(password)
                    user.save()

                    # Create profile
                    profile, _ = Profile.objects.get_or_create(
                        user=user,
                        defaults={'phone': phone}
                    )

                    # Assign role
                    try:
                        custom_role = CustomRole.objects.get(name=role)
                        UserRole.objects.get_or_create(
                            user=user,
                            role=custom_role
                        )
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Created user: {username} ({email}) - {role}"
                            )
                        )
                    except CustomRole.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️ Role '{role}' not found for {username}"
                            )
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"📝 User already exists: {username}")
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creating user {username}: {str(e)}")
            )

    def display_login_info(self):
        """Display login information"""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(
            self.style.SUCCESS("🎉 User creation completed!")
        )
        self.stdout.write("="*60)
        self.stdout.write("LOGIN CREDENTIALS:")
        self.stdout.write("="*60)
        
        users = User.objects.filter(is_active=True).order_by('date_joined')
        
        for user in users:
            try:
                profile = user.profile
                roles = profile.get_user_roles()
                role_names = [role.name for role in roles] if roles.exists() else ['No role']
                
                self.stdout.write(f"\n👤 {user.get_full_name()} ({user.username})")
                self.stdout.write(f"   📧 Email: {user.email}")
                self.stdout.write(f"   🎭 Role: {', '.join(role_names)}")
                self.stdout.write(f"   📱 Phone: {profile.phone}")
                
                if user.username == 'admin':
                    self.stdout.write(f"   🔐 Password: admin123!")
                elif 'manager' in user.username:
                    self.stdout.write(f"   🔐 Password: manager123!")
                elif 'owner' in user.username:
                    self.stdout.write(f"   🔐 Password: owner123!")
                elif 'tenant' in user.username:
                    self.stdout.write(f"   🔐 Password: tenant123!")
                else:
                    self.stdout.write(f"   🔐 Password: password123!")
                    
            except Profile.DoesNotExist:
                self.stdout.write(f"\n👤 {user.get_full_name()} ({user.username})")
                self.stdout.write(f"   📧 Email: {user.email}")
                self.stdout.write(f"   ⚠️ No profile found")

        self.stdout.write("\n" + "="*60)
        self.stdout.write("LOGIN URL: http://127.0.0.1:8000/accounts/login/")
        self.stdout.write("="*60)