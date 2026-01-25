# Mobile App Payment Integration Guide

**Base URL:** `https://portal.maishaapp.co.tz/api/v1/` (or your API base URL)

**Authentication:** All endpoints require JWT Bearer Token:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Payment Types Overview

Your backend supports **3 types of payments**:

| Payment Type | Use Case | Base Endpoint |
|-------------|----------|---------------|
| **Booking Payment** | Pay for hotel/lodge/venue bookings | `/payments/payments/` |
| **Rent Payment** | Pay monthly rent for houses | `/rent/payments/` |
| **Visit Payment** | Pay one-time fee to view house contact info | `/properties/{id}/visit/` |

---

## 🔄 Payment Flow Diagrams

### Flow 1: Booking Payment (Hotel/Lodge/Venue)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Create Payment Record                              │
│ POST /api/v1/payments/payments/                            │
│ Body: {                                                     │
│   "booking": 123,                                           │
│   "amount": "50000.00",                                     │
│   "payment_method": "mobile_money",                         │
│   "mobile_money_provider": "AIRTEL"                         │
│ }                                                           │
│ → Returns: payment_id (e.g., 69)                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Initiate Gateway Payment                           │
│ POST /api/v1/payments/payments/{payment_id}/initiate-gateway/ │
│ Body: { "mobile_money_provider": "AIRTEL" } (optional)      │
│ → Returns: transaction_id, gateway_transaction_id           │
│ → Customer receives payment prompt on phone                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: User Completes Payment on Phone                    │
│ (AZAM Pay sends payment prompt to customer's phone)         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Check Payment Status (Polling)                     │
│ GET /api/v1/payments/payments/{payment_id}/                │
│ → Status: "pending" → "completed" when successful           │
└─────────────────────────────────────────────────────────────┘
```

**Smart Phone Logic:**
- **Admin/Staff:** Uses customer's phone from booking
- **Customer:** Uses their own profile phone

---

### Flow 2: Rent Payment (House - Monthly Rent)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Get Rent Invoice (Optional)                         │
│ GET /api/v1/rent/invoices/{invoice_id}/                    │
│ → Shows amount due, due_date, status                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Create Rent Payment                                │
│ POST /api/v1/rent/payments/                                │
│ Body: {                                                     │
│   "rent_invoice": 45,                                       │
│   "amount": "150000.00",                                    │
│   "payment_method": "mobile_money",                         │
│   "mobile_money_provider": "AIRTEL"                         │
│ }                                                           │
│ → Returns: payment_id (e.g., 80)                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Initiate Gateway Payment                           │
│ POST /api/v1/rent/payments/{payment_id}/initiate-gateway/  │
│ → Returns: payment_link, transaction_id                     │
│ → Tenant receives payment prompt on phone                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: User Completes Payment                             │
│ (AZAM Pay processes payment)                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Verify Payment (Optional)                          │
│ POST /api/v1/rent/payments/{payment_id}/verify/            │
│ → Confirms payment completion                               │
└─────────────────────────────────────────────────────────────┘
```

**Smart Phone Logic:**
- **Admin/Staff:** Uses tenant's phone from rent_invoice
- **Tenant:** Uses their own profile phone

---

### Flow 3: Visit Payment (House - One-Time Access Fee)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Check Visit Payment Status                          │
│ GET /api/v1/properties/{property_id}/visit/status/         │
│ → If has_paid: false → Show "Visit Only" button             │
│ → If has_paid: true → Show contact info (already paid)      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Initiate Visit Payment                             │
│ POST /api/v1/properties/{property_id}/visit/initiate/      │
│ Body: {                                                     │
│   "payment_method": "mobile_money",                         │
│   "mobile_money_provider": "AIRTEL"                         │
│ }                                                           │
│ → Returns: transaction_id, gateway_transaction_id           │
│ → Customer receives payment prompt on phone                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: User Completes Payment                             │
│ (AZAM Pay processes payment)                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Verify Payment & Get Contact Info                  │
│ POST /api/v1/properties/{property_id}/visit/verify/         │
│ Body: { "transaction_id": "AZM..." }                        │
│ → Returns: owner_contact, location, expires_at             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Access Contact Info Anytime (within 72 hours)      │
│ GET /api/v1/properties/{property_id}/visit/status/          │
│ → Returns contact info if payment still valid               │
└─────────────────────────────────────────────────────────────┘
```

**Smart Phone Logic:**
- **Always uses customer's own phone** (regardless of admin status)

**Important:** Visit payments expire after **72 hours**. After expiration, user must pay again.

---

## 📱 Complete API Reference

### 1. BOOKING PAYMENTS

#### 1.1 Create Booking Payment
```http
POST /api/v1/payments/payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking": 123,
  "amount": "50000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "notes": "Payment for booking HTL-000008"
}
```

**Response:**
```json
{
  "id": 69,
  "booking": 123,
  "amount": "50000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "booking_reference": "HTL-000008",
  "booking_id": 123,
  "created_at": "2026-01-23T05:12:00Z"
}
```

#### 1.2 Initiate Gateway Payment
```http
POST /api/v1/payments/payments/{payment_id}/initiate-gateway/
Authorization: Bearer <token>
Content-Type: application/json

