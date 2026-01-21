#!/usr/bin/env python
"""
Check current phone number mandatory status
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from properties.models import Customer
from django.db import connection

print("=" * 80)
print("PHONE NUMBER MANDATORY STATUS CHECK")
print("=" * 80)
print()

# Check Profile model
print("1. PROFILE MODEL (accounts.models.Profile)")
print("-" * 80)
profile_field = Profile._meta.get_field('phone')
print(f"Field: phone")
print(f"  blank: {profile_field.blank}")
print(f"  null: {profile_field.null}")
print(f"  unique: {profile_field.unique}")
print(f"  max_length: {profile_field.max_length}")
print()

if profile_field.blank or profile_field.null:
    print("  [ISSUE] Phone is NOT mandatory (blank=True or null=True)")
    print("  [FIX NEEDED] Should be blank=False, null=False")
else:
    print("  [OK] Phone is mandatory")

print()

# Check Customer model
print("2. CUSTOMER MODEL (properties.models.Customer)")
print("-" * 80)
customer_field = Customer._meta.get_field('phone')
print(f"Field: phone")
print(f"  blank: {customer_field.blank}")
print(f"  null: {customer_field.null}")
print(f"  unique: {customer_field.unique}")
print(f"  max_length: {customer_field.max_length}")
print()

if customer_field.blank or customer_field.null:
    print("  [ISSUE] Customer phone is NOT mandatory")
    print("  [FIX NEEDED] Should be blank=False, null=False")
else:
    print("  [OK] Customer phone is mandatory")

print()

# Check for users without phone
print("3. CHECKING EXISTING DATA")
print("-" * 80)
profiles_without_phone = Profile.objects.filter(phone__isnull=True) | Profile.objects.filter(phone='')
count_no_phone = profiles_without_phone.count()
print(f"Profiles without phone: {count_no_phone}")

if count_no_phone > 0:
    print("  [WARNING] Found profiles without phone numbers:")
    for profile in profiles_without_phone[:10]:
        print(f"    - User: {profile.user.username}, Phone: {profile.phone or 'NOT SET'}")
    if count_no_phone > 10:
        print(f"    ... and {count_no_phone - 10} more")
else:
    print("  [OK] All profiles have phone numbers")

print()

customers_without_phone = Customer.objects.filter(phone__isnull=True) | Customer.objects.filter(phone='')
count_no_customer_phone = customers_without_phone.count()
print(f"Customers without phone: {count_no_customer_phone}")

if count_no_customer_phone > 0:
    print("  [WARNING] Found customers without phone numbers:")
    for customer in customers_without_phone[:10]:
        print(f"    - Customer: {customer.full_name}, Phone: {customer.phone or 'NOT SET'}")
    if count_no_customer_phone > 10:
        print(f"    ... and {count_no_customer_phone - 10} more")
else:
    print("  [OK] All customers have phone numbers")

print()

# Check serializer
print("4. SERIALIZER CHECK")
print("-" * 80)
with open('accounts/serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'phone = serializers.CharField(max_length=15, required=False' in content:
        print("  [ISSUE] Phone is NOT required in TenantSignupSerializer")
        print("  [FIX NEEDED] Should be required=True")
    elif 'phone = serializers.CharField(max_length=15, required=True' in content:
        print("  [OK] Phone is required in serializer")
    else:
        print("  [CHECK] Need to verify serializer")

print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Issues Found:")
print("  1. Profile.phone: blank=True, null=True (should be False)")
print("  2. TenantSignupSerializer.phone: required=False (should be True)")
print("  3. Validation allows empty phone (should require it)")
print()
print("Actions Needed:")
print("  1. Update Profile model: blank=False, null=False")
print("  2. Update TenantSignupSerializer: required=True")
print("  3. Update validation to require phone")
print("  4. Create migration for model change")
print("  5. Update existing data (if any users without phone)")
print()
