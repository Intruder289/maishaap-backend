#!/usr/bin/env python
"""
Script to find which table contains a phone number
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

phone_to_find = "0752285812"

print("=" * 80)
print(f"SEARCHING FOR PHONE NUMBER: {phone_to_find}")
print("=" * 80)
print()

# Try different formats
phone_variations = [
    phone_to_find,
    f"+{phone_to_find}",
    f"+255{phone_to_find[1:]}" if phone_to_find.startswith('0') else phone_to_find,
    f"255{phone_to_find[1:]}" if phone_to_find.startswith('0') else phone_to_find,
]

print("1. CHECKING accounts_profile TABLE (Profile model):")
print("-" * 80)
found_in_profile = False
for phone_var in phone_variations:
    profiles = Profile.objects.filter(phone__iexact=phone_var).select_related('user')
    if profiles.exists():
        found_in_profile = True
        for profile in profiles:
            print(f"   [FOUND] Table: accounts_profile")
            print(f"   User ID: {profile.user.id}")
            print(f"   Username: {profile.user.username}")
            print(f"   Email: {profile.user.email}")
            print(f"   Phone (stored): {profile.phone}")
            print(f"   Full Name: {profile.user.get_full_name()}")
            print()
        break

if not found_in_profile:
    print("   [NOT FOUND] Phone number not in accounts_profile table")
print()

print("2. CHECKING customers TABLE (Customer model):")
print("-" * 80)
found_in_customers = False
for phone_var in phone_variations:
    customers = Customer.objects.filter(phone__iexact=phone_var)
    if customers.exists():
        found_in_customers = True
        for customer in customers:
            print(f"   [FOUND] Table: customers")
            print(f"   Customer ID: {customer.id}")
            print(f"   Name: {customer.full_name}")
            print(f"   Email: {customer.email}")
            print(f"   Phone (stored): {customer.phone}")
            print()
        break

if not found_in_customers:
    print("   [NOT FOUND] Phone number not in customers table")
print()

print("3. SEARCHING ALL VARIATIONS:")
print("-" * 80)
print(f"   Searching for: {phone_variations}")
print()

# Search with LIKE/contains
print("4. PARTIAL MATCH SEARCH:")
print("-" * 80)

# Extract last 9 digits (Tanzanian mobile format)
if len(phone_to_find) >= 9:
    last_9 = phone_to_find[-9:] if not phone_to_find.startswith('0') else phone_to_find[1:]
    
    # Search in Profile
    profiles_partial = Profile.objects.filter(phone__contains=last_9).select_related('user')
    if profiles_partial.exists():
        print(f"   [FOUND IN accounts_profile] Partial match (last 9 digits: {last_9}):")
        for profile in profiles_partial[:5]:  # Show first 5
            print(f"      User: {profile.user.username}, Phone: {profile.phone}")
    
    # Search in Customer
    customers_partial = Customer.objects.filter(phone__contains=last_9)
    if customers_partial.exists():
        print(f"   [FOUND IN customers] Partial match (last 9 digits: {last_9}):")
        for customer in customers_partial[:5]:  # Show first 5
            print(f"      Customer: {customer.full_name}, Phone: {customer.phone}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("Phone numbers are stored in TWO tables:")
print("1. accounts_profile (Profile model) - for registered users")
print("   - Field: phone")
print("   - Table name: accounts_profile")
print()
print("2. customers (Customer model) - for booking customers")
print("   - Field: phone")
print("   - Table name: customers")
print()
