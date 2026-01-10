# ✅ AZAMPAY Sandbox Activated - Integration Ready!

## 🎉 Great News!

Your AZAMPAY sandbox has been **activated** and the integration is **ready to use**!

## ✅ What's Already Configured

1. **✅ Correct Endpoint**: `/api/v1/azampay/mno/checkout` (Mobile Money Checkout)
2. **✅ Authentication**: Token-based auth with dashboard token or OAuth2
3. **✅ Payload Format**: All required fields included
4. **✅ Headers**: Proper Authorization and x-api-key headers
5. **✅ Webhook Handler**: Ready at `/api/v1/payments/webhook/azam-pay/`
6. **✅ Error Handling**: Comprehensive error handling and logging

## 🧪 Quick Test Steps

### Option 1: Verify Configuration (Recommended First)

```bash
python verify_azampay_setup.py
```

This will:
- ✅ Check all configuration variables
- ✅ Test token authentication
- ✅ Verify endpoint configuration
- ✅ Confirm everything is ready

### Option 2: Test Full Payment Flow

```bash
python test_azam_pay.py
```

This will:
- ✅ Login to get JWT token
- ✅ Create a payment record
- ✅ Initiate AZAMpay payment
- ✅ Get payment link
- ✅ Test the complete flow

### Option 3: Test via Web Interface

1. **Go to House Payments**:
   ```
   http://127.0.0.1:8081/properties/house/payments/
   ```

2. **Select a Booking**:
   - Use the dropdown to select a booking
   - Click "Record Payment"

3. **Initiate Payment**:
   - Enter payment amount
   - Select "Online Payment (AZAM Pay)" or "Mobile Money (AZAM Pay)"
   - Click "Record Payment"
   - You should be redirected to AZAMpay payment page

4. **Complete Payment**:
   - Complete the payment on AZAMpay sandbox
   - You'll be redirected back
   - Payment status will be updated automatically

## 📊 What to Expect

### Successful Payment Initiation

When you initiate a payment, you should see in the logs:

```
🔍 [AZAMPAY] Calling checkout endpoint: https://sandbox.azampay.co.tz/api/v1/azampay/mno/checkout
   [AZAMPAY] Method: POST
   [AZAMPAY] Response: 200 OK
✅ Payment checkout created successfully. Checkout URL: https://sandbox.azampay.co.tz/checkout/...
```

### Response Format

```json
{
  "success": true,
  "payment_link": "https://sandbox.azampay.co.tz/checkout/...",
  "transaction_id": "...",
  "reference": "BOOKING-...",
  "error": null
}
```

## 🔍 Monitoring

### Check Logs

Monitor these files for detailed information:

1. **`api.log`** - General API logs
   ```bash
   tail -f api.log | grep AZAMPAY
   ```

2. **`api_errors.log`** - Error logs
   ```bash
   tail -f api_errors.log
   ```

3. **Console Output** - Real-time debugging
   - Look for `[AZAMPAY CHECKOUT]` messages

### What to Look For

✅ **Success Indicators**:
- `✅ Payment checkout created successfully`
- HTTP 200 or 201 response
- `checkoutUrl` in response

❌ **Error Indicators**:
- HTTP 404 - Endpoint not found (shouldn't happen now)
- HTTP 401 - Authentication failed
- HTTP 400 - Bad request (check payload)
- HTTP 500 - Server error

## 🐛 Troubleshooting

### If You Get 404 Error

**This shouldn't happen now**, but if it does:

1. **Verify Sandbox Activation**:
   - Check AZAMpay dashboard
   - Confirm "Mobile Money Checkout (Sandbox)" is enabled

2. **Check Endpoint**:
   - Should be: `/api/v1/azampay/mno/checkout`
   - Base URL: `https://sandbox.azampay.co.tz`

3. **Check Logs**:
   - Look for the exact endpoint being called
   - Verify it matches the above

### If You Get 401 Error

1. **Check Token**:
   ```python
   python manage.py shell
   >>> from payments.gateway_service import AZAMPayGateway
   >>> token = AZAMPayGateway.get_access_token()
   >>> print(token)
   ```

2. **Verify Credentials**:
   - Check `.env` file has correct `AZAM_PAY_CLIENT_ID` and `AZAM_PAY_CLIENT_SECRET`
   - Verify `AZAM_PAY_APP_NAME` matches dashboard exactly

### If You Get 400 Error

1. **Check Payload**:
   - Look in logs for the payload being sent
   - Verify all required fields are present:
     - `amount`
     - `currency`
     - `externalId`
     - `provider`
     - `phoneNumber`
     - `callbackUrl`
     - `redirectUrl`

2. **Check Phone Number**:
   - Must be in format: `2557XXXXXXXX` (12 digits, starting with 2557)
   - Customer must have a phone number

## 📝 Configuration Checklist

Before testing, ensure:

- [ ] `.env` file has all AZAMPAY variables set
- [ ] `AZAM_PAY_CLIENT_ID` is set
- [ ] `AZAM_PAY_CLIENT_SECRET` is set
- [ ] `AZAM_PAY_API_KEY` is set (or will use Client ID)
- [ ] `AZAM_PAY_APP_NAME` matches dashboard exactly
- [ ] `AZAM_PAY_SANDBOX=True`
- [ ] `AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz`
- [ ] `AZAM_PAY_WEBHOOK_URL` is set to your production URL
- [ ] Django server is running
- [ ] Customer has a phone number

## 🚀 Ready to Go!

Your integration is **fully configured** and **ready to use**. The sandbox is activated, so you can start testing payments immediately!

### Quick Start

1. **Verify Setup**:
   ```bash
   python verify_azampay_setup.py
   ```

2. **Test Payment**:
   ```bash
   python test_azam_pay.py
   ```

3. **Or Use Web Interface**:
   - Go to `/properties/house/payments/`
   - Select booking and record payment
   - Choose "Online Payment (AZAM Pay)"

## 📞 Support

If you encounter any issues:

1. **Check Logs**: `api.log` and `api_errors.log`
2. **Run Verification**: `python verify_azampay_setup.py`
3. **Check AZAMpay Dashboard**: Verify sandbox is activated
4. **Contact AZAMpay Support**: If issues persist

---

**Status**: ✅ **READY FOR TESTING**

The integration is complete and the sandbox is activated. Start testing! 🎉
