"""
Script to set test passwords for users in the database
This will set passwords for admin, owner, and tenant users for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile

# Test password to set
TEST_PASSWORD = "test123456"

print("=" * 60)
print("SETTING TEST PASSWORDS")
print("=" * 60)

# Find or create test users
users_to_update = []

# Admin user
admin_user = User.objects.filter(username='admin_user', email='admin@maisha.com').first()
if admin_user:
    users_to_update.append(('Admin', admin_user))

# Owner users
owner_users = User.objects.filter(profile__role='owner')[:2]
for owner in owner_users:
    users_to_update.append(('Owner', owner))

# Tenant users
tenant_users = User.objects.filter(profile__role='tenant')[:2]
for tenant in tenant_users:
    users_to_update.append(('Tenant', tenant))

# Update passwords
print(f"\nSetting password '{TEST_PASSWORD}' for test users:\n")
for role, user in users_to_update:
    user.set_password(TEST_PASSWORD)
    user.save()
    print(f"[OK] {role:10} - Username: {user.username:20} Email: {user.email:30} Password: {TEST_PASSWORD}")

print("\n" + "=" * 60)
print("TEST CREDENTIALS FOR test_crud_operations.py")
print("=" * 60)
print("\nUpdate your test script with these credentials:\n")

if admin_user:
    print(f"TEST_ADMIN = {{")
    print(f'    "email": "{admin_user.email}",')
    print(f'    "password": "{TEST_PASSWORD}"')
    print(f"}}")

if owner_users:
    owner = owner_users[0]
    print(f"\nTEST_OWNER = {{")
    print(f'    "email": "{owner.email}",')
    print(f'    "password": "{TEST_PASSWORD}"')
    print(f"}}")

if tenant_users:
    tenant = tenant_users[0]
    print(f"\nTEST_TENANT = {{")
    print(f'    "email": "{tenant.email}",')
    print(f'    "password": "{TEST_PASSWORD}"')
    print(f"}}")

print("\n" + "=" * 60)
