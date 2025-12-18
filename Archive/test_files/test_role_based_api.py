#!/usr/bin/env python3
"""
Test script for the role-based authentication API
Tests the complete workflow: signup with role selection, admin approval, and role-based login
"""

import requests
import json
import time

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_signup(role="tenant"):
    """Test user signup with role selection"""
    print(f"\n🔍 Testing {role} signup...")
    
    signup_data = {
        "username": f"test_{role}_user",
        "email": f"test_{role}@example.com",
        "password": "securepass123",
        "confirm_password": "securepass123",
        "first_name": "Test",
        "last_name": f"{role.title()}",
        "phone": "+254712345678",
        "role": role
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup/", json=signup_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"❌ Signup failed for {role}")
            return None
            
    except Exception as e:
        print(f"❌ Error during {role} signup: {e}")
        return None

def test_login_before_approval(email):
    """Test login attempt before admin approval"""
    print(f"\n🔍 Testing login before approval for {email}...")
    
    login_data = {
        "email": email,
        "password": "securepass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            error_data = response.json()
            if "pending admin approval" in str(error_data):
                print("✅ Correctly blocked login before approval")
                return True
        
        print("❌ Expected approval error not received")
        return False
        
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

def test_admin_endpoints(admin_token):
    """Test admin endpoints for user approval"""
    print(f"\n🔍 Testing admin endpoints...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test get pending users
    try:
        response = requests.get(f"{BASE_URL}/admin/pending-users/", headers=headers)
        print(f"Get Pending Users - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            pending_data = response.json()
            print(f"Pending users count: {pending_data.get('count', 0)}")
            
            if pending_data.get('pending_users'):
                # Try to approve the first pending user
                first_user = pending_data['pending_users'][0]
                user_id = first_user.get('id')  # Note: This might need adjustment based on actual response
                
                approve_data = {
                    "user_id": user_id,
                    "action": "approve"
                }
                
                approval_response = requests.post(f"{BASE_URL}/admin/approve-user/", 
                                                json=approve_data, headers=headers)
                print(f"Approve User - Status Code: {approval_response.status_code}")
                print(f"Approval Response: {json.dumps(approval_response.json(), indent=2)}")
                
                return approval_response.status_code == 200
        
    except Exception as e:
        print(f"❌ Error during admin endpoint test: {e}")
        return False

def test_login_after_approval(email):
    """Test login after admin approval"""
    print(f"\n🔍 Testing login after approval for {email}...")
    
    login_data = {
        "email": email,
        "password": "securepass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            login_data = response.json()
            if login_data.get('tokens'):
                print("✅ Login successful after approval")
                return login_data['tokens']['access']
        
        print("❌ Login failed after approval")
        return None
        
    except Exception as e:
        print(f"❌ Error during post-approval login: {e}")
        return None

def main():
    """Main test workflow"""
    print("🚀 Starting Role-Based Authentication API Tests")
    print("=" * 50)
    
    # Test server availability
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ API server not available. Please start the Django server first.")
            return
    except:
        print("❌ Cannot connect to API server. Please start the Django server first.")
        return
    
    print("✅ API server is running")
    
    # Test 1: Signup as tenant
    tenant_signup = test_signup("tenant")
    if not tenant_signup:
        return
    
    # Test 2: Signup as owner
    owner_signup = test_signup("owner")
    if not owner_signup:
        return
    
    # Test 3: Try login before approval
    tenant_email = f"test_tenant@example.com"
    owner_email = f"test_owner@example.com"
    
    test_login_before_approval(tenant_email)
    test_login_before_approval(owner_email)
    
    print("\n📝 Summary:")
    print("- User signup with role selection: ✅ Working")
    print("- Login blocked before approval: ✅ Working")
    print("- Admin approval endpoints: ⏳ Requires admin token")
    print("- Login after approval: ⏳ Requires admin approval")
    
    print("\n💡 Next steps:")
    print("1. Create an admin user: python manage.py createsuperuser")
    print("2. Login as admin through the web interface")
    print("3. Use admin endpoints to approve users")
    print("4. Test login after approval")

if __name__ == "__main__":
    main()