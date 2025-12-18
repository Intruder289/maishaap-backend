#!/usr/bin/env python
import requests
import json
from bs4 import BeautifulSoup

def authenticate_and_test():
    print("AUTHENTICATING AND TESTING MANAGEMENT SYSTEM")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8001"
    session = requests.Session()
    
    # Step 1: Get login page
    print("\n1. Getting login page...")
    try:
        login_response = session.get(f"{base_url}/accounts/login/")
        if login_response.status_code == 200:
            print("   Login page loaded successfully")
        else:
            print(f"   Login page failed: {login_response.status_code}")
            return
    except Exception as e:
        print(f"   Login page error: {e}")
        return
    
    # Step 2: Login
    print("\n2. Attempting login...")
    try:
        # Extract CSRF token
        soup = BeautifulSoup(login_response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_token:
            csrf_value = csrf_token.get('value')
            print(f"   CSRF token found: {csrf_value[:20]}...")
        else:
            print("   CSRF token not found")
            return
        
        # Login data
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrfmiddlewaretoken': csrf_value
        }
        
        login_post = session.post(f"{base_url}/accounts/login/", data=login_data)
        print(f"   Login response: {login_post.status_code}")
        
        if login_post.status_code == 200 and "dashboard" in login_post.text.lower():
            print("   Login successful!")
        else:
            print("   Login failed, trying with different credentials...")
            # Try with property_manager1
            login_data['username'] = 'property_manager1'
            login_data['password'] = 'password123'
            login_post = session.post(f"{base_url}/accounts/login/", data=login_data)
            print(f"   Second login attempt: {login_post.status_code}")
            
    except Exception as e:
        print(f"   Login error: {e}")
        return
    
    # Step 3: Test Hotel Dashboard
    print("\n3. Testing Hotel Dashboard...")
    try:
        response = session.get(f"{base_url}/properties/hotel/dashboard/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection
            property_badge = soup.find('span', class_='badge')
            if property_badge:
                print(f"   Property Selection: {property_badge.get_text().strip()}")
            else:
                print("   Property Selection: NOT FOUND")
            
            # Check for stats cards
            stats_cards = soup.find_all('h4', class_='mb-0')
            if stats_cards:
                print(f"   Stats Cards: Found {len(stats_cards)} cards")
                for i, card in enumerate(stats_cards):
                    print(f"      - Card {i+1}: {card.get_text().strip()}")
            else:
                print("   Stats Cards: NOT FOUND")
            
            # Check for New Booking button
            booking_btn = soup.find('a', href=lambda x: x and 'create_hotel_booking' in x)
            if booking_btn:
                print("   New Booking Button: FOUND")
            else:
                print("   New Booking Button: NOT FOUND")
                
        else:
            print(f"   Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"   Dashboard error: {e}")
    
    # Step 4: Test Hotel Bookings
    print("\n4. Testing Hotel Bookings...")
    try:
        response = session.get(f"{base_url}/properties/hotel/bookings/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            bookings_table = soup.find('table')
            if bookings_table:
                rows = bookings_table.find_all('tr')
                print(f"   Bookings Table: Found with {len(rows)-1} booking rows")
            else:
                print("   Bookings Table: No table found (no bookings yet)")
        else:
            print(f"   Bookings failed: {response.status_code}")
    except Exception as e:
        print(f"   Bookings error: {e}")
    
    # Step 5: Test Hotel Rooms
    print("\n5. Testing Hotel Rooms...")
    try:
        response = session.get(f"{base_url}/properties/hotel/rooms/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rooms_table = soup.find('table')
            if rooms_table:
                rows = rooms_table.find_all('tr')
                print(f"   Rooms Table: Found with {len(rows)-1} room rows")
            else:
                print("   Rooms Table: No table found (no rooms yet)")
        else:
            print(f"   Rooms failed: {response.status_code}")
    except Exception as e:
        print(f"   Rooms error: {e}")

if __name__ == "__main__":
    authenticate_and_test()
