# Local AzamPay Payment Testing Guide

## 🎯 Goal
Test AzamPay payment integration locally (including webhook callbacks) before deploying to production.

---

## ✅ Prerequisites

1. **AzamPay Sandbox Account** - Active sandbox credentials
2. **ngrok** - For exposing localhost with HTTPS (required for webhooks)
3. **Local Django Server** - Running on `http://localhost:8081`
4. **AzamPay Sandbox Dashboard Access** - To configure webhook URL

---

## 📋 Step-by-Step Local Testing

### Step 1: Install ngrok

**Download ngrok:**
- Visit: https://ngrok.com/download
- Or install via package manager:
  ```bash
  # Windows (using Chocolatey)
  choco install ngrok
  
  # Or download from website
  ```

**Sign up for free account** (required for custom domains):
- Go to: https://dashboard.ngrok.com/signup
- Get your authtoken

**Authenticate:**
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

---

### Step 2: Start Your Django Server

```bash
# Navigate to project directory
cd d:\KAZI\Maisha_backend

# Start Django development server
python manage.py runserver 8081
```

**Verify it's running:**
- Open: `http://localhost:8081`
- Should see your application

---

### Step 3: Start ngrok Tunnel

**Open a new terminal/command prompt:**

```bash
# Start ngrok tunnel to your local server
ngrok http 8081
```

**You'll see output like:**
```
Forwarding: https://abc123def456.ngrok-free.app -> http://localhost:8081
```

**Copy the HTTPS URL** (e.g., `https://abc123def456.ngrok-free.app`)

**Note:** Free ngrok gives you a random URL each time. For consistent testing, you can:
- Use ngrok paid plan for fixed domain
- Or update webhook URL in AzamPay dashboard each time

---

### Step 4: Update Local Environment Variables

**Edit your `.env` file:**

```bash
# Keep sandbox mode
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz

# Update webhook URL to ngrok URL
AZAM_PAY_WEBHOOK_URL=https://YOUR-NGROK-URL.ngrok-free.app/api/v1/payments/webhook/azam-pay/

# Base URL (optional, for other callbacks)
BASE_URL=https://YOUR-NGROK-URL.ngrok-free.app

# Keep your sandbox credentials
AZAM_PAY_CLIENT_ID=your_sandbox_client_id
AZAM_PAY_CLIENT_SECRET=your_sandbox_client_secret
AZAM_PAY_API_KEY=your_sandbox_api_key
AZAM_PAY_APP_NAME=mishap
```

**Example:**
```bash
AZAM_PAY_WEBHOOK_URL=https://abc123def456.ngrok-free.app/api/v1/payments/webhook/azam-pay/
BASE_URL=https://abc123def456.ngrok-free.app
```

---

### Step 5: Configure Webhook in AzamPay Sandbox Dashboard

1. **Log into AzamPay Sandbox Dashboard:**
   - Go to: https://sandbox.azampay.co.tz (or your sandbox dashboard URL)

2. **Navigate to Webhook Settings:**
   - Go to: Settings > Webhooks
   - Or: App Settings > Webhooks

3. **Add Webhook URL:**
   ```
   https://YOUR-NGROK-URL.ngrok-free.app/api/v1/payments/webhook/azam-pay/
   ```
   - Replace `YOUR-NGROK-URL` with your actual ngrok URL
   - Example: `https://abc123def456.ngrok-free.app/api/v1/payments/webhook/azam-pay/`

4. **Save the webhook URL**

---

### Step 6: Restart Django Server

**After updating .env:**
```bash
# Stop Django server (Ctrl+C)
# Restart it
python manage.py runserver 8081
```

**This loads the new webhook URL from .env**

---

### Step 7: Test Payment Flow

#### 7.1 Create a Test Payment

