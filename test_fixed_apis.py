#!/usr/bin/env python
"""
Test script for the three fixed APIs:
1. Image Upload API - verify image field is available and works
2. Phone Login API - verify phone login works with different formats
3. Manager Login - verify managers can login via mobile app
"""

import requests
import json
import os
import sys
from io import BytesIO
from PIL import Image

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base URL - adjust if your server runs on a different port
BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_section(title):
    """Print a section divider"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_response(status_code, response_data, endpoint=""):
    """Print formatted response"""
    status_marker = "✅ [OK]" if status_code < 400 else "❌ [FAIL]"
    print(f"\n{status_marker} Status: {status_code}")
    if endpoint:
        print(f"Endpoint: {endpoint}")
    if isinstance(response_data, dict):
        print(f"Response: {json.dumps(response_data, indent=2)[:800]}")
    else:
        print(f"Response: {str(response_data)[:800]}")
    return status_code < 400

def create_test_image():
    """Create a simple test image in memory"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_phone_login():
    """Test phone number login with different formats"""
    print_section("TEST 1: Phone Number Login")
    
    # Test cases - adjust these to match your test user's phone number
    test_cases = [
        {
            "name": "Phone with country code",
            "data": {"phone": "+255674367492", "password": "Msebenze@123"}
        },
        {
            "name": "Phone without +",
            "data": {"phone": "255674367492", "password": "Msebenze@123"}
        },
        {
            "name": "Phone without country code",
            "data": {"phone": "0674367492", "password": "Msebenze@123"}
        },
        {
            "name": "Phone with spaces",
            "data": {"phone": "+255 674 367 492", "password": "Msebenze@123"}
        },
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login/",
                json=test_case['data'],
                timeout=10
            )
            success = print_response(response.status_code, response.json() if response.text else {}, 
                                   f"POST {BASE_URL}/auth/login/")
            results.append({
                "test": test_case['name'],
                "success": success,
                "status": response.status_code
            })
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

def test_email_login():
    """Test email login for comparison"""
    print_section("TEST 2: Email Login (for comparison)")
    
    # Adjust to match your test user
    test_data = {
        "email": "test@example.com",  # Change this
        "password": "testpassword"  # Change this
    }
    
    print(f"\n--- Testing Email Login ---")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=test_data,
            timeout=10
        )
        success = print_response(response.status_code, response.json() if response.text else {},
                               f"POST {BASE_URL}/auth/login/")
        return {"success": success, "status": response.status_code, "response": response.json() if response.text else {}}
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"success": False, "error": str(e)}

def test_manager_login():
    """Test manager login"""
    print_section("TEST 3: Manager Login")
    
    # Adjust to match your manager user
    test_data = {
        "email": "manager@example.com",  # Change this to a manager's email
        "password": "managerpassword"  # Change this
    }
    
    print(f"\n--- Testing Manager Login ---")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=test_data,
            timeout=10
        )
        success = print_response(response.status_code, response.json() if response.text else {},
                               f"POST {BASE_URL}/auth/login/")
        
        if success and response.status_code == 200:
            user_data = response.json().get('user', {})
            roles = user_data.get('role', [])
            print(f"\nUser roles: {roles}")
            if 'Manager' in roles or any('manager' in str(r).lower() for r in roles):
                print("✅ Manager role detected - login successful!")
            else:
                print("⚠️  Warning: Manager role not found in response")
        
        return {"success": success, "status": response.status_code}
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"success": False, "error": str(e)}

def test_image_upload_api_structure():
    """Test that image upload API shows image field in Swagger/response"""
    print_section("TEST 4: Image Upload API Structure")
    
    # First, login to get a token
    print("\n--- Step 1: Login to get token ---")
    login_data = {
        "email": "test@example.com",  # Change this
        "password": "testpassword"  # Change this
    }
    
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return {"success": False, "error": "Login failed"}
        
        tokens = login_response.json().get('tokens', {})
        access_token = tokens.get('access')
        
        if not access_token:
            print("❌ No access token received")
            return {"success": False, "error": "No access token"}
        
        print(f"✅ Login successful, token received")
        
        # Get user's properties
        print("\n--- Step 2: Get user's properties ---")
        headers = {"Authorization": f"Bearer {access_token}"}
        properties_response = requests.get(
            f"{BASE_URL}/my-properties/",
            headers=headers,
            timeout=10
        )
        
        if properties_response.status_code != 200:
            print(f"⚠️  Could not get properties: {properties_response.status_code}")
            print("Note: You need at least one property to test image upload")
            return {"success": False, "error": "No properties found"}
        
        properties = properties_response.json()
        if not properties or len(properties) == 0:
            print("⚠️  No properties found. Cannot test image upload.")
            return {"success": False, "error": "No properties found"}
        
        property_id = properties[0].get('id')
        print(f"✅ Found property ID: {property_id}")
        
        # Test image upload
        print("\n--- Step 3: Test image upload with multipart/form-data ---")
        test_image = create_test_image()
        
        files = {
            'image': ('test_image.png', test_image, 'image/png')
        }
        data = {
            'property': property_id,
            'caption': 'Test image upload',
            'is_primary': False,
            'order': 0
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/property-images/",
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        
        success = print_response(upload_response.status_code, 
                               upload_response.json() if upload_response.text else {},
                               f"POST {BASE_URL}/property-images/")
        
        if success:
            response_data = upload_response.json()
            if 'image' in response_data:
                print("✅ Image field present in response!")
            else:
                print("⚠️  Warning: Image field not found in response")
        
        return {"success": success, "status": upload_response.status_code}
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  API TESTING SCRIPT")
    print("  Testing: Image Upload, Phone Login, Manager Login")
    print("="*80)
    
    print("\n⚠️  NOTE: Please update the test credentials in this script")
    print("   before running the tests!")
    print("\n   You need to set:")
    print("   - Test user email/password for login")
    print("   - Test user phone number (for phone login test)")
    print("   - Manager user email/password (for manager login test)")
    
    input("\nPress Enter to continue or Ctrl+C to cancel...")
    
    results = {
        "phone_login": test_phone_login(),
        "email_login": test_email_login(),
        "manager_login": test_manager_login(),
        "image_upload": test_image_upload_api_structure()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    for test_name, result in results.items():
        if isinstance(result, list):
            print(f"\n{test_name}:")
            for item in result:
                status = "✅" if item.get('success') else "❌"
                print(f"  {status} {item.get('test', 'Unknown')}: {item.get('status', 'N/A')}")
        else:
            status = "✅" if result.get('success') else "❌"
            print(f"{status} {test_name}: {result.get('status', 'N/A')}")
    
    print("\n" + "="*80)
    print("  Testing Complete")
    print("="*80)

if __name__ == "__main__":
    main()

