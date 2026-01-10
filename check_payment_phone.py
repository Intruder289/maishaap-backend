#!/usr/bin/env python
"""Script to check payment phone number source"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Booking, Customer
from accounts.models import Profile
from payments.models import Payment

# Get booking #10
booking = Booking.objects.select_related('customer', 'created_by').get(id=10)

print("=" * 60)
print("BOOKING #10 INFORMATION")
print("=" * 60)
print(f"\nCustomer Information:")
print(f"  Name: {booking.customer.full_name}")
print(f"  Phone: {booking.customer.phone}")
print(f"  Email: {booking.customer.email}")

print(f"\nBooking Created By User:")
print(f"  Username: {booking.created_by.username}")
print(f"  Email: {booking.created_by.email}")

# Check user profile
try:
    profile = Profile.objects.get(user=booking.created_by)
    print(f"  Profile Phone: {profile.phone}")
except Profile.DoesNotExist:
    print(f"  Profile Phone: No profile found")

# Check payments for this booking
print(f"\nPayments for this booking:")
payments = Payment.objects.filter(booking=booking).select_related('tenant')
if payments.exists():
    for payment in payments:
        print(f"\n  Payment ID: {payment.id}")
        print(f"  Amount: {payment.amount}")
        print(f"  Status: {payment.status}")
        print(f"  Payment Method: {payment.payment_method}")
        print(f"  Tenant (who made payment): {payment.tenant.username}")
        
        # Check tenant profile phone
        try:
            tenant_profile = Profile.objects.get(user=payment.tenant)
            print(f"  Tenant Profile Phone: {tenant_profile.phone}")
        except Profile.DoesNotExist:
            print(f"  Tenant Profile Phone: No profile found")
        
        # Check what phone would be used based on gateway logic
        print(f"\n  Phone Number Selection Logic:")
        user_profile = getattr(payment.tenant, 'profile', None)
        phone_from_profile = user_profile.phone if user_profile and user_profile.phone else None
        phone_from_customer = payment.booking.customer.phone if payment.booking else None
        
        print(f"    1. User Profile Phone: {phone_from_profile or 'NOT SET'}")
        print(f"    2. Customer Phone: {phone_from_customer or 'NOT SET'}")
        
        if phone_from_profile:
            print(f"    -> USED FOR PAYMENT: {phone_from_profile} (from logged-in user profile)")
        elif phone_from_customer:
            print(f"    -> USED FOR PAYMENT: {phone_from_customer} (from customer)")
        else:
            print(f"    -> USED FOR PAYMENT: None (no phone found)")
else:
    print("  No payments found for this booking")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print("\nThe payment gateway uses phone numbers in this priority order:")
print("1. Logged-in user's profile phone (payment.tenant.profile.phone)")
print("2. Customer's phone (payment.booking.customer.phone)")
print("\nSo if you see '255788412511', it's likely the logged-in user's phone,")
print("NOT the customer's phone number (0758285812).")
