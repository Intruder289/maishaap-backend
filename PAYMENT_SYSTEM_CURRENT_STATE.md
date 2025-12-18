# Payment System Current State

## Overview

This document explains how payments are currently handled across all property types and the status of AZAM Pay integration.

---

## Current Payment Handling

### 1. **"Record Payment" Popup (Manual Entry)**

**Location:** All property payment pages:
- `/properties/house/payments/`
- `/properties/hotel/payments/`
- `/properties/lodge/payments/`
- `/properties/venue/payments/`

**What it does:**
- **Manual payment recording** - Staff/admin manually enters payment details
- Creates a payment record in the database
- Updates booking payment status
- **Does NOT use AZAM Pay** - It's just database entry

**Current Flow:**
```
1. Staff clicks "Record Payment" button
2. Modal opens with form fields:
   - Booking Reference (dropdown)
   - Amount
   - Payment Method (Cash, Bank Transfer, Mobile Money, etc.)
   - Payment Type (Deposit, Partial, Full, Refund)
   - Payment Date
   - Transaction Reference (optional)
   - Status (Active, Refunded, Cancelled)
   - Notes
3. Staff fills form and submits
4. Payment is saved to database
5. Booking's paid_amount is updated
6. Page refreshes to show new payment
```

**Endpoint:** `POST /properties/api/record-payment/`

**Status:** ✅ **Fully Working** - This is for manual/offline payments

---

### 2. **Visit Payment (Property Contact Access)**

**Location:** Property detail pages (e.g., `/properties/19/`)

**What it does:**
- User pays one-time fee to view owner contact & location
- **Uses AZAM Pay** (partially implemented)
- Creates payment record and initiates gateway payment

**Current Flow:**
```
1. User clicks "Pay to View Contact" button
2. Modal opens showing amount
3. User clicks "Proceed to Payment"
4. Backend calls AZAM Pay API (placeholder)
5. Returns payment_link (placeholder URL)
6. User redirected to payment gateway
7. After payment, system verifies and reveals contact
```

**Endpoints:**
- Web: `/properties/api/visit-payment/{id}/initiate/`
- Mobile: `/api/v1/properties/{id}/visit/initiate/`

**Status:** ⚠️ **Partially Working** - Infrastructure ready, waiting for AZAM Pay API docs

---

### 3. **Rent Payments (Mobile App)**

**Location:** Mobile app only

**What it does:**
- Tenants pay monthly rent via mobile app
- **Uses AZAM Pay** (partially implemented)
- Creates payment record and initiates gateway payment

**Current Flow:**
```
1. Tenant creates payment via mobile app
2. Mobile app calls: POST /api/v1/rent/payments/{id}/initiate-gateway/
3. Backend calls AZAM Pay API (placeholder)
4. Returns payment_link to mobile app
5. Mobile app opens payment link
6. User completes payment
7. Webhook updates payment status
```

**Endpoints:**
- `POST /api/v1/rent/payments/` - Create payment
- `POST /api/v1/rent/payments/{id}/initiate-gateway/` - Initiate AZAM Pay
- `POST /api/v1/rent/payments/{id}/verify/` - Verify payment

**Status:** ⚠️ **Partially Working** - Infrastructure ready, waiting for AZAM Pay API docs

---

## AZAM Pay Integration Status

### ✅ **What's Ready (Infrastructure Complete)**

1. **Gateway Service** (`payments/gateway_service.py`)
   - `AZAMPayGateway` class created
   - `initiate_payment()` method structure ready
   - `verify_payment()` method structure ready
   - `verify_webhook_signature()` method structure ready
   - `parse_webhook_payload()` method structure ready

2. **Database Models**
   - `PaymentTransaction` model with AZAM Pay fields
   - `PaymentProvider` model for gateway tracking
   - All necessary fields added

3. **API Endpoints**
   - Payment initiation endpoints
   - Payment verification endpoints
   - Webhook handler endpoint (`/api/v1/payments/webhook/azam-pay/`)

4. **Configuration Structure**
   - Settings structure ready for:
     - `AZAM_PAY_API_KEY`
     - `AZAM_PAY_API_SECRET`
     - `AZAM_PAY_MERCHANT_ID`
     - `AZAM_PAY_BASE_URL`
     - `AZAM_PAY_WEBHOOK_SECRET`

