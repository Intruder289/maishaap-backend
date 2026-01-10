#!/usr/bin/env python
"""Script to explain payment flow and phone number selection"""
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
from django.contrib.auth.models import User

print("=" * 70)
print("PAYMENT FLOW EXPLANATION FOR BOOKING HSE-000009")
print("=" * 70)

# Get booking
booking = Booking.objects.select_related('customer').get(id=10)
print(f"\n1. BOOKING INFORMATION:")
print(f"   Booking Reference: {booking.booking_reference}")
print(f"   Customer Name: {booking.customer.full_name}")
print(f"   Customer Email: {booking.customer.email}")
print(f"   Customer Phone: {booking.customer.phone}")

# Check if there's a user with customer's email
print(f"\n2. FINDING USER FOR CUSTOMER EMAIL ({booking.customer.email}):")
try:
    customer_user = User.objects.get(email=booking.customer.email)
    print(f"   [FOUND] User: {customer_user.username}")
    print(f"   Full Name: {customer_user.get_full_name()}")
    print(f"   Email: {customer_user.email}")
    try:
        customer_user_profile = Profile.objects.get(user=customer_user)
        print(f"   Profile Phone: {customer_user_profile.phone}")
    except Profile.DoesNotExist:
        print(f"   Profile Phone: No profile")
except User.DoesNotExist:
    print(f"   [NOT FOUND] No user found with email {booking.customer.email}")
    customer_user = None

# Check payments
print(f"\n3. PAYMENT RECORDS FOR THIS BOOKING:")
payments = Payment.objects.filter(booking=booking).select_related('tenant')
if payments.exists():
    for payment in payments:
        print(f"\n   Payment ID: {payment.id}")
        print(f"   Amount: {payment.amount}")
        print(f"   Status: {payment.status}")
        print(f"   Payment Method: {payment.payment_method}")
        print(f"   Tenant (payment.tenant): {payment.tenant.username}")
        print(f"   Tenant Email: {payment.tenant.email}")
        
        # Check tenant profile phone
        try:
            tenant_profile = Profile.objects.get(user=payment.tenant)
            print(f"   Tenant Profile Phone: {tenant_profile.phone}")
        except Profile.DoesNotExist:
            print(f"   Tenant Profile Phone: No profile")
        
        print(f"\n   PHONE NUMBER SELECTION LOGIC:")
        print(f"   Step 1: Check payment.tenant.profile.phone")
        user_profile = getattr(payment.tenant, 'profile', None)
        phone_from_tenant = user_profile.phone if user_profile and user_profile.phone else None
        print(f"          -> {phone_from_tenant or 'NOT FOUND'}")
        
        print(f"   Step 2: If not found, check payment.booking.customer.phone")
        phone_from_customer = payment.booking.customer.phone if payment.booking else None
        print(f"          -> {phone_from_customer or 'NOT FOUND'}")
        
        if phone_from_tenant:
            print(f"\n   [RESULT] Using {phone_from_tenant} (from tenant user profile)")
            print(f"   [NOT USING] {phone_from_customer} (from customer)")
        elif phone_from_customer:
            print(f"\n   [RESULT] Using {phone_from_customer} (from customer)")
        else:
            print(f"\n   [RESULT] No phone found")

print("\n" + "=" * 70)
print("EXPLANATION")
print("=" * 70)
print("\nWHY IS IT USING ALFRED'S PHONE NUMBER?")
print("-" * 70)
print("""
The payment system works like this:

1. When creating a payment for booking HSE-000009:
   - Customer: John wewe (email: mimi@gmail.com, phone: 0758285812)
   - System tries to find a user with email: mimi@gmail.com
   - Found: User 'alfred' has email mimi@gmail.com
   - So payment.tenant is set to user 'alfred' (NOT the logged-in user!)

2. When initiating payment via gateway:
   - Gateway checks: payment.tenant.profile.phone
   - payment.tenant = user 'alfred'
   - alfred's profile phone = 0788412511
   - So it uses 0788412511

3. Why NOT the logged-in user's phone?
   - The payment.tenant is NOT the logged-in user
   - The payment.tenant is the user found by customer email
   - Since 'alfred' has the same email as the customer, 'alfred' becomes the tenant

4. Why NOT the customer's phone (0758285812)?
   - The gateway only uses customer phone as a FALLBACK
   - Since 'alfred' has a phone number, it uses that first
   - Customer phone is only used if tenant has no phone

SOLUTION:
- The customer email (mimi@gmail.com) matches user 'alfred'
- Either:
  a) Change customer email to a unique one, OR
  b) Update 'alfred' user's phone to 0758285812, OR
  c) Modify gateway to prioritize customer phone over tenant phone
""")