**Option A: Through Web Interface**
1. Log into your local application: `http://localhost:8081`
2. Navigate to payment/booking page
3. Create a payment with AzamPay
4. Select payment method (Mobile Money, etc.)
5. Enter test phone number (from AzamPay sandbox)
6. Submit payment

**Option B: Through API**
```bash
# Create payment via API
curl -X POST http://localhost:8081/api/v1/payments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "amount": "1000.00",
    "payment_method": "online",
    "tenant": 1
  }'
```

#### 7.2 Initiate Gateway Payment

**After creating payment, initiate gateway:**
```bash
# Initiate payment with AzamPay
curl -X POST http://localhost:8081/api/v1/payments/{payment_id}/initiate-gateway/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Or through web interface:**
- Click "Pay with AzamPay" button
- Should redirect to AzamPay sandbox payment page

#### 7.3 Complete Payment on AzamPay

1. **On AzamPay sandbox page:**
   - Enter test phone number
   - Complete payment (use sandbox test credentials)
   - Payment should process

2. **AzamPay will:**
   - Process payment
   - Send callback to your webhook URL (ngrok)
   - Redirect back to your app

---

### Step 8: Monitor Webhook Reception

**Keep Django server terminal open** to see logs.

**You should see:**
```
[INFO] AzamPay webhook received
[INFO] Headers: {...}
[INFO] Webhook payload: {...}
[INFO] Parsed webhook data: {...}
[INFO] Found payment by transaction ID: {id}
```

**Also check ngrok terminal** for incoming requests:
```
POST /api/v1/payments/webhook/azam-pay/    200 OK
```

---

### Step 9: Verify Payment Status Updated

#### Check Database:
```bash
# Using Django shell
python manage.py shell
```

```python
from payments.models import Payment, PaymentTransaction

# Check payment status
payment = Payment.objects.get(id=YOUR_PAYMENT_ID)
print(f"Payment Status: {payment.status}")
print(f"Payment Amount: {payment.amount}")

# Check transaction
transaction = PaymentTransaction.objects.filter(payment=payment).first()
if transaction:
    print(f"Transaction Status: {transaction.status}")
    print(f"Transaction ID: {transaction.gateway_transaction_id}")
```

#### Check via Web Interface:
1. Go to payment details page
2. Verify status shows "Completed" or "Successful"
3. Check payment date is set

---

## 🔍 Testing Checklist

### Payment Initiation
- [ ] Payment created successfully
- [ ] Gateway initiation returns redirect URL
- [ ] Redirects to AzamPay sandbox page
- [ ] AzamPay page loads correctly

### Payment Processing
- [ ] Can enter phone number on AzamPay page
- [ ] Payment processes on AzamPay
- [ ] Payment completes successfully

### Webhook Reception
- [ ] Webhook received (check Django logs)
- [ ] No "Invalid webhook signature" error
- [ ] Payload parsed correctly
- [ ] Payment found in database

### Status Updates
- [ ] Payment status updated to "completed"
- [ ] PaymentTransaction status updated
- [ ] Payment date set
- [ ] Related records updated (RentInvoice/Booking if applicable)

---

## 🐛 Troubleshooting

### Issue: ngrok URL changes each time

**Solution:**
- Use ngrok paid plan for fixed domain
- Or update webhook URL in AzamPay dashboard each time you restart ngrok
- Or use ngrok config file to set custom domain (paid feature)

### Issue: Webhook not received

**Check:**
1. **ngrok is running:**
   ```bash
   # Check ngrok status
   curl http://localhost:4040/api/tunnels
   ```

2. **Webhook URL in .env matches ngrok URL:**
   ```bash
   # Verify in .env
   AZAM_PAY_WEBHOOK_URL=https://YOUR-NGROK-URL.ngrok-free.app/api/v1/payments/webhook/azam-pay/
   ```

3. **Webhook URL configured in AzamPay dashboard:**
   - Must match exactly (including trailing slash)

4. **Django server restarted** after .env update

5. **Check ngrok web interface:**
   - Open: http://localhost:4040
   - See incoming requests
   - Check if webhook request appears

### Issue: "Invalid webhook signature" error

**This should NOT happen** (signature validation removed)

**If you see it:**
1. Check `payments/api_views.py` - signature validation should be removed
2. Restart Django server
3. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`