### ⏳ **What's Waiting (Placeholder Code)**

All AZAM Pay API calls are currently **placeholders** that return mock data:

1. **`initiate_payment()`** in `gateway_service.py`
   - Currently returns: `payment_link: "https://azampay.co.tz/pay/PLACEHOLDER-{id}"`
   - **Needs:** Actual API endpoint, request format, response parsing

2. **`verify_payment()`** in `gateway_service.py`
   - Currently returns: `status: 'successful'` (hardcoded)
   - **Needs:** Actual verification API endpoint and response parsing

3. **`verify_webhook_signature()`** in `gateway_service.py`
   - Currently returns: `True` (accepts all webhooks - **INSECURE**)
   - **Needs:** Actual signature verification algorithm

4. **`parse_webhook_payload()`** in `gateway_service.py`
   - Currently has placeholder parsing
   - **Needs:** Actual webhook payload structure

---

## What Needs to Be Done (Once AZAM Pay Docs Received)

### Step 1: Update `payments/gateway_service.py`

Replace placeholder code with actual API calls:

```python
# Current (Placeholder):
return {
    'success': True,
    'payment_link': f"https://azampay.co.tz/pay/PLACEHOLDER-{payment.id}",
    'transaction_id': f"AZAM-{payment.id}-{int(timezone.now().timestamp())}",
    ...
}

# After Update (Example):
response = requests.post(
    f"{AZAM_PAY_BASE_URL}/api/v1/payments/initiate",
    json=payload,
    headers={'Authorization': f"Bearer {API_KEY}"}
)
data = response.json()
return {
    'success': True,
    'payment_link': data['payment_url'],  # From actual response
    'transaction_id': data['transaction_id'],  # From actual response
    ...
}
```

### Step 2: Add Environment Variables

Update `.env` file with actual credentials:
```
AZAM_PAY_API_KEY=your_actual_key
AZAM_PAY_API_SECRET=your_actual_secret
AZAM_PAY_MERCHANT_ID=your_merchant_id
AZAM_PAY_BASE_URL=https://api.azampay.co.tz
AZAM_PAY_WEBHOOK_SECRET=your_webhook_secret
```

### Step 3: Test with Sandbox

1. Test payment initiation
2. Test payment verification
3. Test webhook handling
4. Verify signature verification works

### Step 4: Deploy to Production

Once sandbox testing passes, deploy to production.

---

## Summary Table

| Feature | Status | Uses AZAM Pay? | Notes |
|---------|--------|----------------|-------|
| **Record Payment (Manual)** | ✅ Working | ❌ No | Manual entry for offline payments |
| **Visit Payment (Web)** | ⚠️ Partial | ✅ Yes | Infrastructure ready, waiting for API docs |
| **Visit Payment (Mobile)** | ⚠️ Partial | ✅ Yes | Infrastructure ready, waiting for API docs |
| **Rent Payment (Mobile)** | ⚠️ Partial | ✅ Yes | Infrastructure ready, waiting for API docs |
| **AZAM Pay Gateway** | ⏳ Waiting | ✅ Yes | All code structure ready, needs API docs |

---

## Key Points

1. **"Record Payment" popup is NOT connected to AZAM Pay** - It's for manual/offline payment entry
2. **All AZAM Pay integration code is ready** - Just needs actual API endpoints and formats
3. **Visit payments and rent payments WILL use AZAM Pay** - Once documentation is received
4. **Webhook handler is ready** - But signature verification is placeholder (insecure until updated)
5. **All database models are ready** - No migrations needed

---

## Next Steps

1. ⏳ **Wait for AZAM Pay API documentation**
2. 📝 **Update `gateway_service.py`** with actual API calls
3. 🔐 **Implement proper webhook signature verification**
4. 🧪 **Test with AZAM Pay sandbox**
5. 🚀 **Deploy to production**

---

## Files to Update (Once Docs Received)

1. `payments/gateway_service.py` - Main gateway service
2. `.env` - Add actual credentials
3. `settings.py` - Verify configuration (already structured)

---

**Last Updated:** Based on current codebase state
**Status:** Infrastructure complete, waiting for AZAM Pay API documentation

