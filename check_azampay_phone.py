#!/usr/bin/env python
"""Check AZAMPAY phone number and provider"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from django.contrib.auth.models import User
from django.conf import settings

print("=" * 70)
print("AZAMPAY PAYMENT PHONE NUMBER CHECK")
print("=" * 70)

# Check logged-in user (admin_user)
user = User.objects.get(username='admin_user')
profile = Profile.objects.get(user=user)

print(f"\nUser: {user.username}")
print(f"Email: {user.email}")
print(f"Profile Phone: {profile.phone}")

# Format for AZAMPAY
phone = profile.phone
if phone.startswith('0'):
    azampay_phone = '255' + phone[1:]
elif phone.startswith('+255'):
    azampay_phone = phone[1:]
elif phone.startswith('255'):
    azampay_phone = phone
else:
    azampay_phone = '255' + phone

print(f"\nPhone formatted for AZAMPAY: {azampay_phone}")

# Check provider
default_provider = getattr(settings, 'AZAM_PAY_CONFIG', {}).get('default_provider', 'AIRTEL')
print(f"Default Provider: {default_provider}")

print("\n" + "=" * 70)
print("WHY YOU MIGHT NOT RECEIVE PAYMENT PROMPT")
print("=" * 70)
print("""
1. PROVIDER MISMATCH:
   - System is using: AIRTEL
   - Your phone number: 0758285812
   - If your SIM card is TIGO, MPESA, or HALOPESA, you won't receive the prompt
   - Solution: Change provider in settings or ensure phone matches provider

2. SANDBOX MODE:
   - You're using AZAMPAY sandbox (testing environment)
   - Sandbox might not send real prompts to all numbers
   - Solution: Check AZAMPAY dashboard for transaction status

3. PHONE NUMBER NOT REGISTERED:
   - Phone must be registered with mobile money service
   - Number must be active and have mobile money enabled
   - Solution: Ensure your phone has mobile money activated

4. AMOUNT TOO LARGE:
   - Amount: Tsh 9,500,000
   - Some providers have limits on transaction amounts
   - Solution: Check your mobile money transaction limits

5. NETWORK ISSUES:
   - Delayed prompts can happen
   - Check your phone after a few minutes
   - Solution: Wait a bit and check again
""")

print("=" * 70)
