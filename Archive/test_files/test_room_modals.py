#!/usr/bin/env python3
"""
Simple test to verify room management modals are working
"""

import requests
from bs4 import BeautifulSoup

def test_hotel_rooms_page():
    """Test the hotel rooms page loads correctly"""
    
    BASE_URL = "http://127.0.0.1:8001"
    
    print("Testing Hotel Rooms Page")
    print("=" * 30)
    
    try:
        # Test the main page
        response = requests.get(f"{BASE_URL}/properties/hotel/rooms/")
        print(f"Page Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if modals exist
            modals = soup.find_all('div', class_='modal')
            print(f"Found {len(modals)} modals:")
            
            for modal in modals:
                modal_id = modal.get('id', 'No ID')
                print(f"  - {modal_id}")
            
            # Check if JavaScript functions exist
            scripts = soup.find_all('script')
            js_content = ''.join([script.string or '' for script in scripts])
            
            functions = ['viewRoomDetails', 'editRoom', 'manageRoomStatus', 'deleteRoom']
            for func in functions:
                if func in js_content:
                    print(f"✓ {func} function found")
                else:
                    print(f"✗ {func} function missing")
            
            # Check if API endpoints are referenced
            api_endpoints = ['/properties/api/room/', '/edit/', '/status/', '/delete/']
            for endpoint in api_endpoints:
                if endpoint in js_content:
                    print(f"✓ API endpoint {endpoint} referenced")
                else:
                    print(f"✗ API endpoint {endpoint} missing")
                    
        else:
            print(f"Error: Page returned status {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hotel_rooms_page()
