"""
Diagnostic script to check AzamPay webhook integration status
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings
from payments.gateway_service import AZAMPayGateway, PaymentGatewayService

def check_azampay_config():
    """Check AzamPay configuration"""
    print("=" * 70)
    print("AZAMPAY INTEGRATION DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Check settings
    print("[CONFIG] CONFIGURATION CHECK:")
    print("-" * 70)
    
    config = AZAMPayGateway.AZAM_PAY_CONFIG
    
    print(f"[OK] Sandbox Mode: {config['sandbox']}")
    print(f"[OK] Base URL: {config['base_url']}")
    print(f"[OK] Production URL: {config['production_url']}")
    print(f"[OK] App Name: {config['app_name']}")
    print()
    
    # Check credentials
    print("[CREDENTIALS] CREDENTIALS CHECK:")
    print("-" * 70)
    
    client_id = config.get('client_id', '')
    client_secret = config.get('client_secret', '')
    api_key = config.get('api_key', '')
    webhook_secret = config.get('webhook_secret', '')
    dashboard_token = config.get('dashboard_token', '')
    
    print(f"[{'OK' if client_id else 'ERROR'}] Client ID: {'Set' if client_id else 'NOT SET'}")
    print(f"[{'OK' if client_secret else 'ERROR'}] Client Secret: {'Set' if client_secret else 'NOT SET'}")
    print(f"[{'OK' if api_key else 'WARN'}] API Key: {'Set' if api_key else 'NOT SET (using Client ID as fallback)'}")
    print(f"[{'OK' if webhook_secret else 'ERROR'}] Webhook Secret: {'Set' if webhook_secret else 'NOT SET'}")
    print(f"[{'OK' if dashboard_token else 'WARN'}] Dashboard Token: {'Set' if dashboard_token else 'NOT SET (optional)'}")
    print()
    
    # Webhook configuration
    print("[WEBHOOK] WEBHOOK CONFIGURATION:")
    print("-" * 70)
    
    webhook_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', None)
    base_url = getattr(settings, 'BASE_URL', None)
    
    print(f"Webhook URL: {webhook_url or 'Not configured'}")
    print(f"Base URL: {base_url or 'Not configured'}")
    print()
    
    # Sandbox vs Production
    print("[ENV] ENVIRONMENT:")
    print("-" * 70)
    
    if config['sandbox']:
        print("[OK] Running in SANDBOX mode")
        print("[WARN] Webhook signature verification:")
        if webhook_secret:
            print("   [OK] Webhook secret configured - signature will be verified")
        else:
            print("   [WARN] Webhook secret NOT configured")
            print("   [WARN] In sandbox mode, webhooks will be accepted without signature verification")
            print("   [WARN] This is OK for testing, but NOT secure for production")
    else:
        print("[PROD] Running in PRODUCTION mode")
        print("[WARN] Webhook signature verification:")
        if webhook_secret:
            print("   [OK] Webhook secret configured - signature will be verified")
        else:
            print("   [ERROR] Webhook secret NOT configured")
            print("   [ERROR] Webhooks will be REJECTED in production without webhook secret")
            print("   [ERROR] This is why you're getting 'Invalid webhook signature' error")
    print()
    
    # Test signature verification logic
    print("[TEST] SIGNATURE VERIFICATION TEST:")
    print("-" * 70)
    
    test_payload = b'{"test": "data"}'
    test_secret = webhook_secret or client_secret or "test_secret"
    
    if webhook_secret:
        # Test with actual secret
        import hmac
        import hashlib
        expected_sig = hmac.new(
            test_secret.encode('utf-8'),
            test_payload,
            hashlib.sha256
        ).hexdigest()
        
        result = AZAMPayGateway.verify_webhook_signature(test_payload, expected_sig)
        print(f"[OK] Signature verification function works: {result}")
    else:
        print("[WARN] Cannot test signature verification - no webhook secret configured")
    
    print()
    
    # Recommendations
    print("[RECOMMENDATIONS] RECOMMENDATIONS:")
    print("-" * 70)
    
    issues = []
    
    if not client_id:
        issues.append("[ERROR] AZAM_PAY_CLIENT_ID is not set")
    if not client_secret:
        issues.append("[ERROR] AZAM_PAY_CLIENT_SECRET is not set")
    if not webhook_secret and not config['sandbox']:
        issues.append("[ERROR] AZAM_PAY_WEBHOOK_SECRET is not set (REQUIRED for production)")
    if not webhook_secret and config['sandbox']:
        issues.append("[WARN] AZAM_PAY_WEBHOOK_SECRET is not set (recommended for testing)")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("[OK] All required credentials are configured")
    
    print()
    
    # Production fix
    if not config['sandbox'] and not webhook_secret:
        print("[FIX] TO FIX PRODUCTION WEBHOOK ERROR:")
        print("-" * 70)
        print("1. Get webhook secret from AzamPay dashboard:")
        print("   - Log into AzamPay merchant dashboard")
        print("   - Go to Settings > Webhooks")
        print("   - Copy the webhook secret")
        print()
        print("2. Add to your production .env file:")
        print("   AZAM_PAY_WEBHOOK_SECRET=your_webhook_secret_here")
        print()
        print("3. Restart your production server")
        print()
        print("4. Verify webhook URL is configured in AzamPay dashboard:")
        print("   https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/")
        print()
    
    # Local testing
    if config['sandbox']:
        print("[TEST] LOCAL SANDBOX TESTING:")
        print("-" * 70)
        print("[OK] Sandbox mode is enabled")
        print("[OK] Webhooks will work even without webhook secret (for testing)")
        print()
        print("To test webhooks locally:")
        print("1. Use ngrok to expose your local server:")
        print("   ngrok http 8081")
        print()
        print("2. Update AZAM_PAY_WEBHOOK_URL in .env:")
        print("   AZAM_PAY_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/api/v1/payments/webhook/azam-pay/")
        print()
        print("3. Configure webhook URL in AzamPay sandbox dashboard")
        print()
    
    print("=" * 70)

if __name__ == '__main__':
    try:
        check_azampay_config()
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
