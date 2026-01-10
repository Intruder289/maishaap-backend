# 🚀 Quick Start: Testing AZAM Pay

## Where to Start

### Option 1: Using Swagger UI (Recommended for Beginners)

1. **Start your server:**
   ```bash
   python manage.py runserver
   ```

2. **Open Swagger:**
   ```
   http://localhost:8000/swagger/
   ```

3. **Follow the guide:**
   - See `AZAM_PAY_TESTING_GUIDE.md` for step-by-step instructions

---

### Option 2: Using Python Script (Quick Test)

1. **Start your server:**
   ```bash
   python manage.py runserver
   ```

2. **Run the test script:**
   ```bash
   python test_azam_pay.py
   ```

3. **Follow the prompts** - it will guide you through the test

---

## How to See Your Test Results

### 1. **View in Swagger/API** (Real-time)

**Transactions:**
```
GET http://localhost:8000/api/v1/payments/transactions/
```

**Payment Details:**
```
GET http://localhost:8000/api/v1/rent/payments/{id}/
```

**What you'll see:**
- ✅ Transaction status (initiated, processing, successful, failed)
- ✅ Payment link
- ✅ Gateway transaction ID
- ✅ AZAM Pay reference
- ✅ Request/response payloads
- ✅ Timestamps

---

### 2. **View in Phoenix Admin** (Custom Admin Interface)

1. **Go to Phoenix admin:**
   ```
   http://localhost:8000/
   ```

2. **Navigate to Payment Transactions:**
   
   **Via Navigation Menu (Easiest):**
   - Look for **"Payments"** in the sidebar (with credit card icon 💳)
   - Click **"Payments"** to expand
   - Click **"Transactions"**
   
   **Or Direct URL:**
   ```
   http://localhost:8000/payments/transactions/
   ```
   
   **Other Payment Options:**
   - **Payments → Dashboard** - Overview
   - **Payments → Payment List** - All payments
   - **Payments → Transactions** - Gateway transactions (AZAM Pay)
   - **Payments → Payment Methods** - Providers

3. **What you'll see:**
   - All payment transactions in a table
   - Transaction status, IDs, amounts
   - Gateway transaction details
   - Filter and search options
   - Full transaction information

4. **Alternative locations:**
   - **Payments → Payment Methods** - Shows recent transactions at bottom
   - **Payments → Payment List** - Shows payments (click to see transactions)

---

### 3. **View in Server Logs** (Real-time Monitoring)

**In your terminal where Django is running**, you'll see:

```
✅ Success messages:
[INFO] AZAM Pay access token obtained successfully
[INFO] AZAM Pay payment initiated: transaction_id=txn_abc123
[INFO] Webhook received from AZAM Pay
[INFO] Payment verified: status=successful

❌ Error messages:
[ERROR] Failed to obtain access token
[ERROR] Failed to initiate payment: User phone number is required
```

---

## Quick Test Flow

```
1. Login → Get JWT token
   ↓
2. Get Rent Invoice → Get invoice ID
   ↓
3. Create Payment → Get payment ID
   ↓
4. Initiate Gateway → Get payment link
   ↓
5. Open Payment Link → Complete payment on AZAM Pay
   ↓
6. Verify Payment → Check status
   ↓
7. View Results → Check transactions
```

---

## What to Look For

### ✅ Success Indicators:

- Payment link is generated
- Transaction status is "initiated" or "successful"
- Payment status changes to "completed"
- Invoice status updates
- No errors in server logs

### ❌ Error Indicators:

- Error messages in API response
- Transaction status is "failed"
- Error logs in server terminal
- Payment link is null or empty

---

## Need Help?

1. **Check the full guide:** `AZAM_PAY_TESTING_GUIDE.md`
2. **Check server logs** - Most errors are logged there
3. **Check admin panel** - View full transaction details
4. **Review integration guide:** `AZAM_PAY_INTEGRATION_GUIDE.md`

---

**Ready to test?** Start with Option 1 (Swagger) for the easiest experience! 🎉
