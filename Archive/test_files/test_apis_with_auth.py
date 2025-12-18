#!/usr/bin/env python
"""
Comprehensive API Testing Script with Authentication
Tests all available API endpoints including protected ones with JWT tokens
"""

import requests
import json
from datetime import datetime
import sys

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Base URL
BASE_URL = "http://127.0.0.1:8001/api/v1"

# Test credentials (approved test user)
TEST_USER = {
    "email": "api_test@example.com",
    "password": "test123"
}

def print_section(title):
    """Print a section divider"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_response(status_code, response_data, endpoint=""):
    """Print formatted response"""
    status_marker = "[OK]" if status_code < 400 else "[FAIL]"
    print(f"\n{status_marker} Status: {status_code}")
    if endpoint:
        print(f"Endpoint: {endpoint}")
    if isinstance(response_data, dict):
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")  # First 500 chars
    else:
        print(f"Response: {str(response_data)[:500]}")
    return status_code < 400

def login():
    """Login and get JWT token"""
    print_section("Logging in to get JWT Token")
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=TEST_USER, timeout=5)
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('tokens', {}).get('access', '')
            print(f"[OK] Login successful - Token obtained")
            return access_token
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"[FAIL] Login error: {e}")
        return None

def test_with_auth(endpoint, method="GET", data=None, token=None):
    """Test endpoint with authentication"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=5)
        
        try:
            response_data = response.json()
        except:
            response_data = response.text[:200]
        
        return print_response(response.status_code, response_data, f"{method} {endpoint}")
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("  MAISHA BACKEND API TESTING SUITE WITH AUTHENTICATION")
    print("="*80)
    print(f"\nTesting API endpoints at: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Login to get JWT token
    token = login()
    
    if not token:
        print("\n[FAIL] Cannot proceed without authentication token")
        return
    
    results = []
    
    # Step 2: Test authenticated endpoints
    print_section("Testing Protected Endpoints with Authentication")
    
    # Profile endpoints
    print("\n[TEST] Testing Profile Endpoints...")
    results.append(test_with_auth("/auth/profile/", "GET", token=token))
    
    # Properties endpoints (some require auth)
    print("\n[TEST] Testing Properties Endpoints...")
    results.append(test_with_auth("/my-properties/", "GET", token=token))
    
    # Rent endpoints
    print("\n[TEST] Testing Rent Endpoints...")
    results.append(test_with_auth("/rent/invoices/", "GET", token=token))
    results.append(test_with_auth("/rent/payments/", "GET", token=token))
    results.append(test_with_auth("/rent/late-fees/", "GET", token=token))
    results.append(test_with_auth("/rent/reminders/", "GET", token=token))
    
    # Payments endpoints
    print("\n[TEST] Testing Payments Endpoints...")
    results.append(test_with_auth("/payments/providers/", "GET", token=token))
    results.append(test_with_auth("/payments/invoices/", "GET", token=token))
    results.append(test_with_auth("/payments/payments/", "GET", token=token))
    
    # Maintenance endpoints
    print("\n[TEST] Testing Maintenance Endpoints...")
    results.append(test_with_auth("/maintenance/requests/", "GET", token=token))
    
    # Step 3: Generate summary
    print_section("TEST SUMMARY REPORT")
    
    total_tests = len(results)
    passed_tests = sum(results)
    failed_tests = total_tests - passed_tests
    
    print(f"\n[SUMMARY] Total Tests: {total_tests}")
    print(f"[PASS] Passed: {passed_tests}")
    print(f"[FAIL] Failed: {failed_tests}")
    if total_tests > 0:
        print(f"[RATE] Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n[SUCCESS] All protected API endpoints are working correctly!")
    else:
        print(f"\n[WARNING] {failed_tests} endpoint(s) need attention")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

