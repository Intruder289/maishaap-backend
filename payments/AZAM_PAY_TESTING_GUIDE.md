# AZAM Pay Testing Guide

## 🚀 Quick Start Testing

This guide will walk you through testing the AZAM Pay integration step by step.

## Prerequisites

1. ✅ Django server is running
2. ✅ `.env` file is configured with your credentials
3. ✅ You have a user account (tenant or staff)
4. ✅ You have at least one rent invoice to test with

---

## Step 1: Start Your Django Server

```bash
cd e:\KAZI\Maisha_backend
python manage.py runserver
```

The server should start on `http://localhost:8000` or `http://127.0.0.1:8000`

---

## Step 2: Access the API Documentation (Swagger)

1. Open your browser and go to:
   ```
   http://localhost:8000/swagger/
   ```
   or
   ```
   http://localhost:8000/api/docs/
   ```

2. **Login to Swagger:**
   - Click the **"Authorize"** button (lock icon)
   - Enter your credentials or use an existing JWT token
   - Or login via: `POST /api/v1/auth/login/` first to get a token

---

## Step 3: Test the Payment Flow

### Test 1: Get a Rent Invoice

**Endpoint:** `GET /api/v1/rent/invoices/`

1. In Swagger, find **`GET /api/v1/rent/invoices/`**
2. Click **"Try it out"**
3. Click **"Execute"**
4. **Note the invoice ID** from the response (e.g., `id: 1`)

**Expected Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "amount": "50000.00",
      "status": "pending",
      ...
    }
  ]
}
```

---

### Test 2: Create a Payment Record

**Endpoint:** `POST /api/v1/rent/payments/`

1. In Swagger, find **`POST /api/v1/rent/payments/`**
2. Click **"Try it out"**
3. Enter the request body:
   ```json
   {
     "rent_invoice": 1,
     "amount": "50000.00",
     "payment_method": "online"
   }
   ```
   (Replace `rent_invoice: 1` with the actual invoice ID from Test 1)

4. Click **"Execute"**
5. **Note the payment ID** from the response (e.g., `id: 123`)

**Expected Response:**
```json
{
  "id": 123,
  "rent_invoice": 1,
  "amount": "50000.00",
  "status": "pending",
  "payment_method": "online",
  ...
}
```

---

### Test 3: Initiate Gateway Payment (AZAM Pay)

**Endpoint:** `POST /api/v1/rent/payments/{id}/initiate-gateway/`

1. In Swagger, find **`POST /api/v1/rent/payments/{id}/initiate-gateway/`**
2. Click **"Try it out"**
3. Enter the payment ID from Test 2 (e.g., `123`)
4. Click **"Execute"**

**Expected Response (Success):**
```json
{
  "success": true,
  "payment_id": 123,
  "transaction_id": 456,
  "payment_link": "https://sandbox.azampay.co.tz/pay/...",
  "transaction_reference": "RENT-123-...",
  "message": "Payment initiated successfully. Redirect user to payment_link."
}
```

**What Happens:**
- ✅ Backend gets access token from AZAM Pay
- ✅ Creates PaymentTransaction record
- ✅ Calls AZAM Pay checkout API
- ✅ Returns payment link

**If Error Occurs:**
- Check the error message in the response
- Check Django server logs (see Step 6)
- Verify your credentials in `.env` file

---

### Test 4: Open Payment Link

1. **Copy the `payment_link`** from Test 3 response
2. **Open it in your browser**
3. You should see the AZAM Pay sandbox payment page
4. Complete the payment using test credentials (if available in sandbox)

---

### Test 5: Verify Payment Status

**Endpoint:** `POST /api/v1/rent/payments/{id}/verify/`

1. In Swagger, find **`POST /api/v1/rent/payments/{id}/verify/`**
2. Click **"Try it out"**
3. Enter the payment ID (e.g., `123`)
4. Click **"Execute"**

**Expected Response:**
```json
{
  "success": true,
  "payment_id": 123,
  "status": "completed",
  "transaction_status": "successful",
  "verified": true
}
```

---

## Step 4: View Test Results

### Option 1: View via API (Transactions)

**Endpoint:** `GET /api/v1/payments/transactions/`

1. In Swagger, find **`GET /api/v1/payments/transactions/`**
2. Click **"Try it out"**
3. Click **"Execute"**

**You'll see:**
- All payment transactions
- Transaction status (initiated, processing, successful, failed)
- Gateway transaction IDs
- Request/response payloads
- Timestamps

**Example Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 456,
      "payment": 123,
      "provider": "AZAM Pay",
      "status": "successful",
      "gateway_transaction_id": "txn_abc123",
      "azam_reference": "RENT-123-1234567890",
      "created_at": "2024-01-15T10:30:00Z",
      ...
    }
  ]
}
```

---

### Option 2: View via Phoenix Admin Panel (Custom Admin)

1. **Access Phoenix Admin:**
   ```
   http://localhost:8000/
   ```
   (Your custom Phoenix admin interface)

2. **Login** with your admin credentials

3. **Navigate to Payment Transactions:**
   
   **Option A: Via Navigation Menu (Recommended)**
   - Look for **"Payments"** section in the sidebar (with credit card icon 💳)
   - Click on **"Payments"** to expand the menu
   - Click on **"Transactions"** 
   - You should see all payment transactions
   
   **Option B: Via URL (Direct Access)**
   ```
   http://localhost:8000/payments/transactions/
   ```
   
   **Other Payment Menu Items:**
   - **Payments → Dashboard** - Payment overview and statistics
   - **Payments → Payment List** - All payment records
   - **Payments → Transactions** - All payment gateway transactions (AZAM Pay, etc.)
   - **Payments → Payment Methods** - Payment providers and recent transactions
   - **Payments → Invoices** - Invoice management

