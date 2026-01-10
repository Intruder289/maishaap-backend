#!/usr/bin/env python
"""Script to check for duplicate phone numbers in Customer model"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Customer
from django.db.models import Count

print("=" * 70)
print("CHECKING FOR DUPLICATE PHONE NUMBERS")
print("=" * 70)

# Find duplicate phone numbers
duplicates = Customer.objects.values('phone').annotate(count=Count('phone')).filter(count__gt=1).exclude(phone__isnull=True).exclude(phone='')

if duplicates.exists():
    print(f"\n[WARNING] Found {duplicates.count()} duplicate phone number(s):\n")
    for dup in duplicates:
        phone = dup['phone']
        count = dup['count']
        print(f"Phone: {phone} (used by {count} customers)")
        customers = Customer.objects.filter(phone=phone)
        for c in customers:
            print(f"  - Customer ID {c.id}: {c.full_name} ({c.email})")
        print()
    
    print("=" * 70)
    print("RECOMMENDATION:")
    print("=" * 70)
    print("""
You have duplicate phone numbers. You can:
1. Make phone field unique in the model (requires migration)
2. Keep current setup (phone not unique) - allows multiple customers with same phone
3. Manually update duplicate phones to be unique

Note: Making phone unique might cause issues if family members share a phone.
""")
else:
    print("\n[OK] All phone numbers are unique!")
    print("\nNo duplicates found. Phone numbers are already unique across all customers.")

print("=" * 70)
