#!/usr/bin/env python
import requests
import json
from bs4 import BeautifulSoup

def test_property_selection_detailed():
    print("TESTING PROPERTY SELECTION DETAILED")
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
        
        # Check if login was successful by looking for redirect
        if login_post.status_code == 302:
            print("   Login successful (redirect detected)")
        elif login_post.status_code == 200:
            if "dashboard" in login_post.text.lower() or "logout" in login_post.text.lower():
                print("   Login successful (dashboard content detected)")
            else:
                print("   Login may have failed")
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
        print(f"   Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            # Check for specific content
            content = response.text
            
            if "Property Selection" in content:
                print("   Property Selection content found")
            else:
                print("   Property Selection content NOT found")
                
            if "Hotel Management" in content:
                print("   Hotel Management content found")
            else:
                print("   Hotel Management content NOT found")
                
            if "Grand Hotel" in content:
                print("   Grand Hotel content found")
            else:
                print("   Grand Hotel content NOT found")
                
            if "Work with All Properties" in content:
                print("   Work with All Properties content found")
            else:
                print("   Work with All Properties content NOT found")
                
            # Check for authentication redirect
            if "login" in content.lower() and "password" in content.lower():
                print("   Authentication redirect detected")
            else:
                print("   No authentication redirect detected")
                
        else:
            print(f"   Hotel selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Hotel selection error: {e}")

if __name__ == "__main__":
    test_property_selection_detailed()
