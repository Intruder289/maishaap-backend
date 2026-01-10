"""
AZAMPAY 404 Error Diagnostic Script

This script will test the exact endpoint being called and show detailed information
about why it's returning 404.
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings
from payments.gateway_service import AZAMPayGateway

def test_endpoint(base_url, endpoint_path, headers, payload):
    """Test a specific endpoint"""
    full_url = f"{base_url}{endpoint_path}"
    print(f"\n{'='*80}")
    print(f"Testing: {full_url}")
    print(f"{'='*80}")
    print(f"Method: POST")
    print(f"Headers:")
    for key, value in headers.items():
        if 'authorization' in key.lower() or 'api-key' in key.lower():
            print(f"  {key}: {value[:50]}..." if len(str(value)) > 50 else f"  {key}: {value}")
        else:
            print(f"  {key}: {value}")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(full_url, json=payload, headers=headers, timeout=30)
        
        print(f"\nResponse Status: {response.status_code} {response.reason}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except:
            response_text = response.text[:500] if response.text else "(empty response)"
            print(response_text)
        
        return response.status_code, response
    except requests.exceptions.RequestException as e:
        print(f"\nRequest Exception: {str(e)}")
        return None, None

def main():
    print("\n" + "="*80)
    print("AZAMPAY 404 Error Diagnostic")
    print("="*80)
    
    # Get configuration
    config = AZAMPayGateway.AZAM_PAY_CONFIG
    base_url = AZAMPayGateway.get_base_url()
    
    print(f"\nConfiguration:")
    print(f"  Base URL: {base_url}")
    print(f"  Sandbox: {config.get('sandbox')}")
    print(f"  Client ID: {config.get('client_id', 'Not set')[:20]}...")
    print(f"  API Key: {config.get('api_key', 'Not set')[:20]}...")
    print(f"  App Name: {config.get('app_name')}")
    
    # Get access token
    print(f"\n{'='*80}")
    print("Step 1: Getting Access Token")
    print(f"{'='*80}")
    access_token = AZAMPayGateway.get_access_token()
    
    if not access_token:
        print("\n[ERROR] Failed to get access token!")
        return
    
    print(f"[OK] Access token obtained: {access_token[:50]}...")
    
    # Prepare test payload
    test_payload = {
        "amount": "1000",
        "currency": "TZS",
        "externalId": "TEST-404-DIAG-12345",
        "provider": "AIRTEL",
        "phoneNumber": "255758285812",
        "callbackUrl": "https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/",
        "redirectUrl": "https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/"
    }
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    if config.get('api_key'):
        headers["x-api-key"] = config['api_key']
    elif config['sandbox'] and config['client_id']:
        headers["x-api-key"] = config['client_id']
    
    # Test the current endpoint
    print(f"\n{'='*80}")
    print("Step 2: Testing Current Endpoint")
    print(f"{'='*80}")
    
    current_endpoint = "/api/v1/azampay/mno/checkout"
    status, response = test_endpoint(base_url, current_endpoint, headers, test_payload)
    
    if status == 404:
        print(f"\n[ERROR] Current endpoint returns 404!")
        print(f"\n{'='*80}")
        print("Step 3: Testing Alternative Endpoints")
        print(f"{'='*80}")
        
        # Test alternative endpoints
        alternative_endpoints = [
            "/api/v1/azampay/checkout",
            "/api/v1/mno/checkout",
            "/api/v1/checkout",
            "/api/checkout",
            "/checkout",
            "/api/v1/azampay/mobile/checkout",
            "/api/v1/mobile/checkout",
            "/api/v1/azampay/payment/checkout",
            "/api/v1/payment/checkout",
            "/api/v1/azampay/mno/payment",
            "/api/v1/azampay/mno/create",
            "/api/v1/azampay/create-checkout",
        ]
        
        for endpoint in alternative_endpoints:
            status, resp = test_endpoint(base_url, endpoint, headers, test_payload)
            if status and status != 404:
                print(f"\n[SUCCESS] Found working endpoint: {endpoint}")
                print(f"Status: {status}")
                break
            elif status == 404:
                print(f"[FAILED] {endpoint} - 404")
            else:
                print(f"[ERROR] {endpoint} - Request failed")
    
    # Check if base URL might be wrong
    print(f"\n{'='*80}")
    print("Step 4: Verifying Base URL")
    print(f"{'='*80}")
    
    # Try to access base URL root
    try:
        root_response = requests.get(base_url, timeout=10)
        print(f"Base URL root ({base_url}) returns: {root_response.status_code}")
        if root_response.status_code == 200:
            print("Base URL is accessible")
        else:
            print(f"Base URL might be wrong. Status: {root_response.status_code}")
    except Exception as e:
        print(f"Base URL not accessible: {str(e)}")
    
    # Check API documentation endpoint
    print(f"\n{'='*80}")
    print("Step 5: Checking API Documentation")
    print(f"{'='*80}")
    
    doc_urls = [
        f"{base_url}/api/docs",
        f"{base_url}/docs",
        f"{base_url}/api/v1/docs",
        f"{base_url}/swagger",
        f"{base_url}/redoc",
    ]
    
    for doc_url in doc_urls:
        try:
            doc_response = requests.get(doc_url, timeout=10)
            if doc_response.status_code == 200:
                print(f"[OK] Documentation found at: {doc_url}")
                break
        except:
            pass
    
    print(f"\n{'='*80}")
    print("Diagnostic Complete")
    print(f"{'='*80}")
    print("\nRecommendations:")
    print("1. Check AZAMpay dashboard for the exact endpoint path")
    print("2. Verify the base URL is correct")
    print("3. Check if your API key has the correct permissions")
    print("4. Contact AZAMpay support with the endpoint path you're using")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
