"""
Test AZAMpay Authentication for Checkout Endpoint
"""

import os
import sys
import django
import requests
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings
from payments.gateway_service import AZAMPayGateway

def test_auth():
    print("="*80)
    print("AZAMpay Authentication Test")
    print("="*80)
    
    config = AZAMPayGateway.AZAM_PAY_CONFIG
    base_url = AZAMPayGateway.get_base_url()
    
    print(f"\nConfiguration:")
    print(f"  Base URL: {base_url}")
    print(f"  Client ID: {config.get('client_id', 'Not set')[:30]}...")
    print(f"  API Key: {config.get('api_key', 'Not set')[:30]}...")
    print(f"  App Name: {config.get('app_name')}")
    print(f"  Dashboard Token: {'Set' if config.get('dashboard_token') else 'Not set'}")
    
    # Test 1: Get token
    print(f"\n{'='*80}")
    print("Test 1: Getting Access Token")
    print(f"{'='*80}")
    
    # Clear cached token to force fresh token
    AZAMPayGateway._access_token = None
    AZAMPayGateway._token_expires_at = None
    
    token = AZAMPayGateway.get_access_token()
    
    if not token:
        print("[ERROR] Failed to get access token!")
        return
    
    print(f"[OK] Token obtained: {token[:50]}...")
    print(f"Token length: {len(token)}")
    
    # Test 2: Test checkout endpoint with token
    print(f"\n{'='*80}")
    print("Test 2: Testing Checkout Endpoint Authentication")
    print(f"{'='*80}")
    
    endpoint = f"{base_url}/azampay/mno/checkout"
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Add X-API-Key
    if config.get('api_key'):
        headers["X-API-Key"] = config['api_key']
        print(f"[OK] Using API Key: {config['api_key'][:30]}...")
    elif config['sandbox'] and config['client_id']:
        headers["X-API-Key"] = config['client_id']
        print(f"[OK] Using Client ID as X-API-Key: {config['client_id'][:30]}...")
    else:
        print("[WARN] No X-API-Key available!")
    
    # Test payload
    payload = {
        "accountNumber": "255758285812",
        "amount": 1000,
        "currency": "TZS",
        "externalId": "TEST-AUTH-12345",
        "provider": "AIRTEL"
    }
    
    print(f"\nEndpoint: {endpoint}")
    print(f"Headers:")
    for key, value in headers.items():
        if 'authorization' in key.lower() or 'api-key' in key.lower():
            print(f"  {key}: {value[:50]}...")
        else:
            print(f"  {key}: {value}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code} {response.reason}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            
            if response.status_code == 401:
                print(f"\n[ERROR] Authentication failed!")
                print(f"Message: {response_json.get('message', 'Unknown error')}")
                print(f"\nPossible causes:")
                print("  1. Token is invalid or expired")
                print("  2. X-API-Key is incorrect")
                print("  3. Token format is wrong")
                print("  4. Need to get fresh OAuth token instead of dashboard token")
            elif response.status_code == 200:
                print(f"\n[SUCCESS] Authentication works!")
            else:
                print(f"\n[INFO] Got status {response.status_code} - check response for details")
        except:
            response_text = response.text[:500] if response.text else "(empty response)"
            print(response_text)
            
    except Exception as e:
        print(f"\n[ERROR] Request failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
