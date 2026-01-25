# Mobile App Payment APIs & Flow Guide

**Complete Payment Flow for Mobile App Integration**

**Base URL:** `https://portal.maishaapp.co.tz/api/v1/`

**Authentication:** All endpoints require JWT Bearer Token:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Payment Types Overview

| Payment Type | Use Case | Endpoints |
|-------------|----------|-----------|
| **Booking Payment** | Pay for hotel/lodge/venue bookings | `/payments/payments/` |
| **Rent Payment** | Pay monthly house rent | `/rent/payments/` |
| **Visit Payment** | Pay to view house contact info | `/properties/{id}/visit/` |

---

## 🔄 Payment Flow 1: Booking Payments (Hotel, Lodge, Venue)

**Complete flow from booking creation to payment completion.**

### Step-by-Step Flow

```
1. Create Booking → 2. Create Payment → 3. Initiate Gateway → 4. Poll Status → 5. Done!
```

---

### Step 1: Create Booking

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**Request:**
```json
{
  "property_id": 123,
  "property_type": "hotel",  // or "lodge" or "venue"
  "room_number": "101",       // Required for hotel/lodge, NOT for venue
  "room_type": "Deluxe",      // Required for hotel/lodge
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "total_amount": "200000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000"
}
```

**Response:**
```json
{
  "success": true,
  "booking_id": 456,
  "booking_reference": "HTL-000456",
  "total_amount": "200000.00"
}
```

**Save:** `booking_id` (456) for next step

---

### Step 2: Create Payment

**Endpoint:** `POST /api/v1/payments/payments/`

**Request:**
```json
{
  "booking": 456,              // ← Booking ID from Step 1
  "amount": "200000.00",       // ← Amount from booking
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"  // AIRTEL, TIGO, MPESA, HALOPESA
}
```

**Response:**
```json
{
  "id": 80,                    // ← Payment ID (save this!)
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Save:** `id` (80) - this is your `payment_id` for next steps

---

### Step 3: Initiate Payment Gateway ⭐ **CRITICAL**

**Endpoint:** `POST /api/v1/payments/payments/{payment_id}/initiate-gateway/`

**Request:**
```json
{
  "mobile_money_provider": "AIRTEL"  // Optional if already set in Step 2
}
```

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "transaction_id": 20,
  "transaction_reference": "HTL-80-1769145132",
  "phone_number_used": "+255700000000",  // ← Phone that will receive prompt
  "message": "Payment initiated successfully. The customer will receive a payment prompt on their phone."
}
```

**What Happens:**
- ✅ Payment prompt sent to phone number shown in `phone_number_used`
- ✅ Customer receives AZAM Pay prompt on their phone
- ✅ Customer approves/rejects payment on phone

**Mobile App Should:**
- Show message: "Payment prompt sent to +255700000000"
- Show instruction: "Please approve payment on your phone"
- Start polling payment status (Step 4)

---

### Step 4: Poll Payment Status ⭐ **CRITICAL**

**Endpoint:** `GET /api/v1/payments/payments/{payment_id}/`

**Poll every 2-3 seconds until status changes**

**Response (Pending):**
```json
{
  "id": 80,
  "status": "pending",  // ← Still waiting
  "amount": "200000.00",
  "booking_reference": "HTL-000456"
}
```

**Response (Completed):**
```json
{
  "id": 80,
  "status": "completed",  // ← Payment successful! ✅
  "amount": "200000.00",
  "booking_reference": "HTL-000456",
  "updated_at": "2026-01-25T10:35:00Z"
}
```

**Response (Failed):**
```json
{
  "id": 80,
  "status": "failed",  // ← Payment failed ❌
  "amount": "200000.00"
}
```

**Mobile App Polling Logic:**
```typescript
// Poll every 2-3 seconds, max 60 attempts (2-3 minutes)
async function pollPaymentStatus(paymentId: number) {
  let attempts = 0;
  const maxAttempts = 60;
  
  const interval = setInterval(async () => {
    attempts++;
    
    const response = await fetch(
      `https://portal.maishaapp.co.tz/api/v1/payments/payments/${paymentId}/`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    const payment = await response.json();
    
    if (payment.status === 'completed') {
      clearInterval(interval);
      // ✅ Show success message
      return { success: true, payment };
    }
    
    if (payment.status === 'failed' || payment.status === 'cancelled') {
      clearInterval(interval);
      // ❌ Show error message
      return { success: false, error: payment.status };
    }
    
    if (attempts >= maxAttempts) {
      clearInterval(interval);
      // ⏱️ Show timeout message
      return { success: false, error: 'timeout' };
    }
  }, 2000); // Check every 2 seconds
}
```

---

### Step 5: Payment Complete! ✅

**Status:** `completed`

**Mobile App Should:**
- Show success message
- Display booking reference: `HTL-000456`
- Redirect to booking confirmation screen

---

## 🔄 Payment Flow 2: Rent Payments (House)

**Complete flow for paying monthly house rent.**

### Step-by-Step Flow

```
1. Get Invoice → 2. Create Payment → 3. Initiate Gateway → 4. Verify (Optional) → 5. Poll Status → 6. Done!
```

---

### Step 1: Get Rent Invoice

**Endpoint:** `GET /api/v1/rent/invoices/`

**Query Parameters:**
- `status` - Filter: `pending`, `paid`, `overdue`

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 45,                    // ← Invoice ID (save this!)
      "invoice_number": "INV-202601-ABC123",
      "due_date": "2026-02-05",
      "total_amount": "150000.00",  // ← Amount to pay
      "amount_paid": "0.00",
      "status": "pending",
      "period_start": "2026-01-01",
      "period_end": "2026-01-31"
    }
  ]
}
```

