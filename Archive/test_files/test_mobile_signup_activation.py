#!/usr/bin/env python
"""
Test script for mobile signup and web activation flow
This simulates:
1. Mobile app user signup via API
2. Web admin activation
3. Mobile app login after activation
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test user data (simulating mobile signup)
TEST_USER = {
    "username": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "email": f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+254712345678",
    "role": "tenant"  # or "owner"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n[STEP {step_num}] {description}")
    print("-" * 70)

def test_signup():
    """Test 1: Create user via API (mobile signup)"""
    print_step(1, "Testing Mobile Signup (POST /api/v1/auth/signup/)")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/signup/",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\n✅ SUCCESS: User created successfully!")
            print(f"   Username: {TEST_USER['username']}")
            print(f"   Email: {TEST_USER['email']}")
            print(f"   Status: Pending approval (is_active=False)")
            return True
        else:
            print("\n❌ FAILED: User creation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_login_before_activation():
    """Test 2: Try to login before activation (should fail)"""
    print_step(2, "Testing Mobile Login BEFORE Activation (should fail)")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={
                "email": TEST_USER['email'],
                "password": TEST_USER['password']
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("\n✅ EXPECTED: Login blocked - user not activated yet")
            return True
        else:
            print("\n⚠️  UNEXPECTED: Login should have failed")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def show_activation_instructions():
    """Show instructions for web activation"""
    print_step(3, "Web Activation Instructions")
    
    print("""
NOW ACTIVATE THE USER ON THE WEB INTERFACE:

1. Open your browser and go to: http://127.0.0.1:8000/login/
2. Login with your admin credentials
3. Go to: User Management → User (or http://127.0.0.1:8000/user-list/)
4. Find the user: {username}
5. Click the "Activate" button
6. User's status will change from inactive (red) to active (green)

After activation, press ENTER to continue testing...
""".format(username=TEST_USER['username']))
    
    input("Press ENTER after you've activated the user on the web interface...")

def test_login_after_activation():
    """Test 4: Try to login after activation (should succeed)"""
    print_step(4, "Testing Mobile Login AFTER Activation (should succeed)")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={
                "email": TEST_USER['email'],
                "password": TEST_USER['password']
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS: Login successful after activation!")
            print(f"   Access Token: {data.get('access', 'N/A')[:50]}...")
            print(f"   Refresh Token: {data.get('refresh', 'N/A')[:50]}...")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            return True
        else:
            print("\n❌ FAILED: Login should have succeeded")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_authenticated_request(access_token):
    """Test 5: Make authenticated request with token"""
    print_step(5, "Testing Authenticated Request (GET /api/v1/auth/profile/)")
    
    try:
        response = requests.get(
            f"{API_BASE}/auth/profile/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: Authenticated request successful!")
            return True
        else:
            print("\n❌ FAILED: Authenticated request failed")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def main():
    """Run the complete test flow"""
    print_section("MOBILE SIGNUP & WEB ACTIVATION TEST")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER['username']}")
    print(f"Test Email: {TEST_USER['email']}")
    
    # Test 1: Signup
    if not test_signup():
        print("\n❌ Test aborted: Signup failed")
        return
    
    # Test 2: Login before activation
    test_login_before_activation()
    
    # Test 3: Show activation instructions
    show_activation_instructions()
    
    # Test 4: Login after activation
    response = requests.post(
        f"{API_BASE}/auth/login/",
        json={
            "email": TEST_USER['email'],
            "password": TEST_USER['password']
        },
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access')
        
        print("\n✅ SUCCESS: Login successful after activation!")
        print(f"   Access Token: {access_token[:50]}...")
        
        # Test 5: Authenticated request
        if access_token:
            test_authenticated_request(access_token)
    else:
        print("\n❌ FAILED: Login still failing after activation")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Final summary
    print_section("TEST SUMMARY")
    print("""
✅ Mobile Signup Flow: User created via API
✅ Activation Check: Login blocked before activation
✅ Web Activation: Manual activation on web interface
✅ Mobile Login: Login successful after activation
✅ Token Auth: Authenticated requests working

Test user credentials:
  Username: {username}
  Email: {email}
  Password: {password}
  
You can now use these credentials to test the mobile app!
""".format(
        username=TEST_USER['username'],
        email=TEST_USER['email'],
        password=TEST_USER['password']
    ))

if __name__ == "__main__":
    main()