{
  "mobile_money_provider": "AIRTEL"  // Optional if already set
}
```

**Response:**
```json
{
  "success": true,
  "payment_id": 69,
  "transaction_id": 15,
  "transaction_reference": "BOOKING-HTL-000008-1769145132",
  "gateway_transaction_id": "AZM019be9446ac770a2a65c6243434f61d8",
  "message": "Payment initiated successfully. The customer will receive a payment prompt on their phone.",
  "phone_number_used": "255653294241",
  "booking_reference": "HTL-000008"
}
```

#### 1.3 Check Payment Status
```http
GET /api/v1/payments/payments/{payment_id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 69,
  "booking": 123,
  "amount": "50000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "completed",  // pending, completed, failed, cancelled
  "booking_reference": "HTL-000008",
  "created_at": "2026-01-23T05:12:00Z"
}
```

#### 1.4 List All Payments
```http
GET /api/v1/payments/payments/?status=completed&payment_method=mobile_money
Authorization: Bearer <token>
```

---

### 2. RENT PAYMENTS

#### 2.1 Get Rent Invoice
```http
GET /api/v1/rent/invoices/{invoice_id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 45,
  "invoice_number": "INV-202601-ABC123",
  "tenant": 10,
  "due_date": "2026-02-05",
  "total_amount": "150000.00",
  "amount_paid": "0.00",
  "status": "pending",
  "period_start": "2026-01-01",
  "period_end": "2026-01-31"
}
```

#### 2.2 Create Rent Payment
```http
POST /api/v1/rent/payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "rent_invoice": 45,
  "amount": "150000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "reference_number": "REF-12345"
}
```

**Response:**
```json
{
  "id": 80,
  "rent_invoice": 45,
  "amount": "150000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "created_at": "2026-01-23T05:12:00Z"
}
```

#### 2.3 Initiate Gateway Payment
```http
POST /api/v1/rent/payments/{payment_id}/initiate-gateway/
Authorization: Bearer <token>
```

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

#### 2.4 Verify Payment
```http
POST /api/v1/rent/payments/{payment_id}/verify/
Authorization: Bearer <token>
```

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

---

### 3. VISIT PAYMENTS

#### 3.1 Check Visit Payment Status
```http
GET /api/v1/properties/{property_id}/visit/status/
Authorization: Bearer <token>
```

**Response (Not Paid):**
```json
{
  "has_paid": false,
  "visit_cost": 5000.00,
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
  "property_title": "Beautiful 3 Bedroom House",
  "owner_contact": {
    "phone": "+255700000000",
    "email": "owner@example.com",
    "name": "John Doe"
  },
  "location": {
    "address": "123 Main Street, Dar es Salaam",
    "region": "Dar es Salaam",
    "district": "Kinondoni",
    "latitude": -6.7924,
    "longitude": 39.2083
  },
  "paid_at": "2025-11-26T10:30:00Z"
}
```

#### 3.2 Initiate Visit Payment
```http
POST /api/v1/properties/{property_id}/visit/initiate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment initiated successfully. You will receive a payment prompt on your phone.",
  "payment_id": 70,
  "visit_payment_id": 45,
  "transaction_id": 16,
  "gateway_transaction_id": "AZM019be9446ac770a2a65c6243434f61d8",
  "transaction_reference": "VISIT-70-1769145132",
  "phone_number_used": "255653294241",
  "amount": 5000.00,
  "property_id": 123,
  "property_title": "Beautiful 3 Bedroom House"
}
```

#### 3.3 Verify Visit Payment
```http
POST /api/v1/properties/{property_id}/visit/verify/
Authorization: Bearer <token>
Content-Type: application/json

