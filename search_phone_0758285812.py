#!/usr/bin/env python
"""
Comprehensive search for phone number 0758285812 in all formats
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from accounts.models import Profile
from properties.models import Customer, Booking
from django.contrib.auth.models import User
from django.db import connection

phone_to_find = "0758285812"

print("=" * 80)
print(f"COMPREHENSIVE SEARCH FOR PHONE: {phone_to_find}")
print("=" * 80)
print()

# Generate all possible format variations
variations = [
    phone_to_find,                    # 0758285812
    f"+{phone_to_find}",              # +0758285812
    phone_to_find[1:],                # 758285812 (without leading 0)
    f"+255{phone_to_find[1:]}",       # +255758285812
    f"255{phone_to_find[1:]}",        # 255758285812
    f"0{phone_to_find[1:]}",          # 0758285812 (same)
]

# Extract key parts for partial matching
last_9 = phone_to_find[1:] if phone_to_find.startswith('0') else phone_to_find[-9:]  # 758285812
last_8 = last_9[1:] if len(last_9) > 8 else last_9  # 58285812
last_7 = last_8[1:] if len(last_8) > 7 else last_8  # 8285812

print(f"Searching variations: {variations}")
print(f"Partial match keys: last_9={last_9}, last_8={last_8}, last_7={last_7}")
print()

results = []

# 1. Search accounts_profile table
print("=" * 80)
print("1. accounts_profile TABLE (Registered Users)")
print("=" * 80)

with connection.cursor() as cursor:
    # Try exact matches for all variations
    found_exact = False
    for phone_var in variations:
        cursor.execute("""
            SELECT id, user_id, phone 
            FROM accounts_profile 
            WHERE phone = %s OR phone = %s
        """, [phone_var, phone_var.replace(' ', '')])
        rows = cursor.fetchall()
        if rows:
            found_exact = True
            print(f"[EXACT MATCH] Found with format: {phone_var}")
            for row in rows:
                user_id = row[1]
                try:
                    user = User.objects.get(id=user_id)
                    results.append({
                        'table': 'accounts_profile',
                        'id': row[0],
                        'user_id': user_id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.get_full_name(),
                        'phone_stored': row[2]
                    })
                    print(f"   Profile ID: {row[0]}")
                    print(f"   User ID: {user_id}")
                    print(f"   Username: {user.username}")
                    print(f"   Email: {user.email}")
                    print(f"   Full Name: {user.get_full_name()}")
                    print(f"   Phone (stored as): {row[2]}")
                    print()
                except User.DoesNotExist:
                    print(f"   Profile ID: {row[0]}, User ID: {user_id} (user not found)")
                    print(f"   Phone (stored as): {row[2]}")
                    print()
    
    if not found_exact:
        print("[EXACT MATCH] Not found")
    
    # Partial match search
    print("\n[PARTIAL MATCH SEARCH]")
    cursor.execute("""
        SELECT id, user_id, phone 
        FROM accounts_profile 
        WHERE phone LIKE %s 
           OR phone LIKE %s
           OR phone LIKE %s
        ORDER BY phone
        LIMIT 20
    """, [f'%{last_9}%', f'%{last_8}%', f'%{last_7}%'])
    partial_rows = cursor.fetchall()
    
    if partial_rows:
        print(f"Found {len(partial_rows)} profile(s) with partial match:")
        for row in partial_rows:
            print(f"   Profile ID: {row[0]}, User ID: {row[1]}, Phone: {row[2]}")
    else:
        print("   No partial matches found")

print()

# 2. Search customers table
print("=" * 80)
print("2. customers TABLE (Booking Customers)")
print("=" * 80)

with connection.cursor() as cursor:
    # Try exact matches
    found_exact = False
    for phone_var in variations:
        cursor.execute("""
            SELECT id, first_name, last_name, email, phone 
            FROM customers 
            WHERE phone = %s OR phone = %s
        """, [phone_var, phone_var.replace(' ', '')])
        rows = cursor.fetchall()
        if rows:
            found_exact = True
            print(f"[EXACT MATCH] Found with format: {phone_var}")
            for row in rows:
                results.append({
                    'table': 'customers',
                    'id': row[0],
                    'user_id': None,
                    'username': None,
                    'email': row[3],
                    'full_name': f"{row[1]} {row[2]}",
                    'phone_stored': row[4]
                })
                print(f"   Customer ID: {row[0]}")
                print(f"   Name: {row[1]} {row[2]}")
                print(f"   Email: {row[3]}")
                print(f"   Phone (stored as): {row[4]}")
                print()
    
    if not found_exact:
        print("[EXACT MATCH] Not found")
    
    # Partial match search
    print("\n[PARTIAL MATCH SEARCH]")
    cursor.execute("""
        SELECT id, first_name, last_name, email, phone 
        FROM customers 
        WHERE phone LIKE %s 
           OR phone LIKE %s
           OR phone LIKE %s
        ORDER BY phone
        LIMIT 20
    """, [f'%{last_9}%', f'%{last_8}%', f'%{last_7}%'])
    partial_rows = cursor.fetchall()
    
    if partial_rows:
        print(f"Found {len(partial_rows)} customer(s) with partial match:")
        for row in partial_rows:
            print(f"   Customer ID: {row[0]}, Name: {row[1]} {row[2]}, Phone: {row[4]}")
    else:
        print("   No partial matches found")

print()

# 3. Search emergency contact phone
print("=" * 80)
print("3. customers.emergency_contact_phone FIELD")
print("=" * 80)

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT id, first_name, last_name, email, emergency_contact_phone 
        FROM customers 
        WHERE emergency_contact_phone LIKE %s 
           OR emergency_contact_phone LIKE %s
           OR emergency_contact_phone LIKE %s
        LIMIT 20
    """, [f'%{last_9}%', f'%{last_8}%', f'%{last_7}%'])
    emergency_rows = cursor.fetchall()
    
    if emergency_rows:
        print(f"Found {len(emergency_rows)} customer(s) with matching emergency contact:")
        for row in emergency_rows:
            print(f"   Customer ID: {row[0]}, Name: {row[1]} {row[2]}")
            print(f"   Emergency Contact Phone: {row[4]}")
            print()
    else:
        print("   No matches found")

