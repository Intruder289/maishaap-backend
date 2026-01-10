"""
Quick script to verify local AzamPay setup for testing
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

def check_local_setup():
    """Check if local setup is ready for AzamPay testing"""
    print("=" * 70)
    print("LOCAL AZAMPAY TESTING SETUP CHECK")
    print("=" * 70)
    print()
    
    config = AZAMPayGateway.AZAM_PAY_CONFIG
    
    # Check sandbox mode
    print("[1] SANDBOX MODE:")
    print("-" * 70)
    if config['sandbox']:
        print("[OK] Running in SANDBOX mode (correct for local testing)")
    else:
        print("[WARN] NOT in sandbox mode - should be True for local testing")
    print()
    
    # Check credentials
    print("[2] CREDENTIALS:")
    print("-" * 70)
    client_id = config.get('client_id', '')
    client_secret = config.get('client_secret', '')
    api_key = config.get('api_key', '')
    
    print(f"[{'OK' if client_id else 'ERROR'}] Client ID: {'Set' if client_id else 'NOT SET'}")
    print(f"[{'OK' if client_secret else 'ERROR'}] Client Secret: {'Set' if client_secret else 'NOT SET'}")
    print(f"[{'OK' if api_key else 'WARN'}] API Key: {'Set' if api_key else 'NOT SET'}")
    print()
    
    # Check webhook URL
    print("[3] WEBHOOK URL:")
    print("-" * 70)
    webhook_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', None)
    base_url = getattr(settings, 'BASE_URL', None)
    
    print(f"Webhook URL: {webhook_url or 'Not configured'}")
    print(f"Base URL: {base_url or 'Not configured'}")
    print()
    
    if webhook_url:
        if 'ngrok' in webhook_url or 'localhost' in webhook_url:
            print("[WARN] Webhook URL points to localhost/ngrok")
            print("       Make sure ngrok is running and URL matches")
        elif 'portal.maishaapp.co.tz' in webhook_url:
            print("[INFO] Webhook URL points to production")
            print("       For local testing, update to ngrok URL")
        else:
            print("[OK] Webhook URL configured")
    else:
        print("[WARN] Webhook URL not configured")
        print("       Set AZAM_PAY_WEBHOOK_URL in .env to your ngrok URL")
    print()
    
    # Check webhook handler
    print("[4] WEBHOOK HANDLER:")
    print("-" * 70)
    try:
        from payments.api_views import azam_pay_webhook
        import inspect
        source = inspect.getsource(azam_pay_webhook)
        
        if 'verify_webhook_signature' in source:
            print("[ERROR] Signature validation still present in webhook handler")
            print("        Should be removed per AzamPay instructions")
        else:
            print("[OK] Signature validation removed (correct)")
        
        if 'AzamPay webhook received' in source:
            print("[OK] Enhanced logging present")
        else:
            print("[WARN] Enhanced logging may be missing")
    except Exception as e:
        print(f"[ERROR] Could not check webhook handler: {str(e)}")
    print()
    
    # Testing instructions
    print("[5] TESTING INSTRUCTIONS:")
    print("-" * 70)
    print("1. Start Django server:")
    print("   python manage.py runserver 8081")
    print()
    print("2. Start ngrok (in separate terminal):")
    print("   ngrok http 8081")
    print()
    print("3. Copy ngrok HTTPS URL (e.g., https://abc123.ngrok-free.app)")
    print()
    print("4. Update .env file:")
    print("   AZAM_PAY_WEBHOOK_URL=https://YOUR-NGROK-URL.ngrok-free.app/api/v1/payments/webhook/azam-pay/")
    print()
    print("5. Configure webhook in AzamPay sandbox dashboard:")
    print("   Use the same ngrok URL")
    print()
    print("6. Restart Django server")
    print()
    print("7. Make a test payment and verify webhook is received")
    print()
    
    # Summary
    print("[SUMMARY]")
    print("-" * 70)
    issues = []
    
    if not config['sandbox']:
        issues.append("- Set AZAM_PAY_SANDBOX=True for local testing")
    if not client_id or not client_secret:
        issues.append("- Configure AzamPay credentials in .env")
    if not webhook_url or 'portal.maishaapp.co.tz' in webhook_url:
        issues.append("- Update AZAM_PAY_WEBHOOK_URL to ngrok URL")
    
    if issues:
        print("Issues to fix:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("[OK] Setup looks good for local testing!")
        print("     Follow testing instructions above to test payments")
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    try:
        check_local_setup()
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