### Issue: Payment not found in webhook

**Check:**
1. **Transaction ID in webhook payload:**
   - Check Django logs for webhook payload
   - Verify transaction_id is present

2. **Payment exists in database:**
   ```python
   # In Django shell
   from payments.models import PaymentTransaction
   PaymentTransaction.objects.filter(gateway_transaction_id='TRANSACTION_ID').exists()
   ```

3. **Payment lookup logic:**
   - Webhook tries to find by `transaction_id` first
   - Then by `payment_id` if provided
   - Check logs for lookup results

---

## 📊 Expected Results

### Successful Payment Flow:

1. **Payment Created:**
   - Status: `pending`
   - Amount: Set
   - Payment method: `online`

2. **Gateway Initiated:**
   - Redirects to AzamPay
   - Transaction created in database

3. **Payment Completed on AzamPay:**
   - User completes payment
   - AzamPay processes payment

4. **Webhook Received:**
   - Logs show: "AzamPay webhook received"
   - Payload parsed successfully
   - Payment found

5. **Status Updated:**
   - Payment status: `completed`
   - Transaction status: `successful`
   - Payment date: Set to today
   - Related records updated

---

## 🧪 Test Scenarios

### Test 1: Successful Payment
- Create payment
- Complete on AzamPay
- Verify webhook received
- Verify status updated

### Test 2: Failed Payment
- Create payment
- Cancel on AzamPay
- Verify webhook received (if sent)
- Verify status updated to `failed`

### Test 3: Multiple Payments
- Create multiple payments
- Process them
- Verify all webhooks received
- Verify all statuses updated

### Test 4: Payment with Rent Invoice
- Create rent payment
- Complete payment
- Verify webhook received
- Verify RentInvoice updated

### Test 5: Payment with Booking
- Create booking payment
- Complete payment
- Verify webhook received
- Verify Booking updated

---

## 📝 Testing Log Template

**Keep a log of your tests:**

```
Date: [DATE]
Test #: 1
Payment ID: [ID]
Transaction ID: [ID]
Amount: [AMOUNT]
Status: [SUCCESS/FAIL]
Webhook Received: [YES/NO]
Status Updated: [YES/NO]
Notes: [ANY ISSUES]
```

---

## ✅ Success Criteria

**Before deploying to production, verify:**

- [ ] Payment can be created
- [ ] Gateway initiation works
- [ ] Redirects to AzamPay correctly
- [ ] Payment can be completed on AzamPay
- [ ] Webhook is received (check logs)
- [ ] No "Invalid webhook signature" error
- [ ] Payment status updates correctly
- [ ] Related records (RentInvoice/Booking) update correctly
- [ ] All test scenarios pass

---

## 🚀 After Successful Local Testing

Once local testing is successful:

1. **Document any issues** found and fixed
2. **Note any differences** between local and production
3. **Prepare for production deployment** using `DEPLOYMENT_CHECKLIST.md`
4. **Update production .env** with production credentials
5. **Deploy to production**

---

## 📞 Quick Reference

**Local URLs:**
- Django: `http://localhost:8081`
- ngrok: `https://YOUR-NGROK-URL.ngrok-free.app`
- ngrok Dashboard: `http://localhost:4040`

**Webhook Endpoint:**
- Local: `https://YOUR-NGROK-URL.ngrok-free.app/api/v1/payments/webhook/azam-pay/`

**AzamPay:**
- Sandbox: `https://sandbox.azampay.co.tz`
- Dashboard: (your sandbox dashboard URL)

---

**Status:** Ready for local testing  
**Next Step:** Follow steps 1-9 to test payment flow locally
