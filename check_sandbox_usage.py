#!/usr/bin/env python
"""
Check if any sandbox URLs or configurations are being used
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
print("CHECKING FOR SANDBOX USAGE")
print("=" * 80)
print()

issues = []
warnings = []
passed = []

# Check settings
sandbox = getattr(settings, 'AZAM_PAY_SANDBOX', True)
base_url = getattr(settings, 'AZAM_PAY_BASE_URL', '')
checkout_base_url = getattr(settings, 'AZAM_PAY_CHECKOUT_BASE_URL', '')
authenticator_base_url = getattr(settings, 'AZAM_PAY_AUTHENTICATOR_BASE_URL', '')

print("1. SETTINGS CHECK:")
print("-" * 80)
print(f"   AZAM_PAY_SANDBOX: {sandbox}")
print(f"   AZAM_PAY_BASE_URL: {base_url}")
print(f"   AZAM_PAY_CHECKOUT_BASE_URL: {checkout_base_url}")
print(f"   AZAM_PAY_AUTHENTICATOR_BASE_URL: {authenticator_base_url}")
print()

# Check what gateway will use
print("2. GATEWAY SERVICE CHECK:")
print("-" * 80)
gateway_config = AZAMPayGateway.AZAM_PAY_CONFIG
print(f"   Gateway sandbox mode: {gateway_config['sandbox']}")
print(f"   Gateway base_url: {gateway_config['base_url']}")
print(f"   Gateway checkout_base_url: {gateway_config.get('checkout_base_url', 'N/A')}")
print(f"   Gateway authenticator_base_url: {gateway_config.get('authenticator_base_url', 'N/A')}")
print()

# Check what URLs will be used
print("3. ACTUAL URLs THAT WILL BE USED:")
print("-" * 80)
actual_base_url = AZAMPayGateway.get_base_url()
print(f"   get_base_url() returns: {actual_base_url}")

# Check checkout URL
if gateway_config['sandbox']:
    checkout_base = gateway_config['base_url']
else:
    checkout_base = gateway_config.get('checkout_base_url', 'https://checkout.azampay.co.tz')
checkout_url = f"{checkout_base}/azampay/mno/checkout"
print(f"   Checkout URL will be: {checkout_url}")

# Check authenticator URL
if gateway_config['sandbox']:
    authenticator_url = "https://authenticator-sandbox.azampay.co.tz"
else:
    authenticator_url = gateway_config.get('authenticator_base_url', 'https://authenticator.azampay.co.tz')
print(f"   Authenticator URL will be: {authenticator_url}")
print()

# Check for sandbox URLs
print("4. SANDBOX URL DETECTION:")
print("-" * 80)

sandbox_urls = [
    'sandbox.azampay.co.tz',
    'authenticator-sandbox.azampay.co.tz',
    'api-disbursement-sandbox.azampay.co.tz'
]

found_sandbox = False

if 'sandbox' in actual_base_url.lower():
    issues.append(f"[CRITICAL] Base URL contains sandbox: {actual_base_url}")
    print(f"   [X] Base URL contains sandbox: {actual_base_url}")
    found_sandbox = True
else:
    passed.append(f"[OK] Base URL is production: {actual_base_url}")
    print(f"   [OK] Base URL is production: {actual_base_url}")

if 'sandbox' in checkout_url.lower():
    issues.append(f"[CRITICAL] Checkout URL contains sandbox: {checkout_url}")
    print(f"   [X] Checkout URL contains sandbox: {checkout_url}")
    found_sandbox = True
else:
    passed.append(f"[OK] Checkout URL is production: {checkout_url}")
    print(f"   [OK] Checkout URL is production: {checkout_url}")

if 'sandbox' in authenticator_url.lower():
    issues.append(f"[CRITICAL] Authenticator URL contains sandbox: {authenticator_url}")
    print(f"   [X] Authenticator URL contains sandbox: {authenticator_url}")
    found_sandbox = True
else:
    passed.append(f"[OK] Authenticator URL is production: {authenticator_url}")
    print(f"   [OK] Authenticator URL is production: {authenticator_url}")

if gateway_config['sandbox']:
    issues.append("[CRITICAL] Gateway is in SANDBOX mode!")
    print(f"   [X] Gateway sandbox mode: True (should be False for production)")
    found_sandbox = True
else:
    passed.append("[OK] Gateway is in PRODUCTION mode")
    print(f"   [OK] Gateway sandbox mode: False (production)")
print()

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

if issues:
    print("\n[X] ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")

if passed:
    print("\n[OK] PASSED:")
    for check in passed:
        print(f"   {check}")

if found_sandbox:
    print("\n[CRITICAL] You are using SANDBOX configuration!")
    print("   -> Check your .env file:")
    print("      AZAM_PAY_SANDBOX=False")
    print("      AZAM_PAY_BASE_URL=https://api.azampay.co.tz")
    print("      AZAM_PAY_CHECKOUT_BASE_URL=https://checkout.azampay.co.tz")
    print("      AZAM_PAY_AUTHENTICATOR_BASE_URL=https://authenticator.azampay.co.tz")
else:
    print("\n[OK] No sandbox URLs detected - you're using PRODUCTION configuration!")

print()
