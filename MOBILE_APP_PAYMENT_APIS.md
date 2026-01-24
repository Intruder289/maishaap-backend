# Mobile App Payment APIs - Complete List

**Base URL:** Your API base URL (e.g., `https://portal.maishaapp.co.tz/api/v1/`)

**Authentication:** All endpoints require JWT Bearer Token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Quick Reference Table

| Payment Type | Endpoint | Method | Purpose |
|-------------|----------|--------|---------|
| **Booking Payment** | `/payments/payments/{id}/initiate-gateway/` | POST | Pay for hotel/lodge/venue booking |
| **Rent Payment** | `/rent/payments/{id}/initiate-gateway/` | POST | Pay monthly rent (house) |
| **Visit Payment** | `/properties/{id}/visit/initiate/` | POST | Pay to view house contact info |

---

## 1. BOOKING PAYMENTS (Hotel, Lodge, Venue)

### 1.1 Create Booking Payment
**Endpoint:** `POST /api/v1/payments/payments/`

**Request:**
```json
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

---

### 1.2 Initiate Gateway Payment (AZAM Pay)
**Endpoint:** `POST /api/v1/payments/payments/{payment_id}/initiate-gateway/`

**Request:**
```json
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

**Smart Phone Logic:**
- Admin/Staff → Uses customer phone from booking
- Customer → Uses their own profile phone

**Mobile Money Providers:** `AIRTEL`, `TIGO`, `MPESA`, `HALOPESA`

---

### 1.3 Get Payment Status
**Endpoint:** `GET /api/v1/payments/payments/{payment_id}/`

**Response:**
```json
{
  "id": 69,
  "booking": 123,
  "amount": "50000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "completed",
  "booking_reference": "HTL-000008",
  "created_at": "2026-01-23T05:12:00Z"
}
```

**Status Values:** `pending`, `completed`, `failed`, `cancelled`

---

### 1.4 List All Payments
**Endpoint:** `GET /api/v1/payments/payments/`

**Query Parameters:**
- `status` - Filter by status (pending, completed, failed, cancelled)
- `payment_method` - Filter by method (cash, mobile_money, online)
- `booking` - Filter by booking ID

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 69,
      "booking": 123,
      "amount": "50000.00",
      "payment_method": "mobile_money",
      "status": "completed",
      "booking_reference": "HTL-000008",
      "created_at": "2026-01-23T05:12:00Z"
    }
  ]
}
```

---

## 2. RENT PAYMENTS (House - Monthly Rent)

### 2.1 Create Rent Payment
**Endpoint:** `POST /api/v1/rent/payments/`

**Request:**
```json
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

---

### 2.2 Initiate Gateway Payment (AZAM Pay)
**Endpoint:** `POST /api/v1/rent/payments/{payment_id}/initiate-gateway/`

**Request:** (No body required if mobile_money_provider already set)

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

**Smart Phone Logic:**
- Admin/Staff → Uses tenant phone from rent_invoice
- Tenant → Uses their own profile phone

---

### 2.3 Verify Rent Payment
**Endpoint:** `POST /api/v1/rent/payments/{payment_id}/verify/`

**Request:** (No body required)

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

### 2.4 List Rent Payments
**Endpoint:** `GET /api/v1/rent/payments/`

**Query Parameters:**
- `tenant_id` - Filter by tenant (staff only)
- `invoice_id` - Filter by invoice
- `payment_method` - Filter by method

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 80,
      "rent_invoice": 45,
      "amount": "150000.00",
      "payment_method": "mobile_money",
      "status": "completed",
      "created_at": "2026-01-23T05:12:00Z"
    }
  ]
}
```

---

### 2.5 Get Rent Invoice Details
**Endpoint:** `GET /api/v1/rent/invoices/{invoice_id}/`

**Response:**
```json
{
  "id": 45,
  "invoice_number": "INV-202601-ABC123",
  "tenant": 10,
  "due_date": "2026-02-05",
  "total_amount": "150000.00",
  "amount_paid": "150000.00",
  "status": "paid",
  "period_start": "2026-01-01",
  "period_end": "2026-01-31"
}
```

---

## 3. VISIT PAYMENTS (House - One-Time Access Fee)

### 3.1 Check Visit Payment Status
**Endpoint:** `GET /api/v1/properties/{property_id}/visit/status/`

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

---

### 3.2 Initiate Visit Payment
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

**Smart Phone Logic:**
- Always uses customer's own phone (regardless of admin status)

**Note:** Visit payments expire after 72 hours

---

### 3.3 Verify Visit Payment
**Endpoint:** `POST /api/v1/properties/{property_id}/visit/verify/`

**Request:**
```json
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

