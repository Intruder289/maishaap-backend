#!/usr/bin/env python
"""
Script to check which phone number is used for payment processing
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from properties.models import Booking, Customer
from payments.models import Payment
from django.contrib.auth.models import User

# UnifiedPayment is just an alias for Payment
UnifiedPayment = Payment

print("=" * 80)
print("PAYMENT PHONE NUMBER FLOW ANALYSIS")
print("=" * 80)
print()

# Get a recent booking with payment
booking = Booking.objects.select_related('customer').first()
if not booking:
    print("No bookings found in database")
    sys.exit(0)

print(f"Example Booking: {booking.booking_reference}")
print(f"Customer: {booking.customer.full_name}")
print(f"Customer Email: {booking.customer.email}")
print(f"Customer Phone: {booking.customer.phone}")
print()

# Check how tenant is determined
print("=" * 80)
print("1. HOW TENANT IS DETERMINED")
print("=" * 80)
print()
print("When creating a payment (in properties/views.py, line ~5996-6002):")
print()
print("  # Try to find user by customer email")
print("  try:")
print("      customer_user = User.objects.get(email=booking.customer.email)")
print("  except User.DoesNotExist:")
print("      customer_user = request.user  # Logged-in user")
print()

# Check if customer email matches any user
try:
    customer_user = User.objects.get(email=booking.customer.email)
    print(f"  [FOUND] Customer email '{booking.customer.email}' matches user: {customer_user.username}")
    print(f"  -> payment.tenant will be: {customer_user.username}")
except User.DoesNotExist:
    print(f"  [NOT FOUND] Customer email '{booking.customer.email}' doesn't match any user")
    print(f"  -> payment.tenant will be: logged-in user (whoever is making the payment)")
print()

# Check unified payments
unified_payments = UnifiedPayment.objects.filter(booking=booking).select_related('tenant', 'booking__customer')
if unified_payments.exists():
    print("=" * 80)
    print("2. ACTUAL PAYMENT RECORDS")
    print("=" * 80)
    print()
    for payment in unified_payments[:3]:
        print(f"Payment ID: {payment.id}")
        print(f"  Amount: {payment.amount}")
        print(f"  Status: {payment.status}")
        print(f"  Payment Method: {payment.payment_method}")
        print(f"  Tenant (payment.tenant): {payment.tenant.username} ({payment.tenant.email})")
        
        # Get tenant profile phone
        try:
            tenant_profile = Profile.objects.get(user=payment.tenant)
            tenant_phone = tenant_profile.phone
            print(f"  Tenant Profile Phone: {tenant_phone}")
        except Profile.DoesNotExist:
            tenant_phone = None
            print(f"  Tenant Profile Phone: NOT SET")
        
        print(f"  Customer Phone: {payment.booking.customer.phone}")
        print()
        
        # Simulate gateway logic
        print("  [GATEWAY LOGIC] Which phone will be used?")
        print("  " + "-" * 70)
        
        # Step 1: Check tenant profile phone
        user_profile = getattr(payment.tenant, 'profile', None)
        phone_number = user_profile.phone if user_profile and user_profile.phone else None
        
        if phone_number:
            print(f"  STEP 1: payment.tenant.profile.phone = {phone_number}")
            print(f"  -> USED FOR PAYMENT: {phone_number} (from tenant profile)")
        else:
            print(f"  STEP 1: payment.tenant.profile.phone = NOT SET")
            
            # Step 2: Check customer phone
            if payment.booking:
                phone_number = payment.booking.customer.phone
                if phone_number:
                    print(f"  STEP 2: payment.booking.customer.phone = {phone_number}")
                    print(f"  -> USED FOR PAYMENT: {phone_number} (from customer)")
                else:
                    print(f"  STEP 2: payment.booking.customer.phone = NOT SET")
                    print(f"  -> ERROR: No phone number available")
            else:
                print(f"  STEP 2: No booking associated")
                print(f"  -> ERROR: No phone number available")
        
        print()
else:
    print("No unified payments found for this booking")
    print()

print("=" * 80)
print("3. SUMMARY: PHONE NUMBER PRIORITY")
print("=" * 80)
print()
print("The payment gateway (payments/gateway_service.py, lines 414-439) uses:")
print()
print("PRIORITY 1: payment.tenant.profile.phone")
print("  - This is the TENANT's phone number")
print("  - Tenant is determined by:")
print("    a) User with matching customer email, OR")
print("    b) Logged-in user (if no email match)")
print()
print("PRIORITY 2: payment.booking.customer.phone")
print("  - This is the CUSTOMER's phone number")
print("  - Only used if tenant has no phone")
print()
print("PRIORITY 3: Test phone from config (sandbox only)")
print("  - Only used in sandbox mode if configured")
print()
print("=" * 80)
print("4. ANSWER TO YOUR QUESTION")
print("=" * 80)
print()
print("Which phone number is used for payment?")
print()
print("IT DEPENDS:")
print()
print("1. If customer email matches a registered user:")
print("   -> Uses that user's profile phone (NOT logged-in user's phone)")
print()
print("2. If customer email doesn't match any user:")
print("   -> Uses logged-in user's profile phone")
print()
print("3. If tenant has no phone:")
print("   -> Uses customer's phone as fallback")
print()
print("SO:")
print("- It's NOT always the logged-in user's phone")
print("- It's the TENANT's phone (which may or may not be the logged-in user)")
print("- Customer phone is only used as a fallback")
print()
