# AzamPay Webhook Integration Analysis

## Issue Summary

**Error from Production:**
```
URL: https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
Error: {"error": "Invalid webhook signature"}
```

## Root Cause

The error occurs because:

1. **Production Environment**: Your production server (`portal.maishaapp.co.tz`) is running in **PRODUCTION mode** (`AZAM_PAY_SANDBOX=False`)

2. **Webhook Secret Required**: In production mode, the webhook signature verification is **strict** - it requires a valid `AZAM_PAY_WEBHOOK_SECRET` to be configured

3. **Signature Verification Logic**: 
   - If `webhook_secret` is missing in production → webhooks are **REJECTED** (returns False)
   - If `webhook_secret` is missing in sandbox → webhooks are **ACCEPTED** (returns True for testing)

## Local System Status ✅

**Your local system is properly configured:**

- ✅ Sandbox mode enabled (`AZAM_PAY_SANDBOX=True`)
- ✅ All credentials configured (Client ID, Secret, API Key, Webhook Secret)
- ✅ Signature verification function works correctly
- ✅ Webhook secret is set and working

**Local sandbox integration is COMPLETE and WORKING.**

## Production Issue 🔴

**The production server needs:**

1. **Webhook Secret Configuration**
   - Get webhook secret from AzamPay production dashboard
   - Add to production `.env` file: `AZAM_PAY_WEBHOOK_SECRET=your_production_webhook_secret`
   - Restart production server

2. **Webhook URL Configuration**
   - Verify webhook URL is configured in AzamPay production dashboard:
     `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`

3. **Signature Header**
   - AzamPay sends signature in one of these headers:
     - `X-Signature`
     - `X-Azam-Pay-Signature`
     - `X-Webhook-Signature`
   - The code checks all of these automatically

## How Webhook Signature Verification Works

```python
# In payments/gateway_service.py
def verify_webhook_signature(payload, signature):
    # 1. Get webhook secret from config
    secret = AZAM_PAY_CONFIG['webhook_secret']
    
    # 2. If no secret in production → REJECT
    if not secret and not sandbox:
        return False
    
    # 3. If no secret in sandbox → ACCEPT (for testing)
    if not secret and sandbox:
        return True
    
    # 4. Generate expected signature using HMAC-SHA256
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # 5. Compare signatures (constant-time comparison)
    return hmac.compare_digest(expected_sig, signature)
```

## Solution Steps

### For Production Server:

1. **Get Webhook Secret from AzamPay Dashboard:**
   ```
   - Log into AzamPay merchant dashboard (production)
   - Navigate to: Settings > Webhooks
   - Copy the webhook secret
   ```

2. **Update Production Environment:**
   ```bash
   # Add to production .env file
   AZAM_PAY_WEBHOOK_SECRET=your_production_webhook_secret_here
   ```

3. **Verify Production Settings:**
   ```python
   # In production settings.py or .env
   AZAM_PAY_SANDBOX=False  # Production mode
   AZAM_PAY_WEBHOOK_SECRET=your_production_webhook_secret
   AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
   ```

4. **Restart Production Server:**
   ```bash
   # Restart your Django application server
   # This will load the new webhook secret
   ```

5. **Test Webhook:**
   - Make a test payment in production
   - Check if webhook is received and processed
   - Check server logs for any errors

### For Local Testing:

Your local system is already configured correctly:

1. ✅ Sandbox mode enabled
2. ✅ Webhook secret configured
3. ✅ Signature verification working

**To test webhooks locally:**

1. **Use ngrok to expose local server:**
   ```bash
   ngrok http 8081
   ```

2. **Update local .env:**
   ```bash
   AZAM_PAY_WEBHOOK_URL=https://your-ngrok-url.ngrok.io/api/v1/payments/webhook/azam-pay/
   ```

3. **Configure in AzamPay Sandbox Dashboard:**
   - Add the ngrok URL as webhook endpoint
   - Test payments will trigger webhooks to your local server

## Code Location

**Webhook Handler:**
- File: `payments/api_views.py`
- Function: `azam_pay_webhook()`
- Line: 193

**Signature Verification:**
- File: `payments/gateway_service.py`
- Class: `AZAMPayGateway`
- Method: `verify_webhook_signature()`
- Line: 826

**Configuration:**
- File: `Maisha_backend/settings.py`
- Variables: `AZAM_PAY_*` settings
- Line: 433-457

## Testing

**Run diagnostic script:**
```bash
python check_azampay_webhook_integration.py
```

This will show:
- Current configuration status
- Credentials check
- Webhook configuration
- Environment (sandbox/production)
- Signature verification test
- Recommendations

## Summary

✅ **Local System**: Sandbox integration is complete and working
🔴 **Production**: Needs webhook secret configured in production environment

The error is **NOT related to your local system** - it's a production configuration issue. Your local sandbox integration is properly set up and ready for testing.

---

**Date:** Review Date
**Status:** Local integration ✅ Complete | Production ⚠️ Needs webhook secret
