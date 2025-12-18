"""
Test script for Property Visit Payment API endpoints
Run this after starting the Django server to test the endpoints
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"  # Adjust if your server runs on different port
API_BASE = f"{BASE_URL}/api/v1"

# You'll need to get these from your actual login
JWT_TOKEN = "YOUR_JWT_TOKEN_HERE"  # Get this from /api/v1/auth/login/
PROPERTY_ID = 1  # Replace with an actual house property ID

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def test_visit_status():
    """Test GET /api/v1/properties/{id}/visit/status/"""
    print("\n=== Testing Visit Status Endpoint ===")
    url = f"{API_BASE}/properties/{PROPERTY_ID}/visit/status/"
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_visit_initiate():
    """Test POST /api/v1/properties/{id}/visit/initiate/"""
    print("\n=== Testing Visit Initiate Endpoint ===")
    url = f"{API_BASE}/properties/{PROPERTY_ID}/visit/initiate/"
    data = {
        "payment_method": "online"
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_visit_verify(transaction_id):
    """Test POST /api/v1/properties/{id}/visit/verify/"""
    print("\n=== Testing Visit Verify Endpoint ===")
    url = f"{API_BASE}/properties/{PROPERTY_ID}/visit/verify/"
    data = {
        "transaction_id": transaction_id
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

if __name__ == "__main__":
    print("Property Visit Payment API Test Script")
    print("=" * 50)
    print(f"Testing property ID: {PROPERTY_ID}")
    print(f"API Base URL: {API_BASE}")
    
    # Step 1: Check status
    status_response = test_visit_status()
    
    # Step 2: If not paid, initiate payment
    if not status_response.get('has_paid', False):
        initiate_response = test_visit_initiate()
        transaction_id = initiate_response.get('transaction_id')
        
        if transaction_id:
            # Step 3: Verify payment (this will use placeholder gateway response)
            test_visit_verify(transaction_id)
    else:
        print("\n✓ User has already paid - contact info should be in status response")

