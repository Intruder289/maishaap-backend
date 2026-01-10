"""
Test script for Reports API endpoints
Tests all report endpoints to verify they return correct data
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"  # Adjust if your server runs on different port
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials - Updated from database
TEST_ADMIN = {
    "email": "admin@maisha.com",
    "password": "test123456"
}

TEST_OWNER = {
    "email": "july@maisha.com",
    "password": "test123456"
}

TEST_TENANT = {
    "email": "manager@maisha.com",
    "password": "test123456"
}


def get_auth_token(email, password):
    """Get JWT token for authentication"""
    url = f"{API_BASE}/auth/login/"
    data = {"email": email, "password": password}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json().get("access")
        print(f"❌ Login failed for {email}: {response.status_code} - {response.text}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {BASE_URL}")
        print(f"   Make sure the Django server is running!")
        return None
    except Exception as e:
        print(f"❌ Error getting token for {email}: {str(e)}")
        return None


def test_endpoint(name, url, token=None, method="GET", data=None):
    """Test an API endpoint"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Check if data is real (not all zeros/empty)
            if isinstance(result, dict):
                has_real_data = False
                for key, value in result.items():
                    if isinstance(value, (int, float)) and value != 0:
                        has_real_data = True
                        break
                    elif isinstance(value, list) and len(value) > 0:
                        has_real_data = True
                        break
                    elif isinstance(value, dict) and len(value) > 0:
                        has_real_data = True
                        break
                
                if has_real_data:
                    print("✅ Contains real data (not all zeros/empty)")
                else:
                    print("⚠️  Warning: Response contains only zeros/empty data")
            
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Make sure the server is running at {BASE_URL}")
        return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None


def test_reports_endpoints():
    """Test all reports API endpoints"""
    print("\n" + "="*60)
    print("REPORTS API ENDPOINT TESTS")
    print("="*60)
    
    # Get tokens for different user roles
    admin_token = get_auth_token(TEST_ADMIN["email"], TEST_ADMIN["password"])
    owner_token = get_auth_token(TEST_OWNER["email"], TEST_OWNER["password"])
    tenant_token = get_auth_token(TEST_TENANT["email"], TEST_TENANT["password"])
    
    if not admin_token:
        print("\n⚠️  Warning: Could not get admin token. Some tests may fail.")
        print("Please update TEST_ADMIN credentials in the script.")
    
    # Test endpoints
    endpoints = [
        ("Financial Summary", f"{API_BASE}/reports/financial/summary/", admin_token),
        ("Rent Collection Report", f"{API_BASE}/reports/financial/rent-collection/", admin_token),
        ("Expense Report", f"{API_BASE}/reports/financial/expenses/", admin_token),
        ("Property Occupancy Report", f"{API_BASE}/reports/properties/occupancy/", admin_token),
        ("Maintenance Report", f"{API_BASE}/reports/properties/maintenance/", admin_token),
        ("Dashboard Statistics", f"{API_BASE}/reports/dashboard/stats/", admin_token),
        ("Dashboard Charts", f"{API_BASE}/reports/dashboard/charts/", admin_token),
    ]
    
    results = {}
    
    for name, url, token in endpoints:
        result = test_endpoint(name, url, token)
        results[name] = result
    
    # Test with different user roles
    print("\n" + "="*60)
    print("TESTING MULTI-TENANCY (Data Isolation)")
    print("="*60)
    
    if owner_token:
        print("\nTesting as Owner:")
        test_endpoint("Financial Summary (Owner)", f"{API_BASE}/reports/financial/summary/", owner_token)
    
    if tenant_token:
        print("\nTesting as Tenant:")
        test_endpoint("Financial Summary (Tenant)", f"{API_BASE}/reports/financial/summary/", tenant_token)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"Total Endpoints Tested: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("\n✅ All endpoints are working!")
    else:
        print(f"\n⚠️  {total_count - success_count} endpoint(s) failed")
    
    return results


if __name__ == "__main__":
    print("Reports API Test Script")
    print("="*60)
    print("Make sure your Django server is running!")
    print("Update test credentials at the top of this script if needed.")
    print("="*60)
    
    test_reports_endpoints()