4. **What You'll See:**
   - All payment transactions in a table
   - Transaction status (initiated, pending, successful, failed)
   - Gateway transaction ID
   - AZAM Pay reference
   - Request/response payloads (if displayed)
   - Timestamps
   - Filter options (by status, provider, search)

5. **Alternative: View via Payment Methods Page**
   - Go to: **Payments → Payment Methods**
   - Scroll down to **"Recent Transactions"** section
   - This shows the last 10 transactions

**Note:** If you don't see "Payment Transactions" in the navigation menu, you can:
- Access it directly via URL: `/payments/transactions/`
- Or view transactions via the Payment Methods page

---

### Option 3: View via API (Payment Details)

**Endpoint:** `GET /api/v1/rent/payments/{id}/`

1. In Swagger, find **`GET /api/v1/rent/payments/{id}/`**
2. Click **"Try it out"**
3. Enter the payment ID
4. Click **"Execute"**

**You'll see:**
- Payment status
- Amount
- Payment method
- Transaction details
- Related invoice

---

## Step 5: Monitor Server Logs

### View Real-Time Logs

**In your terminal where Django is running**, you'll see:

```
[INFO] AZAM Pay access token obtained successfully
[INFO] AZAM Pay payment initiated: transaction_id=txn_abc123
[INFO] Webhook received from AZAM Pay: transaction_id=txn_abc123
[INFO] Payment verified: status=successful
```

### Check for Errors

Look for lines starting with:
- `[ERROR]` - Something went wrong
- `[WARNING]` - Potential issues
- `Failed to` - API call failures

**Common Errors:**
- `Failed to obtain access token` - Check credentials
- `Failed to initiate payment` - Check phone number format
- `Invalid webhook signature` - Check webhook secret

---

## Step 6: Test Webhook (Manual Testing)

If you want to test the webhook endpoint manually:

**Endpoint:** `POST /api/v1/payments/webhook/azam-pay/`

**Note:** This is normally called by AZAM Pay, but you can test it manually:

1. In Swagger, find **`POST /api/v1/payments/webhook/azam-pay/`**
2. Click **"Try it out"**
3. Enter a test payload:
   ```json
   {
     "data": {
       "transactionId": "txn_test123",
       "referenceId": "RENT-123-1234567890",
       "status": "successful",
       "amount": "50000.00"
     }
   }
   ```
4. Click **"Execute"**

**Expected Response:**
```json
{
  "success": true,
  "message": "Webhook processed successfully"
}
```

---

## Testing Checklist

Use this checklist to ensure everything works:

- [ ] Server starts without errors
- [ ] Can login and get JWT token
- [ ] Can get rent invoices
- [ ] Can create payment record
- [ ] Can initiate gateway payment (gets payment link)
- [ ] Payment link opens in browser
- [ ] Can verify payment status
- [ ] Can view transactions via API
- [ ] Can view transactions in admin panel
- [ ] Server logs show successful API calls
- [ ] Payment status updates correctly
- [ ] Invoice status updates when payment completes

---

## Troubleshooting

### Payment Initiation Fails

**Check:**
1. ✅ Credentials in `.env` file are correct
2. ✅ Server was restarted after adding credentials
3. ✅ User has a phone number in their profile
4. ✅ Phone number format is correct (+255...)
5. ✅ AZAM Pay sandbox is accessible

**Solution:**
- Check server logs for detailed error messages
- Verify credentials match dashboard
- Ensure phone number is in international format

---

### Payment Link Not Working

**Check:**
1. ✅ Payment was initiated successfully
2. ✅ Payment link is valid URL
3. ✅ AZAM Pay sandbox is accessible

**Solution:**
- Copy payment link and open in browser
- Check if AZAM Pay sandbox is down
- Verify callback URL is configured in dashboard

---

### Verification Fails

**Check:**
1. ✅ Transaction was initiated
2. ✅ Gateway transaction ID exists
3. ✅ Payment was completed on AZAM Pay side

**Solution:**
- Wait a few seconds and try again
- Check transaction status in admin panel
- Verify with AZAM Pay dashboard

---

### Can't See Transactions

**Check:**
1. ✅ You're logged in with correct user
2. ✅ Transaction was created
3. ✅ You have permission to view transactions

**Solution:**
- Staff users can see all transactions
- Tenants can only see their own transactions
- Check admin panel for all transactions

---

## Next Steps After Testing

1. ✅ Test with different payment amounts
2. ✅ Test with different users
3. ✅ Test webhook with actual AZAM Pay callbacks
4. ✅ Test error scenarios (failed payments, cancelled payments)
5. ✅ Test production credentials when ready

---

## Support

If you encounter issues:

1. **Check Server Logs** - Most errors are logged there
2. **Check Admin Panel** - View transaction details
3. **Check API Responses** - Error messages are usually descriptive
4. **Review Documentation** - See `AZAM_PAY_INTEGRATION_GUIDE.md`
5. **Contact Support** - support@azampay.com

---

## Quick Reference: API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/rent/invoices/` | GET | List rent invoices |
| `/api/v1/rent/payments/` | POST | Create payment |
| `/api/v1/rent/payments/{id}/initiate-gateway/` | POST | Start AZAM Pay payment |
| `/api/v1/rent/payments/{id}/verify/` | POST | Verify payment status |
| `/api/v1/payments/transactions/` | GET | View all transactions |
| `/api/v1/payments/webhook/azam-pay/` | POST | Webhook endpoint (AZAM Pay calls this) |

---

Happy Testing! 🎉
