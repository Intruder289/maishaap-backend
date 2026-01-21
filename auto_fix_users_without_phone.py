#!/usr/bin/env python
"""
Automatically fix existing users without phone numbers
Sets placeholder phone numbers that users must update later
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile

print("=" * 80)
print("AUTO-FIXING USERS WITHOUT PHONE NUMBERS")
print("=" * 80)
print()

# Find users without phone
profiles_without_phone = Profile.objects.filter(phone__isnull=True) | Profile.objects.filter(phone='')
count = profiles_without_phone.count()

if count == 0:
    print("[OK] No users without phone numbers found!")
    print("Migration can proceed safely.")
    sys.exit(0)

print(f"[INFO] Found {count} user(s) without phone numbers")
print("Setting placeholder phone numbers...")
print()

updated_count = 0
for profile in profiles_without_phone:
    # Generate placeholder: +2557000000{user_id}
    placeholder = f"+2557000000{profile.user_id:03d}"
    
    # Ensure uniqueness
    counter = 1
    original_placeholder = placeholder
    while Profile.objects.filter(phone=placeholder).exclude(id=profile.id).exists():
        placeholder = f"+2557000000{profile.user_id:03d}{counter:02d}"
        counter += 1
        if counter > 99:  # Safety limit
            placeholder = f"+2557000000{profile.user_id}"
            break
    
    profile.phone = placeholder
    profile.save()
    updated_count += 1
    
    print(f"[UPDATED] {profile.user.username}: {placeholder}")

print()
print(f"[DONE] Updated {updated_count} user(s) with placeholder phone numbers")
print()
print("IMPORTANT:")
print("  - These are placeholder phone numbers")
print("  - Users MUST update their phone numbers in their profile")
print("  - Placeholder format: +2557000000XXX")
print()
print("Migration can now proceed safely.")
print()
