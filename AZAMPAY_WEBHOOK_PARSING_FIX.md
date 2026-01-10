# AzamPay Webhook Parsing Fix

## Issue Identified

**From your test logs:**
```
Webhook payload: {'transid': '5aae72e0e5974f0e8319394167d7708f', 'transactionstatus': 'success', 'utilityref': 'BOOKING-HSE-000009-1767956005', ...}
Parsed webhook data: {'transaction_id': None, 'reference': '5aae72e0e5974f0e8319394167d7708f', 'status': '', ...}
ERROR: Could not find payment - payment_id: None, transaction_id: None
```

**Problem:**
- Webhook received ✅
- Payload parsing failed to extract `transid` ❌
- Payment lookup failed because `transaction_id` was None ❌

---

## Root Cause

AzamPay webhook uses different field names than expected:
- **`transid`** (not `transactionId` or `transaction_id`)
- **`transactionstatus`** (not `status`)
- **`utilityref`** (the external reference we sent)

The parsing function was looking for the wrong field names.

---

## Fix Applied

### 1. Updated `parse_webhook_payload()` in `payments/gateway_service.py`

**Added support for AzamPay field names:**
- `transid` → `transaction_id`
- `transactionstatus` → `status`
- `utilityref` → stored for payment lookup

### 2. Enhanced Direct Extraction in `payments/api_views.py`

**Always extracts directly from payload** (prioritizes actual AzamPay field names):
- Checks `transid` first (AzamPay format)
- Falls back to other formats
- Merges with parsed data

### 3. Enhanced Payment Lookup

**Multiple lookup strategies:**
1. **By transaction_id** (from `transid` field)
   - Looks up `PaymentTransaction` by `gateway_transaction_id`
   
2. **By utilityref** (from `utilityref` field)
   - For `BOOKING-*` format: Extracts booking reference, finds booking, finds payment
   - For `RENT-*` format: Extracts payment ID directly
   
3. **By azam_reference**
   - Looks up by `azam_reference` field

---

## Webhook Payload Format (AzamPay)

**Actual format received:**
```json
{
  "message": "success",
  "transactionstatus": "success",
  "operator": "Mpesa",
  "reference": "5aae72e0e5974f0e8319394167d7708f",
  "externalreference": "5aae72e0e5974f0e8319394167d7708f",
  "utilityref": "BOOKING-HSE-000009-1767956005",
  "amount": "60000",
  "transid": "5aae72e0e5974f0e8319394167d7708f",
  "msisdn": "255758285812",
  "mnoreference": "a068932f-09a8-4ff4-82c0-6efa13def8d5"
}
```

**Key Fields:**
- `transid`: Transaction ID (used to find PaymentTransaction)
- `transactionstatus`: Payment status ("success", "failed", etc.)
- `utilityref`: External reference we sent (BOOKING-{ref}-{timestamp} or RENT-{id}-{timestamp})
- `reference`: AzamPay reference
- `amount`: Payment amount

---

## How Payment Lookup Works Now

### Step 1: Extract Transaction ID
```python
transaction_id = payload.get('transid')  # '5aae72e0e5974f0e8319394167d7708f'
```

### Step 2: Find PaymentTransaction
```python
transaction = PaymentTransaction.objects.filter(
    gateway_transaction_id=transaction_id
).first()
```

### Step 3: If Not Found, Use utilityref
```python
# utilityref: 'BOOKING-HSE-000009-1767956005'
# Extract: 'HSE-000009' (booking reference)
booking = Booking.objects.filter(booking_reference__icontains='HSE-000009').first()
payment = Payment.objects.filter(booking=booking).order_by('-created_at').first()
```

---

## Testing

**After this fix, when you test again:**

1. **Webhook received** ✅
2. **Transaction ID extracted** ✅ (from `transid`)
3. **Payment found** ✅ (by transaction_id or utilityref)
4. **Status updated** ✅ (from `transactionstatus`)
5. **Payment marked as completed** ✅

---

## Expected Log Output (After Fix)

```
[INFO] AzamPay webhook received
[INFO] Webhook payload: {...}
[INFO] Parsed webhook data: {'transaction_id': '5aae72e0e5974f0e8319394167d7708f', ...}
[INFO] After direct extraction: {'transaction_id': '5aae72e0e5974f0e8319394167d7708f', ...}
[INFO] Looking for payment - payment_id: None, transaction_id: '5aae72e0e5974f0e8319394167d7708f', utilityref: 'BOOKING-HSE-000009-1767956005'
[INFO] Found payment by transaction ID: {payment.id}
[INFO] Payment {payment.id} marked as completed
[INFO] Transaction {transaction.id} and Payment {payment.id} updated successfully
```

---

## Files Modified

1. **`payments/gateway_service.py`**
   - Updated `parse_webhook_payload()` to handle `transid` and `transactionstatus`

2. **`payments/api_views.py`**
   - Enhanced direct extraction from payload
   - Added utilityref-based payment lookup
   - Improved transaction status handling

---

## Next Steps

1. **Restart Django server** (to load updated code)
2. **Test payment again**
3. **Verify webhook processes correctly**
4. **Check payment status updates**

---

**Status:** ✅ Fixed - Ready to test again
