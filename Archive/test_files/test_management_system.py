#!/usr/bin/env python
import requests
import json
from bs4 import BeautifulSoup

def test_hotel_management():
    print("🏨 TESTING HOTEL MANAGEMENT")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test 1: Hotel Dashboard
    print("\n1. Testing Hotel Dashboard...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/dashboard/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection indicator
            property_badge = soup.find('span', class_='badge')
            if property_badge:
                print(f"   ✅ Property Selection: {property_badge.get_text().strip()}")
            else:
                print("   ❌ Property Selection indicator not found")
            
            # Check for stats cards
            stats_cards = soup.find_all('h4', class_='mb-0')
            if stats_cards:
                print(f"   ✅ Found {len(stats_cards)} stats cards")
                for i, card in enumerate(stats_cards):
                    print(f"      - Card {i+1}: {card.get_text().strip()}")
            else:
                print("   ❌ Stats cards not found")
            
            # Check for New Booking button
            booking_btn = soup.find('a', href=lambda x: x and 'create_hotel_booking' in x)
            if booking_btn:
                print("   ✅ New Booking button found")
            else:
                print("   ❌ New Booking button not found")
                
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")
    
    # Test 2: Hotel Bookings
    print("\n2. Testing Hotel Bookings...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/bookings/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            bookings_table = soup.find('table')
            if bookings_table:
                rows = bookings_table.find_all('tr')
                print(f"   ✅ Bookings table found with {len(rows)-1} booking rows")
            else:
                print("   ✅ Bookings page loaded (no bookings yet)")
        else:
            print(f"   ❌ Bookings failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Bookings error: {e}")
    
    # Test 3: Hotel Rooms
    print("\n3. Testing Hotel Rooms...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/rooms/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rooms_table = soup.find('table')
            if rooms_table:
                rows = rooms_table.find_all('tr')
                print(f"   ✅ Rooms table found with {len(rows)-1} room rows")
            else:
                print("   ✅ Rooms page loaded (no rooms yet)")
        else:
            print(f"   ❌ Rooms failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Rooms error: {e}")
    
    # Test 4: Hotel Customers
    print("\n4. Testing Hotel Customers...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/customers/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            customers_table = soup.find('table')
            if customers_table:
                rows = customers_table.find_all('tr')
                print(f"   ✅ Customers table found with {len(rows)-1} customer rows")
            else:
                print("   ✅ Customers page loaded (no customers yet)")
        else:
            print(f"   ❌ Customers failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Customers error: {e}")
    
    # Test 5: Hotel Payments
    print("\n5. Testing Hotel Payments...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/payments/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            payments_table = soup.find('table')
            if payments_table:
                rows = payments_table.find_all('tr')
                print(f"   ✅ Payments table found with {len(rows)-1} payment rows")
            else:
                print("   ✅ Payments page loaded (no payments yet)")
        else:
            print(f"   ❌ Payments failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Payments error: {e}")
    
    # Test 6: Hotel Reports
    print("\n6. Testing Hotel Reports...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/reports/")
        if response.status_code == 200:
            print("   ✅ Reports page loaded successfully")
        else:
            print(f"   ❌ Reports failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Reports error: {e}")

def test_lodge_management():
    print("\n🏕️ TESTING LODGE MANAGEMENT")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test Lodge Dashboard
    print("\n1. Testing Lodge Dashboard...")
    try:
        response = requests.get(f"{base_url}/properties/lodge/dashboard/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection indicator
            property_badge = soup.find('span', class_='badge')
            if property_badge:
                print(f"   ✅ Property Selection: {property_badge.get_text().strip()}")
            else:
                print("   ❌ Property Selection indicator not found")
            
            # Check for stats cards
            stats_cards = soup.find_all('h4', class_='mb-0')
            if stats_cards:
                print(f"   ✅ Found {len(stats_cards)} stats cards")
                for i, card in enumerate(stats_cards):
                    print(f"      - Card {i+1}: {card.get_text().strip()}")
            else:
                print("   ❌ Stats cards not found")
                
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")

def test_venue_management():
    print("\n🏛️ TESTING VENUE MANAGEMENT")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test Venue Dashboard
    print("\n1. Testing Venue Dashboard...")
    try:
        response = requests.get(f"{base_url}/properties/venue/dashboard/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection indicator
            property_badge = soup.find('span', class_='badge')
            if property_badge:
                print(f"   ✅ Property Selection: {property_badge.get_text().strip()}")
            else:
                print("   ❌ Property Selection indicator not found")
            
            # Check for stats cards
            stats_cards = soup.find_all('h4', class_='mb-0')
            if stats_cards:
                print(f"   ✅ Found {len(stats_cards)} stats cards")
                for i, card in enumerate(stats_cards):
                    print(f"      - Card {i+1}: {card.get_text().strip()}")
            else:
                print("   ❌ Stats cards not found")
                
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")

def test_house_management():
    print("\n🏠 TESTING HOUSE MANAGEMENT")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test House Dashboard
    print("\n1. Testing House Dashboard...")
    try:
        response = requests.get(f"{base_url}/properties/house/dashboard/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection indicator
            property_badge = soup.find('span', class_='badge')
            if property_badge:
                print(f"   ✅ Property Selection: {property_badge.get_text().strip()}")
            else:
                print("   ❌ Property Selection indicator not found")
            
            # Check for stats cards
            stats_cards = soup.find_all('h4', class_='mb-0')
            if stats_cards:
                print(f"   ✅ Found {len(stats_cards)} stats cards")
                for i, card in enumerate(stats_cards):
                    print(f"      - Card {i+1}: {card.get_text().strip()}")
            else:
                print("   ❌ Stats cards not found")
                
        else:
            print(f"   ❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard error: {e}")

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE MANAGEMENT TESTING")
    print("=" * 60)
    
    test_hotel_management()
    test_lodge_management()
    test_venue_management()
    test_house_management()
    
    print("\n✅ TESTING COMPLETE!")
