#!/usr/bin/env python
"""Script to check user role details"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile, CustomRole, UserRole
from django.contrib.auth.models import User, Group

user = User.objects.get(username='alfred')
profile = Profile.objects.get(user=user)

print("=" * 60)
print(f"USER ROLE INFORMATION FOR: {user.username}")
print("=" * 60)

print(f"\nBasic Information:")
print(f"  Username: {user.username}")
print(f"  Full Name: {user.get_full_name()}")
print(f"  Email: {user.email}")
print(f"  Is Staff: {user.is_staff}")
print(f"  Is Superuser: {user.is_superuser}")

print(f"\nProfile Information:")
print(f"  Profile Role: {profile.role}")
print(f"  Is Approved: {profile.is_approved}")
if profile.role:
    print(f"  Role Display: {profile.get_primary_role()}")

print(f"\nCustom Roles Assigned:")
custom_roles = UserRole.objects.filter(user=user).select_related('role')
if custom_roles.exists():
    for user_role in custom_roles:
        print(f"  - {user_role.role.name}")
        if user_role.role.description:
            print(f"    Description: {user_role.role.description}")
        print(f"    Assigned at: {user_role.assigned_at}")
else:
    print("  No custom roles assigned")

print(f"\nDjango Groups:")
groups = user.groups.all()
if groups.exists():
    for group in groups:
        print(f"  - {group.name}")
else:
    print("  No groups assigned")

print(f"\nUser Permissions:")
permissions = user.user_permissions.all()
if permissions.exists():
    print(f"  Direct Permissions: {permissions.count()}")
    for perm in permissions[:5]:  # Show first 5
        print(f"    - {perm.codename}")
    if permissions.count() > 5:
        print(f"    ... and {permissions.count() - 5} more")
else:
    print("  No direct permissions")

# Check group permissions
group_permissions = set()
for group in groups:
    group_permissions.update(group.permissions.all())
if group_permissions:
    print(f"  Group Permissions: {len(group_permissions)}")
    for perm in list(group_permissions)[:5]:  # Show first 5
        print(f"    - {perm.codename}")
    if len(group_permissions) > 5:
        print(f"    ... and {len(group_permissions) - 5} more")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Primary Role: {profile.get_primary_role() or profile.role or 'None'}")
print(f"Custom Roles: {', '.join([ur.role.name for ur in custom_roles]) or 'None'}")
print(f"Django Groups: {', '.join([g.name for g in groups]) or 'None'}")
