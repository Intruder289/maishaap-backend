# AZAM Pay Integration Guide

## Overview

This document describes the AZAM Pay payment gateway integration. The system has been **fully implemented** based on the official AZAM Pay API documentation at https://developerdocs.azampay.co.tz/redoc.

## Current Status

✅ **Fully Implemented:**
- Payment gateway service created (`payments/gateway_service.py`)
- Token-based authentication implemented
- Mobile Money Operator (MNO) checkout implemented
- Bank checkout implemented
- Payment initiation endpoint implemented
- Webhook handler endpoint implemented
- Payment verification endpoint implemented
- Webhook signature verification implemented
- Database models updated
- API endpoints configured
- Settings configured

## Architecture

### Flow Diagram

```
1. Mobile App → POST /api/v1/rent/payments/
   ↓
   Creates: Payment (status='pending')
   
2. Mobile App → POST /api/v1/rent/payments/{id}/initiate-gateway/
   ↓
   Backend:
   - Gets access token from AZAM Pay
   - Creates PaymentTransaction
   - Calls AZAM Pay checkout API (MNO or Bank)
   - Returns payment_link to mobile
   
3. Mobile → Opens AZAM Pay payment link
   ↓
   User completes payment on AZAM Pay
   
4. AZAM Pay → POST /api/v1/payments/webhook/azam-pay/
   ↓
   Backend:
   - Verifies webhook signature (HMAC-SHA256)
   - Parses webhook payload
   - Updates PaymentTransaction (status='successful')
   - Updates Payment (status='completed')
   - Updates RentInvoice (amount_paid, status)
   
5. Mobile → POST /api/v1/rent/payments/{id}/verify/
   ↓
   Backend verifies with AZAM Pay API
   Returns: Updated payment status
```

## API Endpoints

### 1. Create Payment
**Endpoint:** `POST /api/v1/rent/payments/`

**Request:**
```json
{
  "rent_invoice": 1,
  "amount": "50000.00",
  "payment_method": "online"
}
```

**Response:**
```json
{
  "id": 123,
  "rent_invoice": 1,
  "amount": "50000.00",
  "status": "pending",
  ...
}
```

### 2. Initiate Gateway Payment
**Endpoint:** `POST /api/v1/rent/payments/{id}/initiate-gateway/`

**Response:**
```json
{
  "success": true,
  "payment_id": 123,
  "transaction_id": 456,
  "payment_link": "https://azampay.co.tz/pay/...",
  "transaction_reference": "RENT-123-...",
  "message": "Payment initiated successfully. Redirect user to payment_link."
}
```

**Note:** The payment link will redirect the user to AZAM Pay's payment page where they can complete the payment using:
- Mobile Money (M-Pesa, TigoPesa, AzamPesa, etc.)
- Bank transfer

### 3. Verify Payment
**Endpoint:** `POST /api/v1/rent/payments/{id}/verify/`

**Response:**
```json
{
  "success": true,
  "payment_id": 123,
  "status": "completed",
  "transaction_status": "successful",
  "verified": true
}
```

### 4. Webhook (AZAM Pay → Backend)
**Endpoint:** `POST /api/v1/payments/webhook/azam-pay/`

**Note:** This endpoint is called by AZAM Pay, not the mobile app. Configure this URL in your AZAM Pay dashboard.

## Configuration

### Django Settings

The following settings have been added to `settings.py`:

```python
# AZAM Pay Configuration
AZAM_PAY_CLIENT_ID = os.environ.get('AZAM_PAY_CLIENT_ID', '')
AZAM_PAY_CLIENT_SECRET = os.environ.get('AZAM_PAY_CLIENT_SECRET', '')
AZAM_PAY_API_KEY = os.environ.get('AZAM_PAY_API_KEY', '')
AZAM_PAY_APP_NAME = os.environ.get('AZAM_PAY_APP_NAME', 'Maisha Property Management')
AZAM_PAY_SANDBOX = os.environ.get('AZAM_PAY_SANDBOX', 'True').lower() == 'true'
AZAM_PAY_BASE_URL = os.environ.get('AZAM_PAY_BASE_URL', 'https://sandbox.azampay.co.tz')
AZAM_PAY_PRODUCTION_URL = os.environ.get('AZAM_PAY_PRODUCTION_URL', 'https://api.azampay.co.tz')
AZAM_PAY_WEBHOOK_SECRET = os.environ.get('AZAM_PAY_WEBHOOK_SECRET', '')
AZAM_PAY_VENDOR_ID = os.environ.get('AZAM_PAY_VENDOR_ID', '')
AZAM_PAY_MERCHANT_ACCOUNT = os.environ.get('AZAM_PAY_MERCHANT_ACCOUNT', '')
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')
```

### Environment Variables

Add these to your `.env` file:

```bash
# AZAM Pay Credentials (get from https://sandbox.azampay.co.tz/)
AZAM_PAY_CLIENT_ID=your_client_id
AZAM_PAY_CLIENT_SECRET=your_client_secret
AZAM_PAY_API_KEY=your_api_key
AZAM_PAY_APP_NAME=Maisha Property Management
AZAM_PAY_SANDBOX=True  # Set to False for production
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz
AZAM_PAY_WEBHOOK_SECRET=your_webhook_secret
AZAM_PAY_VENDOR_ID=your_vendor_id  # Optional, for MNO checkout
AZAM_PAY_MERCHANT_ACCOUNT=your_merchant_account  # Optional, for bank checkout

# Base URL for webhook callbacks
BASE_URL=https://yourdomain.com  # Your production domain
```

