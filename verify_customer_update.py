#!/usr/bin/env python
"""Script to verify customer update and check payment impact"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Customer, Booking
from django.contrib.auth.models import User

print("=" * 70)
print("VERIFICATION: CUSTOMER UPDATE")
print("=" * 70)

customer = Customer.objects.get(id=10)
print(f"\nCustomer Updated:")
print(f"  Name: {customer.full_name}")
print(f"  Email: {customer.email}")
print(f"  Phone: {customer.phone}")

print(f"\nChecking if email matches any user:")
user_match = User.objects.filter(email=customer.email).first()
if user_match:
    print(f"  [WARNING] Email matches user: {user_match.username}")
else:
    print(f"  [OK] Email does not match any user")
    print(f"  [INFO] Future payments will use logged-in user as tenant")

print(f"\nBooking Info:")
booking = Booking.objects.get(id=10)
print(f"  Booking: {booking.booking_reference}")
print(f"  Customer Email: {booking.customer.email}")

print(f"\n" + "=" * 70)
print("IMPACT ON FUTURE PAYMENTS")
print("=" * 70)
print("""
Since customer email (j.wewe@gmail.com) no longer matches any user:
- Future payments will use the LOGGED-IN USER as payment.tenant
- Phone number will come from logged-in user's profile
- Customer phone (0758285812) will only be used if logged-in user has no phone

This means:
- If you log in as 'admin_user' (phone: 0758285812), payment will use 0758285812
- If you log in as 'alfred' (phone: 0788412511), payment will use 0788412511
- Customer phone (0758285812) is now just a fallback
""")

print("=" * 70)
