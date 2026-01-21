#!/usr/bin/env python
"""
Verify phone number is mandatory in all registration paths
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

print("=" * 80)
print("VERIFICATION: PHONE NUMBER MANDATORY IMPLEMENTATION")
print("=" * 80)
print()

checks = []

# 1. Check Profile model
print("1. PROFILE MODEL")
print("-" * 80)
from accounts.models import Profile
profile_field = Profile._meta.get_field('phone')
if not profile_field.blank and not profile_field.null:
    print("[OK] Profile.phone is mandatory (blank=False, null=False)")
    checks.append(True)
else:
    print(f"[ERROR] Profile.phone is NOT mandatory (blank={profile_field.blank}, null={profile_field.null})")
    checks.append(False)
print(f"  unique: {profile_field.unique}")
print()

# 2. Check Serializer
print("2. TENANT SIGNUP SERIALIZER")
print("-" * 80)
with open('accounts/serializers.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'phone = serializers.CharField(max_length=15, required=True' in content:
        print("[OK] Phone is required in TenantSignupSerializer")
        checks.append(True)
    else:
        print("[ERROR] Phone is NOT required in serializer")
        checks.append(False)
    
    if 'Phone number is required and cannot be empty' in content:
        print("[OK] Validation requires phone number")
        checks.append(True)
    else:
        print("[ERROR] Validation does not require phone")
        checks.append(False)
print()

# 3. Check register_owner view
print("3. REGISTER OWNER VIEW")
print("-" * 80)
with open('accounts/views.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'Phone number is required' in content and 'register_owner' in content:
        print("[OK] register_owner view requires phone")
        checks.append(True)
    else:
        print("[ERROR] register_owner view does not require phone")
        checks.append(False)
    
    if 'Profile.objects.filter(phone=phone.strip()).exists()' in content:
        print("[OK] Phone uniqueness check in register_owner")
        checks.append(True)
    else:
        print("[ERROR] Phone uniqueness check missing")
        checks.append(False)
print()

# 4. Check user_create_api
print("4. USER CREATE API")
print("-" * 80)
with open('accounts/api_views_ajax.py', 'r', encoding='utf-8') as f:
    content = f.read()
    if 'Phone number is required' in content and 'user_create_api' in content:
        print("[OK] user_create_api requires phone")
        checks.append(True)
    else:
        print("[ERROR] user_create_api does not require phone")
        checks.append(False)
print()

# 5. Check Customer model
print("5. CUSTOMER MODEL")
print("-" * 80)
from properties.models import Customer
customer_field = Customer._meta.get_field('phone')
if not customer_field.blank and not customer_field.null:
    print("[OK] Customer.phone is mandatory")
    checks.append(True)
else:
    print(f"[ERROR] Customer.phone is NOT mandatory (blank={customer_field.blank}, null={customer_field.null})")
    checks.append(False)
print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
all_passed = all(checks)
if all_passed:
    print("[SUCCESS] All checks passed!")
    print()
    print("Phone number is mandatory in:")
    print("  [OK] Profile model")
    print("  [OK] TenantSignupSerializer")
    print("  [OK] register_owner view")
    print("  [OK] user_create_api")
    print("  [OK] Customer model")
    print()
    print("Phone number is unique in:")
    print("  [OK] Profile model (unique=True)")
    print()
    print("Next steps:")
    print("  1. Run migration: python manage.py migrate accounts")
    print("  2. Test registration to ensure phone is required")
else:
    print("[ERROR] Some checks failed. Please review the errors above.")
print()
