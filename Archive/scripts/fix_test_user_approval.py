"""
Run this to approve the test user
Execute: python fix_test_user_approval.py
"""
import os
import sys

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone

username = 'testuser_20251006_100841'

try:
    user = User.objects.get(username=username)
    profile = user.profile
    
    print(f"BEFORE:")
    print(f"  is_active: {user.is_active}")
    print(f"  is_approved: {profile.is_approved}")
    print(f"  approved_at: {profile.approved_at}")
    
    # Update approval
    profile.is_approved = True
    profile.approved_at = timezone.now()
    profile.save()
    
    print(f"\nAFTER:")
    print(f"  is_active: {user.is_active}")
    print(f"  is_approved: {profile.is_approved}")
    print(f"  approved_at: {profile.approved_at}")
    print(f"\n✅ User approved successfully! You can now login via API.")
    
except User.DoesNotExist:
    print(f"❌ User '{username}' not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
