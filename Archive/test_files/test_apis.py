#!/usr/bin/env python
"""
Comprehensive API Testing Script for Maisha Backend
Tests all available API endpoints
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

def print_section(title):
    """Print a section divider"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_response(status_code, response_data, endpoint=""):
    """Print formatted response"""
    status_emoji = "[OK]" if status_code < 400 else "[FAIL]"
    print(f"\n{status_emoji} Status: {status_code}")
    if endpoint:
        print(f"Endpoint: {endpoint}")
    if isinstance(response_data, dict):
        print(f"Response: {json.dumps(response_data, indent=2)}")
    else:
        print(f"Response: {response_data}")

def test_api_root():
    """Test API root endpoint"""
    print_section("Testing API Root")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        try:
            response_data = response.json()
        except:
            response_data = response.text[:200]  # First 200 chars
        print_response(response.status_code, response_data, "GET /api/v1/")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Error: Cannot connect to server. Is the server running?")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_properties_endpoints():
    """Test Properties API endpoints"""
    print_section("Testing Properties API")
    
    endpoints = [
        ("GET", "/properties/", "List all properties"),
        ("GET", "/property-types/", "List property types"),
        ("GET", "/regions/", "List regions"),
        ("GET", "/amenities/", "List amenities"),
        ("GET", "/featured/", "Featured properties"),
        ("GET", "/recent/", "Recent properties"),
    ]
    
    results = []
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            status = "[OK]" if response.status_code < 400 else "[FAIL]"
            print(f"{status} {method} {endpoint} - {description} (Status: {response.status_code})")
            results.append(response.status_code < 400)
        except Exception as e:
            print(f"[FAIL] {method} {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_rent_endpoints():
    """Test Rent API endpoints"""
    print_section("Testing Rent API")
    
    endpoints = [
        ("GET", "/rent/invoices/", "List rent invoices"),
        ("GET", "/rent/payments/", "List rent payments"),
        ("GET", "/rent/late-fees/", "List late fees"),
        ("GET", "/rent/reminders/", "List rent reminders"),
        ("GET", "/rent/dashboard/", "Rent dashboard"),
    ]
    
    results = []
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            status = "[OK]" if response.status_code < 400 else "[FAIL]"
            print(f"{status} {method} {endpoint} - {description} (Status: {response.status_code})")
            results.append(response.status_code < 400)
        except Exception as e:
            print(f"[FAIL] {method} {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_payments_endpoints():
    """Test Payments API endpoints"""
    print_section("Testing Payments API")
    
    endpoints = [
        ("GET", "/payments/providers/", "List payment providers"),
        ("GET", "/payments/invoices/", "List invoices"),
        ("GET", "/payments/payments/", "List payments"),
        ("GET", "/payments/transactions/", "List transactions"),
        ("GET", "/payments/expenses/", "List expenses"),
    ]
    
    results = []
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            status = "[OK]" if response.status_code < 400 else "[FAIL]"
            print(f"{status} {method} {endpoint} - {description} (Status: {response.status_code})")
            results.append(response.status_code < 400)
        except Exception as e:
            print(f"[FAIL] {method} {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_maintenance_endpoints():
    """Test Maintenance API endpoints"""
    print_section("Testing Maintenance API")
    
    endpoints = [
        ("GET", "/maintenance/requests/", "List maintenance requests"),
    ]
    
    results = []
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            status = "[OK]" if response.status_code < 400 else "[FAIL]"
            print(f"{status} {method} {endpoint} - {description} (Status: {response.status_code})")
            results.append(response.status_code < 400)
        except Exception as e:
            print(f"[FAIL] {method} {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_auth_endpoints():
    """Test Authentication API endpoints"""
    print_section("Testing Authentication API")
    
    # Test signup
    test_user_data = {
        "username": f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+254712345678",
        "role": "tenant"
    }
    
    try:
        # Signup
        print("\n[TEST] Testing Signup...")
        response = requests.post(f"{BASE_URL}/auth/signup/", json=test_user_data, timeout=5)
        try:
            response_data = response.json()
        except:
            response_data = response.text[:200]
        print_response(response.status_code, response_data, "POST /auth/signup/")
        signup_success = response.status_code == 201
        
        # Get profile (will fail without auth token for now)
        print("\n[TEST] Testing Get Profile (without auth)...")
        response = requests.get(f"{BASE_URL}/auth/profile/", timeout=5)
        try:
            response_data = response.json()
        except:
            response_data = response.text[:100]
        print_response(response.status_code, response_data, "GET /auth/profile/")
        profile_success = response.status_code in [401, 403]  # Expected to fail without token
        
        return signup_success and profile_success
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def test_search_endpoints():
    """Test Search API endpoints"""
    print_section("Testing Search API")
    
    endpoints = [
        ("POST", "/search/", "Property search"),
    ]
    
    results = []
    for method, endpoint, description in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            search_data = {
                "search": "apartment",
                "min_rent": 500,
                "max_rent": 2000
            }
            response = requests.post(url, json=search_data, timeout=5)
            status = "[OK]" if response.status_code < 400 else "[FAIL]"
            print(f"{status} {method} {endpoint} - {description} (Status: {response.status_code})")
            results.append(response.status_code < 400)
        except requests.exceptions.ConnectionError:
            print(f"[FAIL] {method} {endpoint} - Error: Cannot connect to server")
            results.append(False)
        except Exception as e:
            print(f"[FAIL] {method} {endpoint} - Error: {e}")
            results.append(False)
    
    return all(results)

def generate_test_report(results):
    """Generate a test summary report"""
    print_section("TEST SUMMARY REPORT")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r)
    failed_tests = total_tests - passed_tests
    
    print(f"\n[SUMMARY] Total Tests: {total_tests}")
    print(f"[PASS] Passed: {passed_tests}")
    print(f"[FAIL] Failed: {failed_tests}")
    print(f"[RATE] Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n[SUCCESS] All API endpoints are working correctly!")
    else:
        print(f"\n[WARNING] {failed_tests} endpoint(s) need attention")

def main():
    """Main test function"""
    print("\n" + "="*80)
    print("  MAISHA BACKEND API TESTING SUITE")
    print("="*80)
    print(f"\nTesting API endpoints at: {BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run all tests
    results.append(("API Root", test_api_root()))
    results.append(("Properties", test_properties_endpoints()))
    results.append(("Rent", test_rent_endpoints()))
    results.append(("Payments", test_payments_endpoints()))
    results.append(("Maintenance", test_maintenance_endpoints()))
    results.append(("Authentication", test_auth_endpoints()))
    results.append(("Search", test_search_endpoints()))
    
    # Generate report
    test_results = [result for _, result in results]
    generate_test_report(test_results)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

