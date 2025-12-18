#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User

print("=== USER CREDENTIALS CHECK ===")
users = User.objects.all()
print(f"Total Users: {users.count()}")
for user in users:
    print(f"- {user.username} (ID: {user.id}, Active: {user.is_active})")

# Test password for admin user
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"\nAdmin user found: {admin_user.username}")
    print(f"Admin user active: {admin_user.is_active}")
    print(f"Admin user has password: {bool(admin_user.password)}")
else:
    print("\nNo admin user found")

# Test password for property_manager1
pm_user = User.objects.filter(username='property_manager1').first()
if pm_user:
    print(f"\nProperty Manager user found: {pm_user.username}")
    print(f"Property Manager user active: {pm_user.is_active}")
    print(f"Property Manager user has password: {bool(pm_user.password)}")
else:
    print("\nNo property_manager1 user found")
