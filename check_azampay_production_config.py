#!/usr/bin/env python
"""
AzamPay Production Configuration Diagnostic Script

This script checks all critical AzamPay production configurations:
1. Sandbox mode status
2. Production credentials (CLIENT_ID, CLIENT_SECRET, API_KEY)
3. Vendor account configuration
4. Provider settings
5. Environment URLs

Run this on your production server to diagnose "Invalid Vendor" errors.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings
from decouple import config
import requests

print("=" * 80)
print("AZAMPAY PRODUCTION CONFIGURATION DIAGNOSTIC")
print("=" * 80)
print()

# Track issues and warnings
issues = []
warnings = []
passed = []

# =============================================================================
# 1. CHECK SANDBOX MODE STATUS
# =============================================================================
print("1. CHECKING SANDBOX MODE STATUS")
print("-" * 80)

try:
    sandbox_mode = getattr(settings, 'AZAM_PAY_SANDBOX', True)
    sandbox_from_env = config('AZAM_PAY_SANDBOX', default='True', cast=bool)
    
    print(f"   AZAM_PAY_SANDBOX (Django settings): {sandbox_mode}")
    print(f"   AZAM_PAY_SANDBOX (.env file): {sandbox_from_env}")
    
    if sandbox_mode:
        issues.append("[CRITICAL] AZAM_PAY_SANDBOX is True - You're using SANDBOX mode!")
        print("   [X] CRITICAL: AZAM_PAY_SANDBOX = True")
        print("   -> You're in SANDBOX mode, not PRODUCTION!")
        print("   -> Fix: Set AZAM_PAY_SANDBOX=False in .env file")
    else:
        passed.append("[OK] AZAM_PAY_SANDBOX is False (Production mode)")
        print("   [OK] AZAM_PAY_SANDBOX = False (Production mode)")
except Exception as e:
    issues.append(f"Error checking sandbox mode: {str(e)}")
    print(f"   [ERROR] Error: {str(e)}")

print()

# =============================================================================
# 2. CHECK PRODUCTION CREDENTIALS
# =============================================================================
print("2. CHECKING PRODUCTION CREDENTIALS")
print("-" * 80)

# Check CLIENT_ID
client_id = getattr(settings, 'AZAM_PAY_CLIENT_ID', '')
client_id_from_env = config('AZAM_PAY_CLIENT_ID', default='')

if not client_id:
    issues.append("[CRITICAL] AZAM_PAY_CLIENT_ID is NOT SET")
    print("   [X] AZAM_PAY_CLIENT_ID: NOT SET")
    print("   -> This is REQUIRED for production!")
else:
    # Check if it looks like a production client ID (UUID format)
    is_uuid_format = len(client_id) == 36 and client_id.count('-') == 4
    if is_uuid_format:
        passed.append("[OK] AZAM_PAY_CLIENT_ID is set (UUID format)")
        print(f"   [OK] AZAM_PAY_CLIENT_ID: SET ({client_id[:20]}...)")
        print(f"      Format: UUID format (looks correct)")
    else:
        warnings.append("[WARN] AZAM_PAY_CLIENT_ID format might be incorrect")
        print(f"   [WARN] AZAM_PAY_CLIENT_ID: SET but format unusual ({client_id[:30]}...)")
        print(f"      Expected: UUID format (e.g., 019bb775-c4be-7171-904f-9106b7e5002a)")

# Check CLIENT_SECRET
client_secret = getattr(settings, 'AZAM_PAY_CLIENT_SECRET', '')
client_secret_from_env = config('AZAM_PAY_CLIENT_SECRET', default='')

if not client_secret:
    issues.append("[CRITICAL] AZAM_PAY_CLIENT_SECRET is NOT SET")
    print("   [X] AZAM_PAY_CLIENT_SECRET: NOT SET")
    print("   -> This is REQUIRED for production!")
else:
    # Production client secrets are usually very long base64 strings
    if len(client_secret) > 100:
        passed.append("[OK] AZAM_PAY_CLIENT_SECRET is set (long format)")
        print(f"   [OK] AZAM_PAY_CLIENT_SECRET: SET (length: {len(client_secret)} chars)")
        print(f"      Format: Long base64 string (looks correct)")
    else:
        warnings.append("[WARN] AZAM_PAY_CLIENT_SECRET might be too short")
        print(f"   [WARN] AZAM_PAY_CLIENT_SECRET: SET but seems short (length: {len(client_secret)} chars)")
        print(f"      Expected: Long base64 string (usually 500+ characters)")

# Check API_KEY
api_key = getattr(settings, 'AZAM_PAY_API_KEY', '')
api_key_from_env = config('AZAM_PAY_API_KEY', default='')

if not api_key:
    warnings.append("[WARN] AZAM_PAY_API_KEY is NOT SET")
    print("   [WARN] AZAM_PAY_API_KEY: NOT SET")
    print("   -> This might be required for production checkout endpoints")
    print("   -> Check AzamPay production dashboard for API Key")
else:
    passed.append("[OK] AZAM_PAY_API_KEY is set")
    print(f"   [OK] AZAM_PAY_API_KEY: SET ({api_key[:20]}...)")

print()

# =============================================================================
# 3. CHECK APP NAME
# =============================================================================
print("3. CHECKING APP NAME CONFIGURATION")
print("-" * 80)

app_name = getattr(settings, 'AZAM_PAY_APP_NAME', '')
if not app_name:
    warnings.append("[WARN] AZAM_PAY_APP_NAME not set")
    print("   [WARN] AZAM_PAY_APP_NAME: NOT SET")
    print("   -> This must match your AzamPay dashboard app name exactly")
else:
    passed.append(f"[OK] AZAM_PAY_APP_NAME is set: {app_name}")
    print(f"   [OK] AZAM_PAY_APP_NAME: {app_name}")
    print("   -> Verify this matches your AzamPay dashboard app name EXACTLY (case-sensitive)")

print()

# =============================================================================
# 4. CHECK VENDOR ID AND MERCHANT ACCOUNT
# =============================================================================
print("4. CHECKING VENDOR ACCOUNT CONFIGURATION")
print("-" * 80)

vendor_id = getattr(settings, 'AZAM_PAY_VENDOR_ID', '')
merchant_account = getattr(settings, 'AZAM_PAY_MERCHANT_ACCOUNT', '')

if not vendor_id:
    warnings.append("[WARN] AZAM_PAY_VENDOR_ID not set")
    print("   [WARN] AZAM_PAY_VENDOR_ID: NOT SET")
    print("   -> This might be required for production vendor account")
    print("   -> Check AzamPay production dashboard for Vendor ID")
else:
    passed.append("[OK] AZAM_PAY_VENDOR_ID is set")
    print(f"   [OK] AZAM_PAY_VENDOR_ID: {vendor_id}")

if not merchant_account:
    warnings.append("[WARN] AZAM_PAY_MERCHANT_ACCOUNT not set")
    print("   [WARN] AZAM_PAY_MERCHANT_ACCOUNT: NOT SET")
    print("   -> This might be required for bank checkout")
else:
    passed.append("[OK] AZAM_PAY_MERCHANT_ACCOUNT is set")
    print(f"   [OK] AZAM_PAY_MERCHANT_ACCOUNT: {merchant_account}")

print()

# =============================================================================
# 5. CHECK PRODUCTION URLS
# =============================================================================
print("5. CHECKING PRODUCTION URLS")
print("-" * 80)

base_url = getattr(settings, 'AZAM_PAY_BASE_URL', '')
production_url = getattr(settings, 'AZAM_PAY_PRODUCTION_URL', '')
checkout_base_url = getattr(settings, 'AZAM_PAY_CHECKOUT_BASE_URL', '')
authenticator_base_url = getattr(settings, 'AZAM_PAY_AUTHENTICATOR_BASE_URL', '')

if sandbox_mode:
    # In sandbox, check if URLs are sandbox URLs
    if 'sandbox' in base_url.lower():
        print(f"   [OK] AZAM_PAY_BASE_URL: {base_url} (sandbox URL - correct for sandbox mode)")
    else:
        warnings.append(f"[WARN] AZAM_PAY_BASE_URL is not sandbox URL: {base_url}")
        print(f"   [WARN] AZAM_PAY_BASE_URL: {base_url} (not a sandbox URL)")
else:
    # In production, check if URLs are production URLs
    if 'sandbox' in base_url.lower():
        issues.append(f"[CRITICAL] AZAM_PAY_BASE_URL is sandbox URL in production mode: {base_url}")
        print(f"   [X] AZAM_PAY_BASE_URL: {base_url} (SANDBOX URL in PRODUCTION mode!)")
    elif 'api.azampay.co.tz' in base_url or 'checkout.azampay.co.tz' in base_url:
        passed.append(f"[OK] AZAM_PAY_BASE_URL is production URL: {base_url}")
        print(f"   [OK] AZAM_PAY_BASE_URL: {base_url} (production URL)")

print(f"   Production URL: {production_url}")
print(f"   Checkout Base URL: {checkout_base_url}")
print(f"   Authenticator Base URL: {authenticator_base_url}")

print()

# =============================================================================
# 6. CHECK WEBHOOK CONFIGURATION
# =============================================================================
print("6. CHECKING WEBHOOK CONFIGURATION")
print("-" * 80)

webhook_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', '')
base_url_app = getattr(settings, 'BASE_URL', '')

if webhook_url:
    print(f"   [OK] AZAM_PAY_WEBHOOK_URL: {webhook_url}")
    if 'https://' not in webhook_url:
        warnings.append("[WARN] Webhook URL should use HTTPS")
        print("   [WARN] Webhook URL should use HTTPS (not HTTP)")
else:
    warnings.append("[WARN] AZAM_PAY_WEBHOOK_URL not set")
    print("   [WARN] AZAM_PAY_WEBHOOK_URL: NOT SET")

print(f"   BASE_URL: {base_url_app}")

print()

# =============================================================================
# 7. TEST API CONNECTION (if credentials are set)
# =============================================================================
print("7. TESTING API CONNECTION")
print("-" * 80)

if client_id and client_secret and not sandbox_mode:
    print("   Attempting to authenticate with AzamPay production API...")
    
    # Try to get access token
    try:
        from payments.gateway_service import AZAMPayGateway
        
        # Check what base URL will be used
        base_url_used = AZAMPayGateway.get_base_url()
        print(f"   Using base URL: {base_url_used}")
        
        # Try to get access token
        try:
            token = AZAMPayGateway.get_access_token()
            if token:
                passed.append("[OK] Successfully obtained access token from AzamPay")
                print(f"   [OK] Successfully obtained access token!")
                print(f"      Token: {token[:50]}...")
            else:
                issues.append("[CRITICAL] Failed to obtain access token (returned None)")
                print("   [X] Failed to obtain access token (returned None)")
        except Exception as e:
            error_msg = str(e)
            if "Invalid Vendor" in error_msg or "Invalid" in error_msg:
                issues.append(f"[CRITICAL] Authentication failed: {error_msg}")
                print(f"   [X] Authentication FAILED: {error_msg}")
                print("   -> This suggests vendor account issue!")
            else:
                warnings.append(f"[WARN] Authentication error: {error_msg}")
                print(f"   [WARN] Authentication error: {error_msg}")
    except Exception as e:
        warnings.append(f"[WARN] Could not test API connection: {str(e)}")
        print(f"   [WARN] Could not test API connection: {str(e)}")
else:
    if sandbox_mode:
        print("   [SKIP] Skipping (sandbox mode)")
    elif not client_id or not client_secret:
        print("   [SKIP] Skipping (credentials not set)")

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 80)
print("SUMMARY")
print("=" * 80)

if issues:
    print("\n[X] CRITICAL ISSUES FOUND:")
    for issue in issues:
        print(f"   {issue}")
    
if warnings:
    print("\n[WARN] WARNINGS:")
    for warning in warnings:
        print(f"   {warning}")

if passed:
    print("\n[OK] PASSED CHECKS:")
    for check in passed:
        print(f"   {check}")

print()

# =============================================================================
# RECOMMENDATIONS
# =============================================================================
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

if sandbox_mode:
    print("\n[CRITICAL] You're in SANDBOX mode!")
    print("   To fix 'Invalid Vendor' error in production:")
    print("   1. Set AZAM_PAY_SANDBOX=False in .env file")
    print("   2. Ensure you have PRODUCTION credentials (not sandbox)")
    print("   3. Restart your Django server")

if not client_id or not client_secret:
    print("\n[CRITICAL] Missing production credentials!")
    print("   To get production credentials:")
    print("   1. Log in to AzamPay PRODUCTION dashboard: https://developers.azampay.co.tz/")
    print("   2. Navigate to your app settings")
    print("   3. Copy CLIENT_ID and CLIENT_SECRET")
    print("   4. Add to .env file:")
    print("      AZAM_PAY_CLIENT_ID=your_production_client_id")
    print("      AZAM_PAY_CLIENT_SECRET=your_production_client_secret")

if not api_key and not sandbox_mode:
    print("\n[WARN] API Key not set (might be required for production)")
    print("   Check AzamPay production dashboard for API Key")
    print("   Some endpoints require X-API-Key header")

print("\nCHECKLIST FOR 'INVALID VENDOR' ERROR:")
print("   [ ] AZAM_PAY_SANDBOX=False (production mode)")
print("   [ ] AZAM_PAY_CLIENT_ID set (production credentials)")
print("   [ ] AZAM_PAY_CLIENT_SECRET set (production credentials)")
print("   [ ] AZAM_PAY_API_KEY set (if required)")
print("   [ ] Vendor account activated in AzamPay production dashboard")
print("   [ ] App approved/verified in AzamPay production dashboard")
print("   [ ] Providers enabled (Airtel, Tigo, Mpesa) in vendor account")
print("   [ ] Webhook URL configured in production dashboard")

print("\n" + "=" * 80)
print("Next Steps:")
print("=" * 80)
print("1. Fix any CRITICAL ISSUES listed above")
print("2. Check AzamPay PRODUCTION dashboard:")
print("   -> https://developers.azampay.co.tz/")
print("3. Verify vendor account status and provider configuration")
print("4. Restart Django server after making changes")
print("5. Test payment again")
print("=" * 80)