{
  "transaction_id": "AZM019be9446ac770a2a65c6243434f61d8"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payment verified successfully",
  "owner_contact": {
    "phone": "+255700000000",
    "email": "owner@example.com",
    "name": "John Doe"
  },
  "location": {
    "address": "123 Main Street, Dar es Salaam",
    "region": "Dar es Salaam",
    "district": "Kinondoni",
    "latitude": -6.7924,
    "longitude": 39.2083
  },
  "paid_at": "2025-11-26T10:30:00Z",
  "expires_at": "2025-11-29T10:30:00Z"
}
```

---

## 🔑 Important Details

### Mobile Money Providers
- `AIRTEL` - Airtel Money
- `TIGO` - Tigo Pesa
- `MPESA` - M-Pesa (Vodacom)
- `HALOPESA` - HaloPesa

### Payment Methods
- `mobile_money` - Mobile money payment via AZAM Pay
- `online` - Online payment (bank card)
- `cash` - Cash payment (manual)

### Payment Status Values
- `pending` - Payment initiated, waiting for completion
- `completed` - Payment successful
- `failed` - Payment failed
- `cancelled` - Payment cancelled

### Smart Phone Logic Summary
| Payment Type | Admin/Staff | Customer |
|-------------|------------|----------|
| **Booking Payment** | Customer's phone from booking | Own profile phone |
| **Rent Payment** | Tenant's phone from invoice | Own profile phone |
| **Visit Payment** | Own profile phone | Own profile phone |

### Visit Payment Expiration
- Visit payments expire **72 hours** after payment
- After expiration, user must pay again to access contact info
- Check `expires_at` field in response

---

## 💡 Mobile App Implementation Tips

### 1. Payment Status Polling
After initiating payment, poll the status endpoint every 2-3 seconds:
```javascript
// Example polling logic
const checkPaymentStatus = async (paymentId) => {
  const response = await fetch(`/api/v1/payments/payments/${paymentId}/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const payment = await response.json();
  
  if (payment.status === 'completed') {
    // Payment successful - show success message
    return true;
  } else if (payment.status === 'failed') {
    // Payment failed - show error message
    return false;
  }
  // Still pending - continue polling
  return null;
};
```

### 2. Error Handling
Always handle these error scenarios:
- Network errors
- Authentication errors (401)
- Payment already completed (400)
- Invalid payment method/provider (400)
- Payment not found (404)

### 3. User Experience Flow
1. Show loading spinner when initiating payment
2. Display "Waiting for payment..." message after initiation
3. Poll status every 2-3 seconds
4. Show success/error message based on status
5. Redirect to appropriate screen after completion

### 4. Visit Payment Flow
- Always check status first before showing payment button
- If `has_paid: true`, show contact info directly
- If expired, show payment button again
- Store `expires_at` to check expiration client-side

---

## 📚 Additional Resources

### Swagger Documentation
Access full interactive API documentation:
- **Swagger UI:** `/api/schema/swagger-ui/` or `/swagger/`
- **ReDoc:** `/api/schema/redoc/` or `/redoc/`
- **Schema JSON:** `/api/schema/` or `/swagger.json`

### Related Documentation Files
- `MOBILE_APP_PAYMENT_APIS.md` - Complete API reference
- `PAYMENT_APIS_DOCUMENTATION.md` - Detailed API documentation
- `payments/AZAM_PAY_INTEGRATION_GUIDE.md` - AZAM Pay integration details

---

## ✅ API Status

✅ **All APIs are working**  
✅ **All APIs are documented in Swagger**  
✅ **Smart phone logic implemented**  
✅ **Phone numbers stored and returned**  
✅ **Ready for mobile app integration**

---

## 🚀 Quick Start Example

### Booking Payment Example (JavaScript/TypeScript)
```typescript
// Step 1: Create payment
const createPayment = async (bookingId: number, amount: string) => {
  const response = await fetch('/api/v1/payments/payments/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      booking: bookingId,
      amount: amount,
      payment_method: 'mobile_money',
      mobile_money_provider: 'AIRTEL'
    })
  });
  return await response.json();
};

// Step 2: Initiate gateway payment
const initiatePayment = async (paymentId: number) => {
  const response = await fetch(
    `/api/v1/payments/payments/${paymentId}/initiate-gateway/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mobile_money_provider: 'AIRTEL'
      })
    }
  );
  return await response.json();
};

// Step 3: Poll payment status
const pollPaymentStatus = async (paymentId: number): Promise<boolean> => {
  return new Promise((resolve) => {
    const interval = setInterval(async () => {
      const response = await fetch(
        `/api/v1/payments/payments/${paymentId}/`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const payment = await response.json();
      
      if (payment.status === 'completed') {
        clearInterval(interval);
        resolve(true);
      } else if (payment.status === 'failed') {
        clearInterval(interval);
        resolve(false);
      }
    }, 2000); // Poll every 2 seconds
  });
};

// Usage
const processBookingPayment = async (bookingId: number, amount: string) => {
  try {
    // Create payment
    const payment = await createPayment(bookingId, amount);
    console.log('Payment created:', payment.id);
    
    // Initiate gateway payment
    const gatewayResponse = await initiatePayment(payment.id);
    console.log('Payment initiated:', gatewayResponse.message);
    console.log('Phone number used:', gatewayResponse.phone_number_used);
    
    // Poll for completion
    const success = await pollPaymentStatus(payment.id);
    if (success) {
      console.log('Payment completed successfully!');
    } else {
      console.log('Payment failed');
    }
  } catch (error) {
    console.error('Payment error:', error);
  }
};
```

---

**Need Help?** Check the Swagger documentation or refer to the detailed API documentation files in the project.
