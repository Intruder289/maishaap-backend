#!/usr/bin/env python
"""Script to explain the difference between Customer and Tenant"""
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
from documents.models import Lease
from django.contrib.auth.models import User

print("=" * 80)
print("CUSTOMER vs TENANT - COMPREHENSIVE EXPLANATION")
print("=" * 80)

print("\n" + "=" * 80)
print("1. CUSTOMER (properties.Customer)")
print("=" * 80)
print("""
DEFINITION:
-----------
- Customer is a standalone data model (properties.Customer)
- Represents a person who books a property (hotel, lodge, venue, house)
- Does NOT require a user account/login
- Can be created by property owners/staff for walk-in customers
- Stores basic contact information

CHARACTERISTICS:
---------------
- Model: properties.models.Customer
- Table: 'customers' in database
- Fields: first_name, last_name, email, phone, address, etc.
- NOT linked to Django User model
- Can exist without any user account
- Used for: Hotel bookings, Lodge bookings, Venue bookings, House bookings

USE CASES:
----------
- Walk-in customers who don't have accounts
- Customers booking through phone/email
- Customers created by property owners
- Short-term bookings (hotels, lodges, venues)
""")

print("\n" + "=" * 80)
print("2. TENANT (Django User)")
print("=" * 80)
print("""
DEFINITION:
-----------
- Tenant is a Django User (settings.AUTH_USER_MODEL)
- Represents a registered user who can log into the system
- MUST have a user account with username/password
- Has a Profile model linked to the User
- Can make payments, view invoices, manage leases

CHARACTERISTICS:
---------------
- Model: django.contrib.auth.models.User
- Table: 'auth_user' in database
- Has Profile: accounts.models.Profile (one-to-one relationship)
- Profile contains: phone, role, is_approved, etc.
- Can log into the system
- Used for: Long-term leases, Rent payments, System access

USE CASES:
----------
- Registered users who rent properties long-term
- Users who need to log in and manage their account
- Users who make online payments
- Users who have active leases
""")

print("\n" + "=" * 80)
print("3. HOW THEY RELATE IN BOOKINGS")
print("=" * 80)

# Show example booking
booking = Booking.objects.select_related('customer', 'created_by').get(id=10)
print(f"\nExample: Booking HSE-000009")
print(f"  - booking.customer = Customer object (John wewe)")
print(f"    * Customer Email: {booking.customer.email}")
print(f"    * Customer Phone: {booking.customer.phone}")
print(f"    * Customer is NOT a User - just data")
print(f"\n  - booking.created_by = User object ({booking.created_by.username})")
print(f"    * This is the user who created the booking (property owner/staff)")

print("\n" + "=" * 80)
print("4. HOW THEY RELATE IN PAYMENTS")
print("=" * 80)

payment = Payment.objects.filter(booking=booking).first()
if payment:
    print(f"\nExample: Payment for Booking HSE-000009")
    print(f"  - payment.booking.customer = Customer object")
    print(f"    * Customer: {payment.booking.customer.full_name}")
    print(f"    * Customer Phone: {payment.booking.customer.phone}")
    print(f"\n  - payment.tenant = User object (Django User)")
    print(f"    * Tenant: {payment.tenant.username}")
    print(f"    * Tenant Email: {payment.tenant.email}")
    try:
        tenant_profile = Profile.objects.get(user=payment.tenant)
        print(f"    * Tenant Profile Phone: {tenant_profile.phone}")
    except:
        print(f"    * Tenant Profile Phone: No profile")
    
    print(f"\n  KEY DIFFERENCE:")
    print(f"    - payment.tenant is found by matching customer email")
    print(f"    - If customer email matches a user email, that user becomes tenant")
    print(f"    - If no match, logged-in user becomes tenant")

print("\n" + "=" * 80)
print("5. PHONE NUMBER SELECTION IN PAYMENTS")
print("=" * 80)
print("""
When making a payment, the system checks phone numbers in this order:

STEP 1: Check payment.tenant.profile.phone
        - This is the TENANT's phone (Django User's Profile phone)
        - Priority: HIGHEST
        
STEP 2: Check payment.booking.customer.phone
        - This is the CUSTOMER's phone (Customer model phone)
        - Priority: FALLBACK (only if tenant has no phone)

WHY THIS MATTERS:
-----------------
- If customer email matches a user email:
  * payment.tenant = that user
  * Uses that user's profile phone (NOT customer phone)
  
- If customer email doesn't match any user:
  * payment.tenant = logged-in user
  * Uses logged-in user's profile phone (NOT customer phone)
  
- Customer phone is ONLY used if tenant has no phone number
""")

print("\n" + "=" * 80)
print("6. REAL-WORLD EXAMPLE (Your Case)")
print("=" * 80)
print(f"""
Booking HSE-000009:
  Customer: John wewe
  Customer Email: {booking.customer.email}
  Customer Phone: {booking.customer.phone}

Payment Creation:
  System looks for user with email: {booking.customer.email}
  Found: User 'alfred' has email {booking.customer.email}
  So: payment.tenant = user 'alfred'

Phone Selection:
  Step 1: payment.tenant.profile.phone = 0788412511 (alfred's phone)
  Step 2: payment.booking.customer.phone = 0758285812 (customer's phone)
  
  Result: Uses 0788412511 (alfred's phone) because tenant phone exists
  
  Customer phone (0758285812) is NOT used because tenant has a phone
""")

print("\n" + "=" * 80)
print("7. SUMMARY")
print("=" * 80)
print("""
CUSTOMER:
---------
- Data model (properties.Customer)
- No login required
- Used for booking information
- Phone stored in: customer.phone
- Can exist without user account

TENANT:
-------
- Django User (auth.User)
- Requires login account
- Used for payments and system access
- Phone stored in: user.profile.phone
- Must have user account

IN PAYMENTS:
------------
- payment.tenant = User (who makes payment)
- payment.booking.customer = Customer (who booked)
- Gateway uses tenant phone FIRST
- Customer phone is FALLBACK only
""")

print("\n" + "=" * 80)
