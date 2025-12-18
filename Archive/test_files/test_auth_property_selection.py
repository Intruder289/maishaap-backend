#!/usr/bin/env python
import requests
import json
from bs4 import BeautifulSoup

def test_property_selection_authenticated():
    print("TESTING PROPERTY SELECTION WITH AUTHENTICATION")
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
        
        if login_post.status_code == 200:
            print("   Login attempt completed")
        else:
            print("   Login failed")
            
    except Exception as e:
        print(f"   Login error: {e}")
        return
    
    # Step 3: Test Hotel Property Selection
    print("\n3. Testing Hotel Property Selection...")
    try:
        response = session.get(f"{base_url}/properties/hotel/select-property/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection content
            if "Property Selection" in response.text:
                print("   Property Selection page loaded successfully")
            else:
                print("   Property Selection content not found")
                
            # Check for hotel properties
            if "Grand Hotel" in response.text:
                print("   Hotel properties found in page")
            else:
                print("   Hotel properties not found")
                
            # Check for template content
            if "Work with All Properties" in response.text:
                print("   Template content found")
            else:
                print("   Template content not found")
                
        else:
            print(f"   Hotel selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Hotel selection error: {e}")

if __name__ == "__main__":
    test_property_selection_authenticated()
