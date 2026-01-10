"""
Script to check users in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

print("=" * 60)
print("USERS IN DATABASE")
print("=" * 60)

users = User.objects.all().order_by('id')[:30]

if not users:
    print("No users found in database.")
else:
    print(f"\nTotal users found: {User.objects.count()}\n")
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Staff':<6} {'Superuser':<10} {'Active':<6} {'Role':<10}")
    print("-" * 100)
    
    for user in users:
        try:
            profile = user.profile
            role = profile.role if profile else "No profile"
        except Profile.DoesNotExist:
            role = "No profile"
        
        print(f"{user.id:<5} {user.username:<20} {user.email or 'N/A':<30} {str(user.is_staff):<6} {str(user.is_superuser):<10} {str(user.is_active):<6} {role:<10}")

print("\n" + "=" * 60)
print("USERS BY ROLE")
print("=" * 60)

# Get users by role
admin_users = User.objects.filter(is_staff=True, is_superuser=True)
owner_users = User.objects.filter(profile__role='owner')
tenant_users = User.objects.filter(profile__role='tenant')

print(f"\nAdmin/Superuser: {admin_users.count()}")
for u in admin_users[:5]:
    print(f"  - {u.username} ({u.email})")

print(f"\nOwners: {owner_users.count()}")
for u in owner_users[:5]:
    print(f"  - {u.username} ({u.email})")

print(f"\nTenants: {tenant_users.count()}")
for u in tenant_users[:5]:
    print(f"  - {u.username} ({u.email})")

print("\n" + "=" * 60)
print("NOTE: Passwords are hashed and cannot be retrieved.")
print("To test login, you need to know the actual password or reset it.")
print("=" * 60)