**Save:** `id` (45) - this is your `invoice_id` for Step 2

---

### Step 2: Create Rent Payment

**Endpoint:** `POST /api/v1/rent/payments/`

**Request:**
```json
{
  "rent_invoice": 45,              // ← Invoice ID from Step 1
  "amount": "150000.00",           // ← Amount from invoice
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "reference_number": "REF-12345"   // Optional: your reference
}
```

**Response:**
```json
{
  "id": 80,                        // ← Payment ID (save this!)
  "rent_invoice": 45,
  "amount": "150000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Save:** `id` (80) - this is your `payment_id` for next steps

---

### Step 3: Initiate Gateway Payment ⭐ **CRITICAL**

**Endpoint:** `POST /api/v1/rent/payments/{payment_id}/initiate-gateway/`

**Request:** (No body needed)

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "transaction_id": 20,
  "payment_link": "https://checkout.azampay.co.tz/...",
  "transaction_reference": "RENT-80-1769145132",
  "message": "Payment initiated successfully. Redirect user to payment_link."
}
```

**What Happens:**
- ✅ Payment prompt sent to tenant's phone
- ✅ Tenant receives AZAM Pay prompt on their phone
- ✅ Tenant approves/rejects payment on phone

**Mobile App Should:**
- Show message: "Payment prompt sent to your phone"
- Show instruction: "Please approve payment on your phone"
- Start polling payment status (Step 5)

---

### Step 4: Verify Payment (Optional)

**Endpoint:** `POST /api/v1/rent/payments/{payment_id}/verify/`

