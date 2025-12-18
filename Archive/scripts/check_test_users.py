"""Check for approved users in the database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile, CustomRole, UserRole
from django.utils import timezone

# Find all approved users
approved_users = User.objects.filter(profile__is_approved=True)

if approved_users.exists():
    print("\n[INFO] Approved users found:")
    print("="*80)
    for user in approved_users:
        print(f"\nUsername: {user.username}")
        print(f"Email: {user.email}")
        print(f"First Name: {user.first_name}")
        print(f"Last Name: {user.last_name}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Approved: {user.profile.is_approved}")
        print(f"Role: {user.profile.get_role_display()}")
else:
    print("\n[WARNING] No approved users found")
    print("\nCreating or updating test user for API testing...")
    
    # Get or create test user
    test_user, created = User.objects.get_or_create(
        username='api_test_user',
        defaults={
            'email': 'api_test@example.com',
            'first_name': 'API',
            'last_name': 'Test',
            'is_active': True
        }
    )
    
    # Set password
    test_user.set_password('test123')
    test_user.is_active = True
    test_user.save()
    
    # Create or update profile
    profile, profile_created = Profile.objects.get_or_create(
        user=test_user,
        defaults={
            'phone': '+254712345678',
            'role': 'tenant',
            'is_approved': True,
            'approved_at': timezone.now()
        }
    )
    
    # Approve if not already approved
    if not profile.is_approved:
        profile.is_approved = True
        profile.approved_at = timezone.now()
        profile.save()
    
    # Assign Tenant role
    try:
        tenant_role = CustomRole.objects.get(name='Tenant')
    except CustomRole.DoesNotExist:
        # Create Tenant role if it doesn't exist
        tenant_role = CustomRole.objects.create(
            name='Tenant',
            description='Property tenant with mobile app access'
        )
    
    # Assign role to user if not already assigned
    if not UserRole.objects.filter(user=test_user, role=tenant_role).exists():
        UserRole.objects.create(user=test_user, role=tenant_role)
    
    print("[SUCCESS] Test user ready:")
    print(f"  Username: {test_user.username}")
    print(f"  Email: {test_user.email}")
    print(f"  Password: test123")
    print(f"  Is Approved: {profile.is_approved}")
    print(f"  Role: {tenant_role.name}")

print("\n" + "="*80)

