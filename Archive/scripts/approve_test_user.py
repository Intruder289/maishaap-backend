"""
Quick script to approve the test user for API login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

# Find the test user
username = 'testuser_20251006_100841'

try:
    user = User.objects.get(username=username)
    
    # Activate user account
    user.is_active = True
    user.save()
    
    # Approve user profile
    profile = user.profile
    profile.is_approved = True
    profile.approved_at = timezone.now()
    profile.save()
    
    print("✅ User approval successful!")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   is_active: {user.is_active}")
    print(f"   is_approved: {profile.is_approved}")
    print(f"   approved_at: {profile.approved_at}")
    print("\n🔑 You can now login via Swagger or the mobile app!")
    
except User.DoesNotExist:
    print(f"❌ User '{username}' not found")
except Exception as e:
    print(f"❌ Error: {e}")
