#!/usr/bin/env python
"""
Script to fix existing users without phone numbers
This should be run before applying the migration that makes phone mandatory
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from django.contrib.auth.models import User

print("=" * 80)
print("FIXING EXISTING USERS WITHOUT PHONE NUMBERS")
print("=" * 80)
print()

# Find users without phone
profiles_without_phone = Profile.objects.filter(phone__isnull=True) | Profile.objects.filter(phone='')
count = profiles_without_phone.count()

if count == 0:
    print("[OK] No users without phone numbers found!")
    print("You can proceed with the migration.")
    sys.exit(0)

print(f"[WARNING] Found {count} user(s) without phone numbers:")
print()

for profile in profiles_without_phone:
    print(f"User: {profile.user.username}")
    print(f"  Email: {profile.user.email}")
    print(f"  Full Name: {profile.user.get_full_name()}")
    print(f"  Current Phone: {profile.phone or 'NOT SET'}")
    print()

print("=" * 80)
print("OPTIONS")
print("=" * 80)
print()
print("You have two options:")
print()
print("OPTION 1: Set a default phone number for these users")
print("  - Use email or username to generate a placeholder")
print("  - Users will need to update their phone later")
print()
print("OPTION 2: Delete these users (if they're test accounts)")
print("  - Only if these are test/development accounts")
print("  - NOT recommended for production data")
print()
print("OPTION 3: Manually update each user's phone")
print("  - Best option for production")
print("  - Update phone numbers in admin panel or database")
print()

response = input("Do you want to set placeholder phone numbers? (yes/no): ").strip().lower()

if response == 'yes':
    print()
    print("Setting placeholder phone numbers...")
    print()
    
    for profile in profiles_without_phone:
        # Generate placeholder: use username + a suffix
        # Format: +255700000001, +255700000002, etc.
        placeholder = f"+2557000000{profile.user.id:03d}"
        
        # Check if placeholder already exists
        while Profile.objects.filter(phone=placeholder).exclude(id=profile.id).exists():
            placeholder = f"+2557000000{profile.user.id:03d}"
        
        profile.phone = placeholder
        profile.save()
        
        print(f"[UPDATED] {profile.user.username}: {placeholder}")
        print(f"  NOTE: User must update this phone number!")
    
    print()
    print("[DONE] All users now have phone numbers (placeholders)")
    print("Users should update their phone numbers in their profile.")
else:
    print()
    print("[SKIPPED] No changes made.")
    print("Please manually update phone numbers before running migration.")
    print()

print("=" * 80)
