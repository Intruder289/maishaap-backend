#!/usr/bin/env python
"""
Check if sandbox mode is enabled and explain the test phone fallback
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
print("SANDBOX MODE AND TEST PHONE FALLBACK CHECK")
print("=" * 80)
print()

# Check sandbox status
sandbox_enabled = getattr(settings, 'AZAM_PAY_SANDBOX', True)
test_phone = getattr(settings, 'AZAM_PAY_TEST_PHONE', None)

print("1. CURRENT CONFIGURATION")
print("-" * 80)
print(f"AZAM_PAY_SANDBOX: {sandbox_enabled}")
print(f"AZAM_PAY_TEST_PHONE: {test_phone}")
print()

# Check gateway config
gateway_config = AZAMPayGateway.AZAM_PAY_CONFIG
print("2. GATEWAY CONFIGURATION")
print("-" * 80)
print(f"Sandbox Mode: {gateway_config.get('sandbox', 'Not set')}")
print(f"Test Phone: {gateway_config.get('test_phone', 'Not set')}")
print()

# Explain the fallback
print("3. TEST PHONE FALLBACK EXPLANATION")
print("-" * 80)
print()
print("The code has this fallback logic (line 436-439 in gateway_service.py):")
print()
print("  if not phone_number and cls.AZAM_PAY_CONFIG.get('sandbox') and cls.AZAM_PAY_CONFIG.get('test_phone'):")
print("      phone_number = cls.AZAM_PAY_CONFIG['test_phone']")
print("      logger.info(f\"Using test phone number from config: {phone_number}\")")
print()
print("This fallback ONLY triggers if ALL three conditions are true:")
print("  1. No phone number found (neither customer nor tenant has phone)")
print("  2. Sandbox mode is ENABLED (sandbox=True)")
print("  3. Test phone is configured (AZAM_PAY_TEST_PHONE is set)")
print()

if not sandbox_enabled:
    print("4. YOUR SITUATION")
    print("-" * 80)
    print()
    print("Since you're in PRODUCTION (sandbox=False):")
    print("  [OK] This fallback will NEVER execute")
    print("  [OK] The code checks 'sandbox' first, so it short-circuits")
    print("  [OK] If no phone is found, it will show an error (as it should)")
    print()
    print("The fallback code is harmless - it's dead code in production.")
    print("It's only useful if you were testing in sandbox mode.")
    print()
    print("RECOMMENDATION:")
    print("  - Option 1: Leave it (harmless, doesn't affect production)")
    print("  - Option 2: Remove it (cleaner code, but not necessary)")
    print()
else:
    print("4. YOUR SITUATION")
    print("-" * 80)
    print()
    print("WARNING: Sandbox mode is ENABLED!")
    print("  - If no phone is found, it will use test phone")
    print("  - This might not be what you want in production")
    print("  - Consider setting AZAM_PAY_SANDBOX=False in your .env")
    print()

print("=" * 80)
print("CONCLUSION")
print("=" * 80)
print()
if not sandbox_enabled:
    print("The test phone fallback is NOT active in your production setup.")
    print("It will only show errors if phone numbers are missing (correct behavior).")
else:
    print("Sandbox mode is enabled - the fallback could trigger if configured.")
print()
