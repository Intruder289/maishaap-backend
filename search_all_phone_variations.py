#!/usr/bin/env python
"""
Search for phone number with all possible variations and partial matches
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

phone_to_find = "0752285812"

print("=" * 80)
print(f"SEARCHING FOR PHONE: {phone_to_find}")
print("=" * 80)
print()

# Extract key parts
last_9 = "752285812"  # Last 9 digits
last_8 = "52285812"   # Last 8 digits
last_7 = "2285812"    # Last 7 digits

print("Searching with variations and partial matches...")
print()

# 1. accounts_profile table
print("=" * 80)
print("1. accounts_profile TABLE")
print("=" * 80)

with connection.cursor() as cursor:
    # Exact matches
    cursor.execute("SELECT id, user_id, phone FROM accounts_profile WHERE phone = %s", [phone_to_find])
    exact = cursor.fetchall()
    
    # Contains last 9 digits
    cursor.execute("SELECT id, user_id, phone FROM accounts_profile WHERE phone LIKE %s", [f'%{last_9}%'])
    partial_9 = cursor.fetchall()
    
    # Contains last 8 digits
    cursor.execute("SELECT id, user_id, phone FROM accounts_profile WHERE phone LIKE %s", [f'%{last_8}%'])
    partial_8 = cursor.fetchall()
    
    # Contains last 7 digits
    cursor.execute("SELECT id, user_id, phone FROM accounts_profile WHERE phone LIKE %s", [f'%{last_7}%'])
    partial_7 = cursor.fetchall()
    
    if exact:
        print(f"[EXACT MATCH] Found {len(exact)} result(s):")
        for row in exact:
            print(f"   ID: {row[0]}, User ID: {row[1]}, Phone: {row[2]}")
    elif partial_9:
        print(f"[PARTIAL MATCH - Last 9 digits] Found {len(partial_9)} result(s):")
        for row in partial_9[:10]:
            print(f"   ID: {row[0]}, User ID: {row[1]}, Phone: {row[2]}")
    elif partial_8:
        print(f"[PARTIAL MATCH - Last 8 digits] Found {len(partial_8)} result(s):")
        for row in partial_8[:10]:
            print(f"   ID: {row[0]}, User ID: {row[1]}, Phone: {row[2]}")
    elif partial_7:
        print(f"[PARTIAL MATCH - Last 7 digits] Found {len(partial_7)} result(s):")
        for row in partial_7[:10]:
            print(f"   ID: {row[0]}, User ID: {row[1]}, Phone: {row[2]}")
    else:
        print("[NOT FOUND]")
    
    # Show all phones containing these digits
    if partial_9:
        print(f"\nAll phones containing '{last_9}':")
        for row in partial_9[:20]:
            print(f"   {row[2]}")

print()

# 2. customers table
print("=" * 80)
print("2. customers TABLE")
print("=" * 80)

with connection.cursor() as cursor:
    # Exact matches
    cursor.execute("SELECT id, first_name, last_name, email, phone FROM customers WHERE phone = %s", [phone_to_find])
    exact = cursor.fetchall()
    
    # Contains last 9 digits
    cursor.execute("SELECT id, first_name, last_name, email, phone FROM customers WHERE phone LIKE %s", [f'%{last_9}%'])
    partial_9 = cursor.fetchall()
    
    # Contains last 8 digits
    cursor.execute("SELECT id, first_name, last_name, email, phone FROM customers WHERE phone LIKE %s", [f'%{last_8}%'])
    partial_8 = cursor.fetchall()
    
    # Emergency contact phone
    cursor.execute("SELECT id, first_name, last_name, email, emergency_contact_phone FROM customers WHERE emergency_contact_phone LIKE %s", [f'%{last_9}%'])
    emergency = cursor.fetchall()
    
    if exact:
        print(f"[EXACT MATCH] Found {len(exact)} result(s):")
        for row in exact:
            print(f"   ID: {row[0]}, Name: {row[1]} {row[2]}, Email: {row[3]}, Phone: {row[4]}")
    elif partial_9:
        print(f"[PARTIAL MATCH - Last 9 digits] Found {len(partial_9)} result(s):")
        for row in partial_9[:10]:
            print(f"   ID: {row[0]}, Name: {row[1]} {row[2]}, Email: {row[3]}, Phone: {row[4]}")
    elif partial_8:
        print(f"[PARTIAL MATCH - Last 8 digits] Found {len(partial_8)} result(s):")
        for row in partial_8[:10]:
            print(f"   ID: {row[0]}, Name: {row[1]} {row[2]}, Email: {row[3]}, Phone: {row[4]}")
    else:
        print("[NOT FOUND]")
    
    if emergency:
        print(f"\n[EMERGENCY CONTACT MATCH] Found {len(emergency)} result(s):")
        for row in emergency[:10]:
            print(f"   Customer ID: {row[0]}, Name: {row[1]} {row[2]}, Emergency Phone: {row[4]}")

print()

# 3. Show all unique phone formats in database
print("=" * 80)
print("3. SAMPLE PHONE NUMBER FORMATS IN DATABASE")
print("=" * 80)

with connection.cursor() as cursor:
    # Sample from accounts_profile
    cursor.execute("SELECT DISTINCT phone FROM accounts_profile WHERE phone IS NOT NULL AND phone != '' LIMIT 10")
    profile_phones = cursor.fetchall()
    if profile_phones:
        print("Sample from accounts_profile:")
        for (phone,) in profile_phones:
            print(f"   {phone}")
    
    # Sample from customers
    cursor.execute("SELECT DISTINCT phone FROM customers WHERE phone IS NOT NULL AND phone != '' LIMIT 10")
    customer_phones = cursor.fetchall()
    if customer_phones:
        print("\nSample from customers:")
        for (phone,) in customer_phones:
            print(f"   {phone}")

print()
print("=" * 80)
print("SQL QUERIES TO RUN MANUALLY")
print("=" * 80)
print()
print("1. Search accounts_profile:")
print("   SELECT * FROM accounts_profile WHERE phone LIKE '%752285812%';")
print()
print("2. Search customers:")
print("   SELECT * FROM customers WHERE phone LIKE '%752285812%';")
print()
print("3. Search emergency contact:")
print("   SELECT * FROM customers WHERE emergency_contact_phone LIKE '%752285812%';")
print()