print()

# 4. Check bookings related to customers with this phone
print("=" * 80)
print("4. BOOKINGS (via Customer phone)")
print("=" * 80)

customers_with_phone = Customer.objects.filter(
    phone__in=variations
).values_list('id', flat=True)

if customers_with_phone:
    bookings = Booking.objects.filter(customer_id__in=customers_with_phone).select_related('customer')
    if bookings.exists():
        print(f"Found {bookings.count()} booking(s) for customer(s) with this phone:")
        for booking in bookings[:10]:
            print(f"   Booking: {booking.booking_reference}")
            print(f"   Customer: {booking.customer.full_name} ({booking.customer.phone})")
            print(f"   Booking ID: {booking.id}")
            print()
    else:
        print("   No bookings found")
else:
    print("   No customers found with this phone")

print()

# 5. Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

if results:
    print(f"\n[FOUND] Phone number found in {len(results)} location(s):\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. Table: {result['table']}")
        print(f"   ID: {result['id']}")
        if result['user_id']:
            print(f"   User ID: {result['user_id']}")
            print(f"   Username: {result['username']}")
        print(f"   Name: {result['full_name']}")
        print(f"   Email: {result['email']}")
        print(f"   Phone (stored as): {result['phone_stored']}")
        print()
else:
    print("\n[NOT FOUND] Phone number not found in any table")
    print("\nThe phone number '0758285812' does not exist in:")
    print("   - accounts_profile table")
    print("   - customers table")
    print("   - customers.emergency_contact_phone field")
    print("\nThis phone number may:")
    print("   1. Not be registered in the system yet")
    print("   2. Be stored in a different format")
    print("   3. Not exist in the database")

print()
print("=" * 80)
print("SQL QUERIES TO RUN MANUALLY")
print("=" * 80)
print()
print("-- Search accounts_profile:")
print("SELECT * FROM accounts_profile WHERE phone LIKE '%758285812%';")
print()
print("-- Search customers:")
print("SELECT * FROM customers WHERE phone LIKE '%758285812%';")
print()
print("-- Search emergency contact:")
print("SELECT * FROM customers WHERE emergency_contact_phone LIKE '%758285812%';")
print()
