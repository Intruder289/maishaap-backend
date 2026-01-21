#!/usr/bin/env python
"""
Debug script to see exactly what's being sent to AzamPay checkout endpoint
Run this to see the full request details
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings
from payments.gateway_service import AZAMPayGateway

print("=" * 80)
print("AZAMPAY CHECKOUT REQUEST DEBUG")
print("=" * 80)
print()

# Check configuration
print("1. CONFIGURATION CHECK:")
print("-" * 80)
client_id = getattr(settings, 'AZAM_PAY_CLIENT_ID', '')
client_secret = getattr(settings, 'AZAM_PAY_CLIENT_SECRET', '')
api_key = getattr(settings, 'AZAM_PAY_API_KEY', '')
sandbox = getattr(settings, 'AZAM_PAY_SANDBOX', True)

print(f"   AZAM_PAY_SANDBOX: {sandbox}")
print(f"   AZAM_PAY_CLIENT_ID: {client_id[:30]}..." if client_id else "   AZAM_PAY_CLIENT_ID: NOT SET")
print(f"   AZAM_PAY_CLIENT_SECRET: {'SET' if client_secret else 'NOT SET'}")
print(f"   AZAM_PAY_API_KEY: {api_key[:30]}..." if api_key else "   AZAM_PAY_API_KEY: NOT SET")
print()

# Check what will be used as X-API-Key
print("2. X-API-KEY HEADER LOGIC:")
print("-" * 80)
api_key_value = api_key.strip() if api_key else ''
client_id_value = client_id.strip() if client_id else ''

if api_key_value:
    print(f"   [OK] Will use AZAM_PAY_API_KEY: {api_key_value[:30]}...")
elif client_id_value:
    print(f"   [OK] Will use CLIENT_ID as X-API-Key: {client_id_value[:30]}...")
else:
    print("   [ERROR] No X-API-Key available!")
print()

# Check provider mapping
print("3. PROVIDER FORMAT MAPPING:")
print("-" * 80)
provider_mapping = {
    'AIRTEL': 'Airtel',
    'TIGO': 'Tigo',
    'MPESA': 'Mpesa',
    'HALOPESA': 'Halopesa',
    'AZAMPESA': 'Azampesa',
}
print("   Mapping:")
for key, value in provider_mapping.items():
    print(f"     {key} -> {value}")
print()

# Check base URL
print("4. ENDPOINT URLS:")
print("-" * 80)
if sandbox:
    checkout_base = "https://sandbox.azampay.co.tz"
else:
    checkout_base = getattr(settings, 'AZAM_PAY_CHECKOUT_BASE_URL', 'https://checkout.azampay.co.tz')

checkout_url = f"{checkout_base}/azampay/mno/checkout"
print(f"   Checkout URL: {checkout_url}")
print()

print("=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print()

if not client_id_value:
    print("[CRITICAL] AZAM_PAY_CLIENT_ID is not set!")
    print("   -> Set AZAM_PAY_CLIENT_ID in .env file")
    print()

if sandbox:
    print("[WARN] You're in SANDBOX mode")
    print("   -> For production, set AZAM_PAY_SANDBOX=False")
    print()

print("To see actual request being sent:")
print("1. Make a payment attempt")
print("2. Check server logs for these messages:")
print("   - 'Using CLIENT_ID as X-API-Key' (if API_KEY not set)")
print("   - '[AZAMPAY] Headers: Authorization=Bearer ***, X-API-Key=***'")
print("   - '[AZAMPAY] Payload: {...}'")
print()
print("If you see 'X-API-Key=none' in logs, the header is NOT being sent!")
print("If you see 'X-API-Key=***' in logs, the header IS being sent.")
print()
