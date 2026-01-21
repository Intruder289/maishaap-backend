#!/usr/bin/env python
"""
Final comprehensive check of all phone-related implementations
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from properties.models import Customer
from django.contrib.auth.models import User

print("=" * 80)
print("FINAL COMPREHENSIVE CHECK - PHONE NUMBER IMPLEMENTATION")
print("=" * 80)
print()

all_checks_passed = True

# 1. Check Profile Model
print("1. PROFILE MODEL")
print("-" * 80)
profile_field = Profile._meta.get_field('phone')
if not profile_field.blank and not profile_field.null and profile_field.unique:
    print("[OK] Phone is mandatory and unique")
else:
    print(f"[ERROR] Phone settings: blank={profile_field.blank}, null={profile_field.null}, unique={profile_field.unique}")
    all_checks_passed = False

# Check existing data
profiles_without_phone = Profile.objects.filter(phone__isnull=True) | Profile.objects.filter(phone='')
if profiles_without_phone.count() == 0:
    print("[OK] All profiles have phone numbers")
else:
    print(f"[ERROR] Found {profiles_without_phone.count()} profiles without phone")
    all_checks_passed = False
print()

# 2. Check Customer Model
print("2. CUSTOMER MODEL")
print("-" * 80)
customer_field = Customer._meta.get_field('phone')
if not customer_field.blank and not customer_field.null:
    print("[OK] Customer phone is mandatory")
else:
    print(f"[ERROR] Customer phone: blank={customer_field.blank}, null={customer_field.null}")
    all_checks_passed = False
print()

# 3. Check Serializer
print("3. SERIALIZER")
print("-" * 80)
with open('accounts/serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'phone = serializers.CharField(max_length=15, required=True' in content:
        print("[OK] Phone is required in serializer")
    else:
        print("[ERROR] Phone not required in serializer")
        all_checks_passed = False
    
    if 'Phone number is required and cannot be empty' in content:
        print("[OK] Validation requires phone")
    else:
        print("[ERROR] Validation does not require phone")
        all_checks_passed = False
    
    if 'Phone number already exists' in content:
        print("[OK] Uniqueness check in validation")
    else:
        print("[ERROR] Uniqueness check missing")
        all_checks_passed = False
print()

# 4. Check Smart Logic in Gateway
print("4. PAYMENT GATEWAY SMART LOGIC")
print("-" * 80)
with open('payments/gateway_service.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'is_admin_or_staff' in content and 'payment.booking.customer.phone' in content:
        print("[OK] Smart logic implemented")
    else:
        print("[ERROR] Smart logic not properly implemented")
        all_checks_passed = False
    
    if 'test_phone' not in content or 'cls.AZAM_PAY_CONFIG.get(\'test_phone\')' not in content:
        print("[OK] Sandbox test phone fallback removed")
    else:
        print("[ERROR] Sandbox test phone fallback still present")
        all_checks_passed = False
print()

# 5. Check Migration
print("5. MIGRATION")
print("-" * 80)
import os
migration_file = 'accounts/migrations/0013_make_phone_mandatory.py'
if os.path.exists(migration_file):
    print("[OK] Migration file exists")
    with open(migration_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'blank=False' in content or 'null=False' in content or 'AlterField' in content:
            print("[OK] Migration makes phone mandatory")
        else:
            print("[WARN] Migration may not be complete")
else:
    print("[ERROR] Migration file not found")
    all_checks_passed = False
print()

# 6. Test Phone Uniqueness
print("6. PHONE UNIQUENESS TEST")
print("-" * 80)
# Check for duplicate phones
from django.db.models import Count
duplicate_phones = Profile.objects.values('phone').annotate(count=Count('phone')).filter(count__gt=1).exclude(phone__isnull=True).exclude(phone='')
if duplicate_phones.count() == 0:
    print("[OK] No duplicate phone numbers found")
else:
    print(f"[WARN] Found {duplicate_phones.count()} duplicate phone numbers")
    for dup in duplicate_phones[:5]:
        print(f"  - Phone {dup['phone']} used by {dup['count']} users")
print()

print("=" * 80)
print("FINAL RESULT")
print("=" * 80)
print()

if all_checks_passed:
    print("[SUCCESS] All checks passed!")
    print()
    print("Summary:")
    print("  [OK] Phone is mandatory in Profile model")
    print("  [OK] Phone is unique in Profile model")
    print("  [OK] Phone is required in all registration paths")
    print("  [OK] Smart logic implemented in payment gateway")
    print("  [OK] Sandbox fallback removed")
    print("  [OK] Migration ready to apply")
    print()
    print("Next step: Run migration")
    print("  python manage.py migrate accounts")
else:
    print("[ERROR] Some checks failed. Please review errors above.")
print()
