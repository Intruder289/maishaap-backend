#!/usr/bin/env python3
"""
Test script to verify room management modals work with authentication
"""

import requests
from bs4 import BeautifulSoup

def test_authenticated_room_management():
    """Test the room management page with authentication"""
    
    BASE_URL = "http://127.0.0.1:8001"
    
    print("Testing Authenticated Room Management")
    print("=" * 40)
    
    # Create a session to maintain login state
    session = requests.Session()
    
    try:
        # Step 1: Login
        print("1. Logging in...")
        login_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'csrfmiddlewaretoken': ''  # We'll get this from the login page
        }
        
        # Get login page to get CSRF token
        login_page = session.get(f"{BASE_URL}/accounts/login/")
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
        
        if csrf_token:
            login_data['csrfmiddlewaretoken'] = csrf_token['value']
            print("✓ CSRF token obtained")
        else:
            print("✗ CSRF token not found")
            return
        
        # Perform login
        login_response = session.post(f"{BASE_URL}/accounts/login/", data=login_data)
        print(f"Login response: {login_response.status_code}")
        
        if login_response.status_code == 200 and 'dashboard' in login_response.url:
            print("✓ Login successful")
        else:
            print("✗ Login failed")
            return
        
        # Step 2: Access hotel rooms page
        print("\n2. Accessing hotel rooms page...")
        rooms_response = session.get(f"{BASE_URL}/properties/hotel/rooms/")
        print(f"Rooms page status: {rooms_response.status_code}")
        
        if rooms_response.status_code == 200:
            soup = BeautifulSoup(rooms_response.content, 'html.parser')
            
            # Check for modals
            modals = soup.find_all('div', class_='modal')
            print(f"✓ Found {len(modals)} modals:")
            for modal in modals:
                modal_id = modal.get('id', 'No ID')
                print(f"  - {modal_id}")
            
            # Check for JavaScript functions
            scripts = soup.find_all('script')
            js_content = ''.join([script.string or '' for script in scripts])
            
            functions = ['viewRoomDetails', 'editRoom', 'manageRoomStatus', 'deleteRoom']
            print(f"\n3. Checking JavaScript functions:")
            for func in functions:
                if func in js_content:
                    print(f"✓ {func} function found")
                else:
                    print(f"✗ {func} function missing")
            
            # Check for API endpoints
            api_endpoints = ['/properties/api/room/', '/edit/', '/status/', '/delete/']
            print(f"\n4. Checking API endpoints:")
            for endpoint in api_endpoints:
                if endpoint in js_content:
                    print(f"✓ API endpoint {endpoint} referenced")
                else:
                    print(f"✗ API endpoint {endpoint} missing")
            
            # Check for rooms table
            rooms_table = soup.find('table', {'id': 'rooms-table'})
            if rooms_table:
                print(f"\n5. ✓ Rooms table found")
                rows = rooms_table.find_all('tr')
                print(f"   Found {len(rows)} table rows")
            else:
                print(f"\n5. ✗ Rooms table not found")
                
        else:
            print(f"✗ Failed to access rooms page: {rooms_response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_authenticated_room_management()
