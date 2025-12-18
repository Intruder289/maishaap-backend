#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User

print("=== USER CHECK ===")
users = User.objects.all()
print(f"Total Users: {users.count()}")
for user in users:
    print(f"- {user.username} (ID: {user.id}, Active: {user.is_active})")

# Check if we can create a test user
if users.count() == 0:
    print("\nCreating test user...")
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"Created user: {test_user.username}")
else:
    print("\nUsing existing user for testing...")
