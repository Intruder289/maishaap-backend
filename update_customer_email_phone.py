#!/usr/bin/env python
"""Script to update customer email and ensure phone uniqueness"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Customer
from django.contrib.auth.models import User

print("=" * 70)
print("UPDATING CUSTOMER EMAIL AND PHONE")
print("=" * 70)

# Get customer
customer = Customer.objects.get(id=10)
print(f"\nCurrent Customer Info:")
print(f"  Name: {customer.full_name}")
print(f"  Email: {customer.email}")
print(f"  Phone: {customer.phone}")

# Check if new email exists
new_email = "j.wewe@gmail.com"
print(f"\nChecking if {new_email} exists:")
email_exists_customer = Customer.objects.filter(email=new_email).exclude(id=customer.id).exists()
email_exists_user = User.objects.filter(email=new_email).exists()

if email_exists_customer:
    print(f"  [WARNING] Email {new_email} already exists in Customer table")
else:
    print(f"  [OK] Email {new_email} is available in Customer table")

if email_exists_user:
    print(f"  [INFO] Email {new_email} exists in User table (this is OK)")
else:
    print(f"  [OK] Email {new_email} is available in User table")

# Check phone uniqueness
current_phone = customer.phone
print(f"\nChecking phone uniqueness for {current_phone}:")
phone_count = Customer.objects.filter(phone=current_phone).exclude(id=customer.id).count()
if phone_count > 0:
    print(f"  [WARNING] Phone {current_phone} is used by {phone_count} other customer(s)")
    print(f"  Phone numbers: {list(Customer.objects.filter(phone=current_phone).exclude(id=customer.id).values_list('id', 'full_name', 'phone'))}")
else:
    print(f"  [OK] Phone {current_phone} is unique")

# Update email
print(f"\n" + "=" * 70)
print("UPDATING CUSTOMER...")
print("=" * 70)

if not email_exists_customer:
    customer.email = new_email
    customer.save()
    print(f"  [SUCCESS] Updated email to: {new_email}")
else:
    print(f"  [SKIPPED] Email update skipped - email already exists")

# Check if phone needs to be made unique
if phone_count > 0:
    # Find a unique phone number
    base_phone = current_phone
    unique_phone = base_phone
    counter = 1
    while Customer.objects.filter(phone=unique_phone).exclude(id=customer.id).exists():
        # Try adding a suffix
        if base_phone.startswith('0'):
            unique_phone = base_phone[:-1] + str(counter)
        else:
            unique_phone = base_phone + f"_{counter}"
        counter += 1
        if counter > 100:
            break
    
    if unique_phone != current_phone:
        print(f"  [INFO] Phone {current_phone} is not unique")
        print(f"  [SUCCESS] Updated phone to unique: {unique_phone}")
        customer.phone = unique_phone
        customer.save()
    else:
        print(f"  [OK] Phone {current_phone} is already unique")
else:
    print(f"  [OK] Phone {current_phone} is already unique")

# Verify update
customer.refresh_from_db()
print(f"\n" + "=" * 70)
print("UPDATED CUSTOMER INFO:")
print("=" * 70)
print(f"  Name: {customer.full_name}")
print(f"  Email: {customer.email}")
print(f"  Phone: {customer.phone}")

# Verify email is now unique
print(f"\nVerification:")
if Customer.objects.filter(email=customer.email).count() == 1:
    print(f"  [OK] Email {customer.email} is now unique")
else:
    print(f"  [WARNING] Email {customer.email} is still not unique")

if Customer.objects.filter(phone=customer.phone).count() == 1:
    print(f"  [OK] Phone {customer.phone} is now unique")
else:
    print(f"  [WARNING] Phone {customer.phone} is still not unique")

print("\n" + "=" * 70)
print("UPDATE COMPLETE!")
print("=" * 70)
