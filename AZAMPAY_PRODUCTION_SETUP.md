# AZAM Pay Production Configuration Guide

## ✅ Production Configuration Complete

The code has been updated to support AZAM Pay production endpoints. The following changes have been made:

### Code Changes

1. **`Maisha_backend/settings.py`**:
   - Added `AZAM_PAY_CHECKOUT_BASE_URL` setting for production checkout endpoint
   - Added `AZAM_PAY_AUTHENTICATOR_BASE_URL` setting for production authenticator endpoint

2. **`payments/gateway_service.py`**:
   - Updated to use separate checkout base URL in production (`https://checkout.azampay.co.tz`)
   - Updated to use production authenticator base URL (`https://authenticator.azampay.co.tz`)
   - Token generation now uses the correct production authenticator endpoint

## 📋 Required .env File Updates

Update your `.env` file with the following production credentials:

```env
# =============================================================================
# AZAM PAY PRODUCTION CONFIGURATION
# =============================================================================

# Production Credentials (from AZAM Pay Dashboard)
AZAM_PAY_CLIENT_ID=019bb775-c4be-7171-904f-9106b7e5002a
AZAM_PAY_CLIENT_SECRET=RUxrOWpTQmtSMk9LQkRiYjdLc0YralV0M2hYUS9SUHF3Sjh5YXltbmRzcWNKOXo3M2JUS2JuOWIyQjBIVFl1dmxNdjhVUzR2RG8vZzA5M1dOV1FjL29mQTYyaFgwcnNoN3hTWEFFbGVaOElvVzNxaHZlN01kbHJSanJqYjNqZlFuR1ZZQ2kxV3RPSG5kRisxVkg1aDYwcHdzZkRzVkdYelZVMCtqOFRBT0Y3MHNKWG9SZHJScCtCR2d0NzVyZDM4RGkzMFVDQ0NMTjNDR241M05CYXNpaEowa1lOTFhNTTRsaDRQL3BuN2lUeXJvSmE4YzNMS1BpQUtpT3pVbUcrSXE0VlJrK0xoYzVLMEM3Q21PUisycDRrM04ra1IxaWN0Y1BmdS8rS2RiSXJGWlQvd1pRWGhmRHJBTWJ1TUM4MjNGbGNuUVlnMklyQzhYL2s1eEdsWGRpeXJOaUJ4TFFMQVhjWmtwYUxXQTN6VGFpRjBXU3JJQTl2MkY0NlRVY1FhRHZwcjNxcnF4a1BzN3ZiNERJMDJvQ1lpSkF5NVcwNTBlakRRR3Z4QWtDeDBVZmtOdlFORlM4SGU3b3VtWmVpL2V5bnBkazRRaVRBLzZQNmU4c3pFWExQeU9uMFVhKzNkeXFUNnNGaGg5Mno1VkxmRzl0Z2RsREVuZnVpVEwycjNwUnllWnhuZTdvdXBneWp0TnFNSFU0aDQ5dDBwSCtXdlc5cTlzVEFDaVNZL2pwVEtpZ2JoQVRjQXNrMlpJcTFaWVZqd3pnV2N0NS9FVEVMRlV3bE95QU9KWGNsNG1OMlJ1ODZVVHdMUU9xZUMxZjY4T2lYdDN3TnBXZWtpZVdEaEFHQjExWU5JQ043NFNhZDEzQ3VCcVpDNTRCa3NQZkJBR0x2TFJubXhKbEk9

# App Name (must match AZAM Pay dashboard exactly)
AZAM_PAY_APP_NAME=maishaapp

# Production Mode (CRITICAL: Set to False for production)
AZAM_PAY_SANDBOX=False

# Production Base URLs
AZAM_PAY_BASE_URL=https://api.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz
AZAM_PAY_CHECKOUT_BASE_URL=https://checkout.azampay.co.tz
AZAM_PAY_AUTHENTICATOR_BASE_URL=https://authenticator.azampay.co.tz

# API Key (if provided by AZAM Pay for production)
AZAM_PAY_API_KEY=

# Webhook Configuration (update with your production domain)
AZAM_PAY_WEBHOOK_SECRET=
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# Base URL for your application (production domain)
BASE_URL=https://portal.maishaapp.co.tz

# Optional: Vendor ID and Merchant Account (if provided)
AZAM_PAY_VENDOR_ID=
AZAM_PAY_MERCHANT_ACCOUNT=
```

## 🔑 Key Configuration Points

### 1. **Sandbox Mode**
```env
AZAM_PAY_SANDBOX=False
```
**CRITICAL**: Must be set to `False` to use production endpoints.

### 2. **App Name**
```env
AZAM_PAY_APP_NAME=maishaapp
```
Must match exactly as registered in AZAM Pay dashboard (case-sensitive).

### 3. **Production Endpoints**
- **Authenticator**: `https://authenticator.azampay.co.tz/AppRegistration/GenerateToken`
- **Checkout**: `https://checkout.azampay.co.tz/azampay/mno/checkout`

These are automatically configured in the code based on `AZAM_PAY_SANDBOX=False`.

### 4. **Client Secret**
⚠️ **IMPORTANT**: The Client Secret is a long string. Make sure to copy it completely without any line breaks or spaces.

## 🧪 Testing Production Configuration

After updating your `.env` file:

1. **Restart your Django server** to load the new environment variables
2. **Test token generation**: The system will automatically fetch tokens from the production authenticator endpoint
3. **Test payment checkout**: Payments will be processed through the production checkout endpoint

## 📝 Verification Checklist

- [ ] `AZAM_PAY_SANDBOX=False` in `.env`
- [ ] `AZAM_PAY_CLIENT_ID` matches production credentials
- [ ] `AZAM_PAY_CLIENT_SECRET` is complete and correct
- [ ] `AZAM_PAY_APP_NAME=maishaapp` (matches dashboard exactly)
- [ ] `BASE_URL` points to your production domain
- [ ] `AZAM_PAY_WEBHOOK_URL` is configured correctly
- [ ] Django server restarted after `.env` changes

## 🔒 Security Notes

1. **Never commit `.env` file** to version control
2. **Keep Client Secret secure** - it's only shown once in the dashboard
3. **Use environment variables** in production, not hardcoded values
4. **Verify webhook URL** is accessible from AZAM Pay servers

## 📞 Support

If you encounter issues:
1. Check Django logs for authentication errors
2. Verify credentials match AZAM Pay dashboard exactly
3. Ensure production endpoints are accessible
4. Contact AZAM Pay support if token generation fails

---

**Status**: ✅ Production configuration ready
**Last Updated**: 2026-01-12