## 4. PAYMENT TRANSACTIONS

### 4.1 List Transactions
**Endpoint:** `GET /api/v1/payments/transactions/`

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 15,
      "payment": 69,
      "gateway_transaction_id": "AZM019be9446ac770a2a65c6243434f61d8",
      "azam_reference": "BOOKING-HTL-000008-1769145132",
      "status": "initiated",
      "request_payload": {
        "accountNumber": "255653294241",
        "amount": 50000,
        "currency": "TZS",
        "provider": "Airtel"
      },
      "created_at": "2026-01-23T05:12:00Z"
    }
  ]
}
```

---

### 4.2 Get Transaction Details
**Endpoint:** `GET /api/v1/payments/transactions/{transaction_id}/`

---

## 5. PAYMENT PROVIDERS

### 5.1 List Payment Providers
**Endpoint:** `GET /api/v1/payments/providers/`

**Response:**
```json
[
  {
    "id": 1,
    "name": "AZAM Pay",
    "description": "AZAM Pay Payment Gateway"
  }
]
```

---

## 📱 Mobile App Integration Flows

### Flow 1: Booking Payment (Hotel/Lodge/Venue)

```
1. Create Payment
   POST /api/v1/payments/payments/
   Body: { "booking": 123, "amount": "50000.00", "payment_method": "mobile_money", "mobile_money_provider": "AIRTEL" }

2. Initiate Gateway Payment
   POST /api/v1/payments/payments/{payment_id}/initiate-gateway/
   → Customer receives payment prompt on phone

3. Check Payment Status
   GET /api/v1/payments/payments/{payment_id}/
   → Status: "completed" when payment successful
```

---

### Flow 2: Rent Payment (House)

```
1. Get Rent Invoice
   GET /api/v1/rent/invoices/{invoice_id}/
   → Shows amount due

2. Create Payment
   POST /api/v1/rent/payments/
   Body: { "rent_invoice": 45, "amount": "150000.00", "payment_method": "mobile_money", "mobile_money_provider": "AIRTEL" }

3. Initiate Gateway Payment
   POST /api/v1/rent/payments/{payment_id}/initiate-gateway/
   → Tenant receives payment prompt on phone

4. Verify Payment (Optional)
   POST /api/v1/rent/payments/{payment_id}/verify/
   → Confirms payment completion
```

---

### Flow 3: Visit Payment (House)

```
1. Check Visit Payment Status
   GET /api/v1/properties/{property_id}/visit/status/
   → If has_paid: false, show "Visit Only" button

2. Initiate Visit Payment
   POST /api/v1/properties/{property_id}/visit/initiate/
   Body: { "payment_method": "mobile_money", "mobile_money_provider": "AIRTEL" }
   → Customer receives payment prompt on phone

3. Verify Payment
   POST /api/v1/properties/{property_id}/visit/verify/
   Body: { "transaction_id": "AZM..." }
   → Returns owner contact and location

4. Access Contact Info (within 72 hours)
   GET /api/v1/properties/{property_id}/visit/status/
   → Returns owner contact and location
```

---

## 🔑 Important Notes

### Mobile Money Providers
- `AIRTEL` - Airtel Money
- `TIGO` - Tigo Pesa
- `MPESA` - M-Pesa (Vodacom)
- `HALOPESA` - HaloPesa

### Payment Status Values
- `pending` - Payment initiated, waiting for completion
- `completed` - Payment successful
- `failed` - Payment failed
- `cancelled` - Payment cancelled

### Smart Phone Logic Summary
- **Booking Payment:** Admin → Customer phone, Customer → Own phone
- **Rent Payment:** Admin → Tenant phone, Tenant → Own phone
- **Visit Payment:** Always → Customer's own phone

### Visit Payment Expiration
- Visit payments expire **72 hours** after payment
- After expiration, user must pay again to access contact info

---

## ✅ All APIs Status

✅ **All APIs are working**  
✅ **All APIs are documented in Swagger**  
✅ **Smart phone logic implemented**  
✅ **Phone numbers stored and returned**  
✅ **Ready for mobile app integration**

---

## 📚 Swagger Documentation

Access full API documentation:
- **Swagger UI:** `/api/schema/swagger-ui/` or `/swagger/`
- **ReDoc:** `/api/schema/redoc/` or `/redoc/`
- **Schema JSON:** `/api/schema/` or `/swagger.json`
