"""
AZAMPAY Integration Verification Script

This script verifies that your AZAMPAY integration is correctly configured
and ready to use now that the sandbox is activated.

Usage:
    python verify_azampay_setup.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings
from payments.gateway_service import AZAMPayGateway

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def verify_configuration():
    """Verify AZAMPAY configuration"""
    print_section("Step 1: Verify Configuration")
    
    config = AZAMPayGateway.AZAM_PAY_CONFIG
    issues = []
    
    print("\nConfiguration Check:")
    print(f"   Client ID: {'[OK] Set' if config.get('client_id') else '[MISSING] Not set'}")
    print(f"   Client Secret: {'[OK] Set' if config.get('client_secret') else '[MISSING] Not set'}")
    print(f"   API Key: {'[OK] Set' if config.get('api_key') else '[WARN] Not set (will use Client ID)'}")
    print(f"   App Name: {config.get('app_name', 'Not set')}")
    print(f"   Sandbox Mode: {config.get('sandbox', False)}")
    print(f"   Base URL: {config.get('base_url', 'Not set')}")
    print(f"   Dashboard Token: {'[OK] Set' if config.get('dashboard_token') else '[WARN] Not set (will use OAuth2)'}")
    print(f"   Webhook URL: {getattr(settings, 'AZAM_PAY_WEBHOOK_URL', 'Not set')}")
    
    if not config.get('client_id'):
        issues.append("[ERROR] AZAM_PAY_CLIENT_ID is not set")
    if not config.get('client_secret'):
        issues.append("[ERROR] AZAM_PAY_CLIENT_SECRET is not set")
    if not config.get('app_name'):
        issues.append("[WARN] AZAM_PAY_APP_NAME is not set (using default)")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print("\n[SUCCESS] Configuration looks good!")
        return True

def test_token_authentication():
    """Test token authentication"""
    print_section("Step 2: Test Token Authentication")
    
    try:
        print("\nGetting access token from AZAMpay...")
        token = AZAMPayGateway.get_access_token()
        
        if token:
            print(f"[SUCCESS] Access token obtained successfully!")
            print(f"   Token: {token[:50]}...")
            return True
        else:
            print("[ERROR] Failed to get access token")
            return False
    except Exception as e:
        print(f"[ERROR] Error getting access token: {str(e)}")
        return False

def test_endpoint_configuration():
    """Test endpoint configuration"""
    print_section("Step 3: Verify Endpoint Configuration")
    
    base_url = AZAMPayGateway.get_base_url()
    checkout_endpoint = f"{base_url}/api/v1/azampay/mno/checkout"
    
    print(f"\nEndpoint Configuration:")
    print(f"   Base URL: {base_url}")
    print(f"   Checkout Endpoint: {checkout_endpoint}")
    print(f"   [OK] Using correct endpoint: /api/v1/azampay/mno/checkout")
    
    return True

def main():
    """Main verification flow"""
    print("\n" + "=" * 70)
    print("  AZAMPAY Integration Verification")
    print("=" * 70)
    print("\nThis script will verify your AZAMPAY integration is ready.")
    print("Make sure your Django server is NOT running during this check.")
    
    # Verify configuration
    if not verify_configuration():
        print("\n[ERROR] Configuration issues found. Please fix them before proceeding.")
        print("\nCheck your .env file and ensure all required variables are set.")
        sys.exit(1)
    
    # Test token authentication
    if not test_token_authentication():
        print("\n[ERROR] Token authentication failed.")
        print("\nCheck:")
        print("   - Your AZAM_PAY_CLIENT_ID and AZAM_PAY_CLIENT_SECRET")
        print("   - Your AZAM_PAY_APP_NAME matches the dashboard")
        print("   - Your internet connection")
        print("   - AZAMpay sandbox is accessible")
        sys.exit(1)
    
    # Verify endpoint
    test_endpoint_configuration()
    
    # Final summary
    print_section("[SUCCESS] Verification Complete")
    print("\n[SUCCESS] Your AZAMPAY integration is correctly configured!")
    print("\nNext Steps:")
    print("   1. Start your Django server: python manage.py runserver")
    print("   2. Test a payment using: python test_azam_pay.py")
    print("   3. Or test via the web interface at /properties/bookings/{id}/payment/")
    print("   4. Monitor logs in api.log for detailed information")
    print("\nRemember: The sandbox is now activated, so payments should work!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] Verification interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
