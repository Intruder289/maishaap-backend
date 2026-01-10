#!/usr/bin/env python
"""Script to check user profile phone numbers"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from django.contrib.auth.models import User

print("=" * 60)
print("CHECKING USER PROFILE PHONE NUMBERS")
print("=" * 60)

# Check user "alfred"
try:
    user_alfred = User.objects.get(username='alfred')
    profile_alfred = Profile.objects.get(user=user_alfred)
    print(f"\nUser: alfred")
    print(f"  Full Name: {user_alfred.get_full_name()}")
    print(f"  Email: {user_alfred.email}")
    print(f"  Profile Phone: {profile_alfred.phone}")
except User.DoesNotExist:
    print("\nUser 'alfred' not found")
except Profile.DoesNotExist:
    print("\nUser 'alfred' has no profile")

# Check user with email admin@maisha.com
try:
    user_admin = User.objects.get(email='admin@maisha.com')
    profile_admin = Profile.objects.get(user=user_admin)
    print(f"\nUser with email admin@maisha.com:")
    print(f"  Username: {user_admin.username}")
    print(f"  Full Name: {user_admin.get_full_name()}")
    print(f"  Profile Phone: {profile_admin.phone}")
except User.DoesNotExist:
    print("\nUser with email 'admin@maisha.com' not found")
except Profile.DoesNotExist:
    print("\nUser with email 'admin@maisha.com' has no profile")

# Check all users with phone 0758285812
print(f"\n" + "=" * 60)
print("Users with phone number 0758285812:")
print("=" * 60)
profiles_0758 = Profile.objects.filter(phone='0758285812').select_related('user')
if profiles_0758.exists():
    for p in profiles_0758:
        print(f"\n  Username: {p.user.username}")
        print(f"  Full Name: {p.user.get_full_name()}")
        print(f"  Email: {p.user.email}")
        print(f"  Phone: {p.phone}")
else:
    print("  No users found with phone 0758285812")

# Check all users with phone 0788412511
print(f"\n" + "=" * 60)
print("Users with phone number 0788412511:")
print("=" * 60)
profiles_0788 = Profile.objects.filter(phone='0788412511').select_related('user')
if profiles_0788.exists():
    for p in profiles_0788:
        print(f"\n  Username: {p.user.username}")
        print(f"  Full Name: {p.user.get_full_name()}")
        print(f"  Email: {p.user.email}")
        print(f"  Phone: {p.phone}")
else:
    print("  No users found with phone 0788412511")

print("\n" + "=" * 60)