## Getting AZAM Pay Credentials

1. **Register for Sandbox:**
   - Visit https://sandbox.azampay.co.tz/
   - Create a developer account
   - Complete KYC documentation

2. **Register Your Application:**
   - Log in to the sandbox dashboard
   - Register your application
   - You'll receive:
     - Client ID
     - Client Secret
     - API Key

3. **Configure Webhook:**
   - In the AZAM Pay dashboard, set your webhook URL to:
     `https://yourdomain.com/api/v1/payments/webhook/azam-pay/`
   - Copy the webhook secret

4. **Get Production Credentials:**
   - After testing in sandbox, request production credentials
   - Update environment variables with production values
   - Set `AZAM_PAY_SANDBOX=False`

## Implementation Details

### Authentication

The system uses token-based authentication:
- Gets access token from `/api/v1/Token/GetToken`
- Token is cached for 1 hour (configurable)
- Token is automatically refreshed when expired

### Payment Initiation

Supports two payment methods:

1. **Mobile Money Operator (MNO) Checkout:**
   - Endpoint: `/api/v1/azampay/mno/checkout`
   - Supports: M-Pesa, TigoPesa, AzamPesa, etc.
   - Requires: Customer phone number

2. **Bank Checkout:**
   - Endpoint: `/api/v1/bank/checkout`
   - Supports: Bank transfers
   - Requires: Account number, account name

### Payment Verification

- Endpoint: `/api/v1/Transaction/Query`
- Uses reference ID to query transaction status
- Returns: status, amount, reference

### Webhook Handling

- Signature verification using HMAC-SHA256
- Checks signature from `X-Signature` or `X-Azam-Pay-Signature` header
- Parses webhook payload and updates payment status
- Automatically updates rent invoice when payment is completed

## Testing

### 1. Test Payment Creation
```bash
POST /api/v1/rent/payments/
Content-Type: application/json
Authorization: Bearer <token>

{
  "rent_invoice": 1,
  "amount": "50000.00",
  "payment_method": "online"
}
```

### 2. Test Gateway Initiation
```bash
POST /api/v1/rent/payments/{id}/initiate-gateway/
Authorization: Bearer <token>
```

### 3. Test Verification
```bash
POST /api/v1/rent/payments/{id}/verify/
Authorization: Bearer <token>
```

### 4. Test Webhook (from AZAM Pay)
```bash
POST /api/v1/payments/webhook/azam-pay/
X-Signature: <hmac_signature>
Content-Type: application/json

{
  "data": {
    "transactionId": "...",
    "referenceId": "...",
    "status": "successful",
    "amount": "50000.00",
    ...
  }
}
```

## Database Migrations

Run migrations to ensure all fields are present:

```bash
python manage.py migrate payments
```

This will:
- Add `azam_reference` field to `PaymentTransaction`
- Add `gateway_transaction_id` field to `PaymentTransaction`

## Payment Provider

The AZAM Pay provider is automatically created when first payment is initiated. You can also create it manually:

```python
from payments.models import PaymentProvider

PaymentProvider.objects.get_or_create(
    name='AZAM Pay',
    defaults={'description': 'AZAM Pay Payment Gateway'}
)
```

## Error Handling

All gateway functions return structured responses:

```python
{
    'success': bool,
    'error': str,  # Error message if failed
    'details': dict  # Additional error details
}
```

Common errors:
- `Failed to obtain access token` - Check credentials
- `User phone number is required` - Ensure user profile has phone number
- `Invalid webhook signature` - Check webhook secret
- `Transaction not found` - Payment may not have been initiated

## Security Notes

1. **Webhook Signature Verification:** Implemented using HMAC-SHA256. Always verify signatures in production.

2. **API Credentials:** Store in environment variables, never commit to code.

3. **HTTPS:** Ensure webhook endpoint is accessible via HTTPS in production.

4. **CSRF Exemption:** Webhook endpoint has CSRF exemption (required for external webhooks).

5. **Token Caching:** Access tokens are cached in memory. In production, consider using Redis for distributed systems.

## Troubleshooting

### Payment Initiation Fails
- Check that credentials are correct
- Verify phone number format (should include country code, e.g., +255...)
- Check AZAM Pay dashboard for API status
- Review logs for detailed error messages

### Webhook Not Received
- Verify webhook URL is configured in AZAM Pay dashboard
- Ensure webhook endpoint is accessible (not behind firewall)
- Check webhook secret matches
- Review server logs for incoming requests

### Payment Verification Fails
- Ensure transaction was initiated successfully
- Check reference ID is correct
- Verify AZAM Pay API is accessible
- Review transaction status in AZAM Pay dashboard

## Support

For issues:
1. Check AZAM Pay documentation: https://developerdocs.azampay.co.tz/redoc
2. Review server logs for detailed error messages
3. Contact AZAM Pay support: support@azampay.com

## Next Steps

1. ✅ Infrastructure ready
2. ✅ Gateway service implemented
3. ✅ API endpoints configured
4. ⏳ Get AZAM Pay credentials
5. ⏳ Test with sandbox environment
6. ⏳ Configure webhook URL
7. ⏳ Test end-to-end payment flow
8. ⏳ Deploy to production

## References

- AZAM Pay API Documentation: https://developerdocs.azampay.co.tz/redoc
- AZAM Pay Sandbox: https://sandbox.azampay.co.tz/
- Support Email: support@azampay.com
