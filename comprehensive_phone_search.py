#!/usr/bin/env python
"""
Comprehensive script to search for phone number in all possible tables
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from properties.models import Customer, Booking
from payments.models import Payment
from django.contrib.auth.models import User
from django.db import connection

phone_to_find = "0752285812"

print("=" * 80)
print(f"COMPREHENSIVE PHONE NUMBER SEARCH: {phone_to_find}")
print("=" * 80)
print()

# Generate all possible variations
variations = [
    phone_to_find,  # 0752285812
    phone_to_find.replace('0', '+255', 1) if phone_to_find.startswith('0') else phone_to_find,  # +255752285812
    phone_to_find[1:] if phone_to_find.startswith('0') else phone_to_find,  # 752285812
    f"255{phone_to_find[1:]}" if phone_to_find.startswith('0') else phone_to_find,  # 255752285812
    f"+{phone_to_find}",  # +0752285812
]

# Extract last 9 digits for partial matching
last_9_digits = phone_to_find[-9:] if len(phone_to_find) >= 9 else phone_to_find
if phone_to_find.startswith('0'):
    last_9_digits = phone_to_find[1:]

print(f"Searching variations: {variations}")
print(f"Last 9 digits for partial match: {last_9_digits}")
print()

results = []

# 1. Search accounts_profile table
print("1. SEARCHING accounts_profile TABLE:")
print("-" * 80)
for phone_var in variations:
    profiles = Profile.objects.filter(phone__iexact=phone_var).select_related('user')
    if profiles.exists():
        for profile in profiles:
            results.append({
                'table': 'accounts_profile',
                'model': 'Profile',
                'id': profile.id,
                'user_id': profile.user.id,
                'username': profile.user.username,
                'email': profile.user.email,
                'phone': profile.phone,
                'name': profile.user.get_full_name() or profile.user.username
            })
            print(f"   [FOUND] User: {profile.user.username} ({profile.user.email})")
            print(f"           Phone stored as: {profile.phone}")
            print(f"           Full Name: {profile.user.get_full_name()}")
            print()

# Partial match in Profile
profiles_partial = Profile.objects.filter(phone__icontains=last_9_digits).select_related('user')
if profiles_partial.exists():
    print(f"   [PARTIAL MATCH] Found {profiles_partial.count()} profile(s) containing '{last_9_digits}':")
    for profile in profiles_partial[:10]:
        print(f"      - {profile.user.username}: {profile.phone}")
    print()

if not results:
    print("   [NOT FOUND]")
print()

# 2. Search customers table
print("2. SEARCHING customers TABLE:")
print("-" * 80)
for phone_var in variations:
    customers = Customer.objects.filter(phone__iexact=phone_var)
    if customers.exists():
        for customer in customers:
            results.append({
                'table': 'customers',
                'model': 'Customer',
                'id': customer.id,
                'user_id': None,
                'username': None,
                'email': customer.email,
                'phone': customer.phone,
                'name': customer.full_name
            })
            print(f"   [FOUND] Customer: {customer.full_name} ({customer.email})")
            print(f"           Phone stored as: {customer.phone}")
            print(f"           Customer ID: {customer.id}")
            print()

# Partial match in Customer
customers_partial = Customer.objects.filter(phone__icontains=last_9_digits)
if customers_partial.exists():
    print(f"   [PARTIAL MATCH] Found {customers_partial.count()} customer(s) containing '{last_9_digits}':")
    for customer in customers_partial[:10]:
        print(f"      - {customer.full_name}: {customer.phone}")
    print()

if not any(r['table'] == 'customers' for r in results):
    print("   [NOT FOUND]")
print()

# 3. Search bookings (might have phone in notes or related customer)
print("3. SEARCHING bookings TABLE (via Customer):")
print("-" * 80)
for phone_var in variations:
    bookings = Booking.objects.filter(customer__phone__iexact=phone_var).select_related('customer')
    if bookings.exists():
        print(f"   [FOUND] {bookings.count()} booking(s) for customer with phone {phone_var}:")
        for booking in bookings[:5]:
            print(f"      - Booking: {booking.booking_reference}")
            print(f"        Customer: {booking.customer.full_name} ({booking.customer.phone})")
            print(f"        Booking ID: {booking.id}")
        print()

# 4. Search payments (might reference phone)
print("4. SEARCHING payments TABLE:")
print("-" * 80)
# Check if Payment model has phone field
if hasattr(Payment, 'phone'):
    for phone_var in variations:
        payments = Payment.objects.filter(phone__iexact=phone_var)
        if payments.exists():
            print(f"   [FOUND] {payments.count()} payment(s) with phone {phone_var}")
            for payment in payments[:5]:
                print(f"      - Payment ID: {payment.id}, Amount: {payment.amount}")
            print()

# 5. Raw SQL search across all tables
print("5. RAW SQL SEARCH (checking all tables with 'phone' column):")
print("-" * 80)

with connection.cursor() as cursor:
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name LIKE '%phone%' 
        AND table_schema = 'public'
        ORDER BY table_name;
    """)
    tables_with_phone = cursor.fetchall()
    
    if tables_with_phone:
        print(f"   Found {len(tables_with_phone)} table(s) with 'phone' column:")
        for (table_name,) in tables_with_phone:
            print(f"      - {table_name}")
            
            # Search in each table
            try:
                cursor.execute(f"""
                    SELECT * FROM {table_name} 
                    WHERE phone::text ILIKE %s 
                    LIMIT 5;
                """, [f'%{last_9_digits}%'])
                rows = cursor.fetchall()
                
                if rows:
                    print(f"        [FOUND {len(rows)} row(s)]")
                    # Get column names
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = %s;
                    """, [table_name])
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    for row in rows[:3]:  # Show first 3 matches
                        row_dict = dict(zip(columns, row))
                        phone_value = row_dict.get('phone', 'N/A')
                        print(f"          Phone: {phone_value}")
                        # Show other relevant fields
                        if 'id' in row_dict:
                            print(f"          ID: {row_dict['id']}")
                        if 'email' in row_dict:
                            print(f"          Email: {row_dict['email']}")
                        print()
            except Exception as e:
                print(f"        [ERROR] {str(e)}")
    else:
        print("   [NOT FOUND] No tables with 'phone' column")

print()

# 6. Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)
if results:
    print(f"\n[FOUND] Phone number found in {len(results)} location(s):")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Table: {result['table']} ({result['model']})")
        print(f"   ID: {result['id']}")
        if result['user_id']:
            print(f"   User ID: {result['user_id']}")
            print(f"   Username: {result['username']}")
        print(f"   Name: {result['name']}")
        print(f"   Email: {result['email']}")
        print(f"   Phone (stored): {result['phone']}")
else:
    print("\n[NOT FOUND] Phone number not found in any table")
    print("\nPossible reasons:")
    print("1. Phone number doesn't exist in database")
    print("2. Phone number is stored in different format")
    print("3. Phone number is in a different table")
    print("\nTry searching with partial match using last 9 digits:", last_9_digits)

print()
print("=" * 80)
print("TABLES THAT STORE PHONE NUMBERS:")
print("=" * 80)
print("1. accounts_profile - Registered users (Profile model)")
print("   - Field: phone (CharField, unique=True)")
print("   - SQL: SELECT * FROM accounts_profile WHERE phone = '0752285812';")
print()
print("2. customers - Booking customers (Customer model)")
print("   - Field: phone (CharField)")
print("   - SQL: SELECT * FROM customers WHERE phone = '0752285812';")
print()
print("3. customers.emergency_contact_phone - Emergency contact")
print("   - Field: emergency_contact_phone")
print("   - SQL: SELECT * FROM customers WHERE emergency_contact_phone = '0752285812';")
print()