**Request:** (No body needed)

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "status": "completed",
  "transaction_status": "successful",
  "verified": true
}
```

**Note:** This step is optional. You can skip to Step 5 (polling) instead.

---

### Step 5: Poll Payment Status ⭐ **CRITICAL**

**Endpoint:** `GET /api/v1/rent/payments/{payment_id}/`

**Poll every 2-3 seconds until status changes**

**Response (Completed):**
```json
{
  "id": 80,
  "status": "completed",  // ← Payment successful! ✅
  "amount": "150000.00",
  "rent_invoice": 45
}
```

**Use same polling logic as Booking Payments (Step 4)**

---

### Step 6: Payment Complete! ✅

**Status:** `completed`

**Mobile App Should:**
- Show success message
- Display invoice number: `INV-202601-ABC123`
- Update invoice list

---

## 🔄 Payment Flow 3: Visit Payments (House - View Contact)

**Pay one-time fee to view house owner contact information.**

### Step-by-Step Flow

```
1. Check Status → 2. Initiate Payment → 3. Verify → 4. Get Contact → 5. Done!
```

---

### Step 1: Check Visit Payment Status

**Endpoint:** `GET /api/v1/properties/{property_id}/visit/status/`

**Response (Not Paid):**
```json
{
  "has_paid": false,
  "visit_cost": 5000.00,        // ← Amount to pay
  "property_id": 123,
  "property_title": "Beautiful 3 Bedroom House"
}
```

**Response (Already Paid):**
```json
{
  "has_paid": true,
  "visit_cost": 5000.00,
  "property_id": 123,
  "owner_contact": {
    "name": "John Owner",
    "phone": "+255700000000",
    "email": "owner@example.com"
  },
  "property_location": {
    "address": "123 Main Street",
    "latitude": "-6.7924",
    "longitude": "39.2083"
  },
  "expires_at": "2026-01-28T10:30:00Z"  // Valid for 72 hours
}
```

**If `has_paid: false`** → Proceed to Step 2  
**If `has_paid: true`** → Skip to Step 4 (already paid, show contact)

---

### Step 2: Initiate Visit Payment

**Endpoint:** `POST /api/v1/properties/{property_id}/visit/initiate/`

**Request:**
```json
{
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"
}
```

**Response:**
```json
{
  "success": true,
  "payment_id": 90,
  "transaction_id": 25,
  "phone_number_used": "+255700000000",
  "message": "Payment initiated successfully. Please approve payment on your phone."
}
```

**What Happens:**
- ✅ Payment prompt sent to user's phone
- ✅ User receives AZAM Pay prompt
- ✅ User approves/rejects payment on phone

**Mobile App Should:**
- Show message: "Payment prompt sent to your phone"
- Wait for user to approve payment
- Proceed to Step 3 after a few seconds

---

### Step 3: Verify Payment

**Endpoint:** `POST /api/v1/properties/{property_id}/visit/verify/`

**Request:**
```json
{
  "transaction_id": 25  // ← From Step 2 response
}
```

**Response:**
```json
{
  "success": true,
  "has_paid": true,
  "owner_contact": {
    "name": "John Owner",
    "phone": "+255700000000",
    "email": "owner@example.com"
  },
  "property_location": {
    "address": "123 Main Street",
    "latitude": "-6.7924",
    "longitude": "39.2083"
  },
  "expires_at": "2026-01-28T10:30:00Z"
}
```

---

### Step 4: Get Contact Information

**Endpoint:** `GET /api/v1/properties/{property_id}/visit/status/`

**Response:** (Same as Step 1 - Already Paid)

**Mobile App Should:**
- Display owner contact information
- Show property location
- Show expiration time (72 hours from payment)

---

### Step 5: Payment Complete! ✅

**Contact information is now available for 72 hours**

---

## 📊 Payment Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| `pending` | Payment initiated, waiting for approval | Keep polling |
| `completed` | Payment successful ✅ | Show success |
| `failed` | Payment failed ❌ | Show error, allow retry |
| `cancelled` | Payment cancelled ❌ | Show cancelled message |

---

## 💳 Payment Providers

| Provider | Code | Description |
|----------|------|-------------|
| Airtel Money | `AIRTEL` | Airtel mobile money |
| Tigo Pesa | `TIGO` | Tigo mobile money |
| M-Pesa | `MPESA` | Vodacom M-Pesa |
| HaloPesa | `HALOPESA` | HaloPesa mobile money |

---

## 🔑 Key Points

### 1. **Smart Phone Logic** ✅
- **Booking Payments (Admin):** Uses customer's phone from booking
- **Booking Payments (Customer):** Uses customer's own profile phone
- **Rent Payments:** Uses tenant's profile phone
- **Visit Payments:** Uses user's own profile phone

**No manual phone selection needed!** Backend automatically selects correct phone.

### 2. **Payment Polling** ⏱️
- Poll every **2-3 seconds**
- Maximum **60 attempts** (2-3 minutes)
- Stop when status is `completed`, `failed`, or `cancelled`

### 3. **Error Handling** ❌
- **400 Bad Request:** Invalid data (check request body)
- **401 Unauthorized:** Invalid/expired token (re-login)
- **404 Not Found:** Payment/booking not found
- **500 Server Error:** Server issue (retry later)

### 4. **Payment Expiration** ⏰
- **Visit Payments:** Expire after **72 hours**
- **Booking/Rent Payments:** No expiration (one-time payment)

---

## 📱 Complete Mobile App Flow Example

```typescript
// Complete Booking Payment Flow
async function completeBookingPayment(bookingId: number, amount: string, provider: string) {
  try {
    // Step 1: Create Payment
    const payment = await fetch('/api/v1/payments/payments/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        booking: bookingId,
        amount: amount,
        payment_method: 'mobile_money',
        mobile_money_provider: provider,
      }),
    }).then(r => r.json());
    
    // Step 2: Initiate Gateway
    const gateway = await fetch(
      `/api/v1/payments/payments/${payment.id}/initiate-gateway/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mobile_money_provider: provider }),
      }
    ).then(r => r.json());
    
    // Step 3: Poll Status
    let status = 'pending';
    let attempts = 0;
    
    while (status === 'pending' && attempts < 60) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      
      const check = await fetch(
        `/api/v1/payments/payments/${payment.id}/`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      ).then(r => r.json());
      
      status = check.status;
      attempts++;
      
      if (status === 'completed') {
        return { success: true, payment: check };
      }
      
      if (status === 'failed' || status === 'cancelled') {
        return { success: false, error: status };
      }
    }
    
    return { success: false, error: 'timeout' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

---

## ✅ Quick Reference

### Booking Payment Endpoints
1. `POST /api/v1/payments/payments/` - Create payment
2. `POST /api/v1/payments/payments/{id}/initiate-gateway/` - Initiate payment
3. `GET /api/v1/payments/payments/{id}/` - Check status

### Rent Payment Endpoints
1. `GET /api/v1/rent/invoices/` - Get invoices
2. `POST /api/v1/rent/payments/` - Create payment
3. `POST /api/v1/rent/payments/{id}/initiate-gateway/` - Initiate payment
4. `POST /api/v1/rent/payments/{id}/verify/` - Verify payment (optional)
5. `GET /api/v1/rent/payments/{id}/` - Check status

### Visit Payment Endpoints
1. `GET /api/v1/properties/{id}/visit/status/` - Check status
2. `POST /api/v1/properties/{id}/visit/initiate/` - Initiate payment
3. `POST /api/v1/properties/{id}/visit/verify/` - Verify payment

---

## 🎯 Summary

**All payment flows follow this pattern:**
1. **Create Payment** → Get payment ID
2. **Initiate Gateway** → Send payment prompt to phone
3. **Poll Status** → Check every 2-3 seconds until completed
4. **Show Result** → Success or error message

**Ready for Mobile App Integration!** 🚀
