# Payment APIs Documentation

## Complete List of Payment APIs for Mobile App

**Base URL:** `/api/v1/payments/`

**Authentication:** JWT Bearer Token required (except webhook)

---

## 1. Payment Providers APIs

### 1.1 List Payment Providers
- **Endpoint:** `GET /api/v1/payments/providers/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get all available payment providers (AZAM Pay, etc.)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

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

## 2. Payment APIs (Main - Booking Payments)

### 2.1 List Payments
- **Endpoint:** `GET /api/v1/payments/payments/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get all payments (filtered by user - tenants see only their payments, staff see all)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

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
      "mobile_money_provider": "AIRTEL",
      "status": "pending",
      "booking_reference": "HTL-000008",
      "booking_id": 123,
      "created_at": "2026-01-23T05:12:00Z"
    }
  ]
}
```

---

### 2.2 Create Payment
- **Endpoint:** `POST /api/v1/payments/payments/`
- **Method:** POST
- **Auth:** ✅ Required
- **Description:** Create a new payment for booking (hotel, house, lodge, venue)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

**Request Body:**
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

### 2.3 Get Payment Details
- **Endpoint:** `GET /api/v1/payments/payments/{id}/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get specific payment details
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

**Response:**
```json
{
  "id": 69,
  "booking": 123,
  "amount": "50000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "transaction_ref": null,
  "booking_reference": "HTL-000008",
  "booking_id": 123,
  "created_at": "2026-01-23T05:12:00Z"
}
```

---

### 2.4 Update Payment
- **Endpoint:** `PUT /api/v1/payments/payments/{id}/` or `PATCH /api/v1/payments/payments/{id}/`
- **Method:** PUT/PATCH
- **Auth:** ✅ Required
- **Description:** Update payment details
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

### 2.5 Delete Payment
- **Endpoint:** `DELETE /api/v1/payments/payments/{id}/`
- **Method:** DELETE
- **Auth:** ✅ Required
- **Description:** Delete a payment
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

### 2.6 Initiate Gateway Payment (NEW - Booking Payments)
- **Endpoint:** `POST /api/v1/payments/payments/{id}/initiate-gateway/`
- **Method:** POST
- **Auth:** ✅ Required
- **Description:** Initiate AZAM Pay gateway payment for booking (hotel, house, lodge, venue). Uses smart phone logic.
- **Swagger:** ✅ **FULLY DOCUMENTED** with `@swagger_auto_schema`
- **Status:** ✅ **WORKING** - Fully implemented

**Request Body:**
```json
{
  "mobile_money_provider": "AIRTEL"  // Optional if already set in payment
}
```

**Response (Success):**
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

**Response (Error):**
```json
{
  "error": "Payment already completed"
}
```

**Smart Phone Logic:**
- **Admin/Staff:** Uses customer phone from booking
- **Customer:** Uses their own profile phone
- Phone number is stored in transaction payload
- Phone number is returned in response

---

## 3. Payment Transaction APIs

### 3.1 List Transactions
- **Endpoint:** `GET /api/v1/payments/transactions/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get all payment transactions (filtered by user)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 15,
      "payment": 69,
      "provider": 1,
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

### 3.2 Get Transaction Details
- **Endpoint:** `GET /api/v1/payments/transactions/{id}/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get specific transaction details
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

## 4. Invoice APIs

### 4.1 List Invoices
- **Endpoint:** `GET /api/v1/payments/invoices/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get all invoices (filtered by user)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

### 4.2 Create Invoice
- **Endpoint:** `POST /api/v1/payments/invoices/`
- **Method:** POST
- **Auth:** ✅ Required (Staff only)
- **Description:** Create a new invoice
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

### 4.3 Get Invoice Details
- **Endpoint:** `GET /api/v1/payments/invoices/{id}/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get specific invoice details
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

## 5. Payment Audit APIs

### 5.1 List Payment Audits
- **Endpoint:** `GET /api/v1/payments/audits/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get payment audit logs (read-only)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

## 6. Expense APIs

### 6.1 List Expenses
- **Endpoint:** `GET /api/v1/payments/expenses/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Get all expenses (filtered by property owner)
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

### 6.2 Create Expense
- **Endpoint:** `POST /api/v1/payments/expenses/`
- **Method:** POST
- **Auth:** ✅ Required (Staff/Property Owner)
- **Description:** Create a new expense
- **Swagger:** ✅ Auto-documented (ViewSet)
- **Status:** ✅ Working

---

## 7. Visit Payment APIs (House Properties Only)

**Base URL:** `/api/v1/properties/{property_id}/visit/`

**Note:** Visit payments are only available for **house properties**. They allow users to pay a one-time fee to access owner contact information and property location.

---

### 7.1 Check Visit Payment Status
- **Endpoint:** `GET /api/v1/properties/{property_id}/visit/status/`
- **Method:** GET
- **Auth:** ✅ Required
- **Description:** Check if the current user has already paid for visit access to a house property
- **Swagger:** ✅ Auto-documented with `@extend_schema`
- **Status:** ✅ Working

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

### 7.2 Initiate Visit Payment
- **Endpoint:** `POST /api/v1/properties/{property_id}/visit/initiate/`
- **Method:** POST
- **Auth:** ✅ Required
- **Description:** Initiate AZAM Pay gateway payment for visit access. Uses smart phone logic (always uses customer's own phone).
- **Swagger:** ✅ Auto-documented with `@extend_schema`
- **Status:** ✅ **WORKING** - Fully implemented

**Request Body:**
```json
{
  "payment_method": "mobile_money",  // Optional, default: "mobile_money"
  "mobile_money_provider": "AIRTEL"  // Required for mobile_money: AIRTEL, TIGO, MPESA, HALOPESA
}
```

**Response (Success):**
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

**Response (Already Paid):**
```json
{
  "success": true,
  "message": "Visit payment already completed and active",
  "payment_id": 45,
  "status": "completed",
  "expires_at": "2025-11-29T10:30:00Z"
}
```

**Smart Phone Logic:**
- **Always uses customer's own phone** (the user making the payment)
- Works for both regular customers and admin/staff (they pay for themselves to visit)
- Phone number is stored in transaction payload
- Phone number is returned in response

---

### 7.3 Verify Visit Payment
- **Endpoint:** `POST /api/v1/properties/{property_id}/visit/verify/`
- **Method:** POST
- **Auth:** ✅ Required
- **Description:** Verify payment completion and retrieve owner contact information and location
- **Swagger:** ✅ Auto-documented with `@extend_schema`
- **Status:** ✅ **WORKING** - Fully implemented

**Request Body:**
```json
{
  "transaction_id": "AZM019be9446ac770a2a65c6243434f61d8"
}
```

**Response (Success):**
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

**Response (Already Verified):**
```json
{
  "success": true,
  "message": "Payment already verified",
  "owner_contact": { ... },
  "location": { ... },
  "paid_at": "2025-11-26T10:30:00Z",
  "expires_at": "2025-11-29T10:30:00Z",
  "is_expired": false
}
```

**Response (Expired):**
```json
{
  "success": false,
  "error": "Visit payment has expired. Please pay again to access property details.",
  "is_expired": true,
  "paid_at": "2025-11-26T10:30:00Z",
  "expires_at": "2025-11-29T10:30:00Z"
}
```

**Important Notes:**
- Visit payment expires **72 hours** after payment
- After expiration, user must pay again to access contact info
- One-time payment per property per user (until expiration)

---

## 8. Webhook API

### 8.1 AZAM Pay Webhook
- **Endpoint:** `POST /api/v1/payments/webhook/azam-pay/`
- **Method:** POST
- **Auth:** ❌ No authentication (called by AZAM Pay)
- **Description:** Webhook endpoint for AZAM Pay payment notifications
- **Swagger:** ❌ **Intentionally NOT documented** (standard practice - webhooks are not documented in Swagger)
- **Status:** ✅ Working

**Note:** This endpoint is called by AZAM Pay, not by mobile app. Mobile app should not call this directly.

---

## Summary Table

| Endpoint | Method | Auth | Swagger | Status | Purpose |
|----------|--------|------|---------|--------|---------|
| `/providers/` | GET | ✅ | ✅ | ✅ | List payment providers |
| `/payments/` | GET | ✅ | ✅ | ✅ | List payments |
| `/payments/` | POST | ✅ | ✅ | ✅ | Create payment |
| `/payments/{id}/` | GET | ✅ | ✅ | ✅ | Get payment details |
| `/payments/{id}/` | PUT/PATCH | ✅ | ✅ | ✅ | Update payment |
| `/payments/{id}/` | DELETE | ✅ | ✅ | ✅ | Delete payment |
| `/payments/{id}/initiate-gateway/` | POST | ✅ | ✅ | ✅ | **Initiate AZAM Pay gateway** |
| `/transactions/` | GET | ✅ | ✅ | ✅ | List transactions |
| `/transactions/{id}/` | GET | ✅ | ✅ | ✅ | Get transaction details |
| `/invoices/` | GET/POST | ✅ | ✅ | ✅ | Invoice management |
| `/audits/` | GET | ✅ | ✅ | ✅ | Payment audit logs |
| `/expenses/` | GET/POST | ✅ | ✅ | ✅ | Expense management |
| `/properties/{id}/visit/status/` | GET | ✅ | ✅ | ✅ | Check visit payment status |
| `/properties/{id}/visit/initiate/` | POST | ✅ | ✅ | ✅ | **Initiate visit payment** |
| `/properties/{id}/visit/verify/` | POST | ✅ | ✅ | ✅ | **Verify visit payment** |
| `/webhook/azam-pay/` | POST | ❌ | ❌ | ✅ | AZAM Pay webhook |

---

## Swagger Documentation Status

### ✅ Fully Documented
- All ViewSet endpoints are **auto-documented** by DRF-Spectacular
- Custom action `initiate_gateway` has **explicit `@swagger_auto_schema` decorator** with:
  - Request body schema
  - Response schema
  - Error responses
  - Security requirements
  - Operation description

### Swagger Access
- **Swagger UI:** `/api/schema/swagger-ui/` or `/swagger/`
- **ReDoc:** `/api/schema/redoc/` or `/redoc/`
- **Schema JSON:** `/api/schema/` or `/swagger.json`

---

## Mobile App Integration Flow

### Complete Flow for Booking Payment:

1. **Create Payment**
   ```
   POST /api/v1/payments/payments/
   {
     "booking": 123,
     "amount": "50000.00",
     "payment_method": "mobile_money",
     "mobile_money_provider": "AIRTEL"
   }
   ```

2. **Initiate Gateway Payment**
   ```
   POST /api/v1/payments/payments/{payment_id}/initiate-gateway/
   ```

3. **Customer receives payment prompt** on their phone (smart phone logic)

4. **Payment processed** via AZAM Pay

5. **Webhook updates** payment status automatically

6. **Check Payment Status**
   ```
   GET /api/v1/payments/payments/{payment_id}/
   ```

---

### Complete Flow for Visit Payment (House Properties Only):

1. **Check Visit Payment Status**
   ```
   GET /api/v1/properties/{property_id}/visit/status/
   ```
   - If `has_paid: false`, show "Visit Only" button with `visit_cost` amount
   - If `has_paid: true`, display owner contact and location

2. **Initiate Visit Payment**
   ```
   POST /api/v1/properties/{property_id}/visit/initiate/
   {
     "payment_method": "mobile_money",
     "mobile_money_provider": "AIRTEL"
   }
   ```
   - Response includes `phone_number_used` (customer's own phone)
   - Customer receives payment prompt on their phone

3. **Verify Payment**
   ```
   POST /api/v1/properties/{property_id}/visit/verify/
   {
     "transaction_id": "<transaction_id_from_step_2>"
   }
   ```
   - Returns owner contact and location information
   - Payment expires after 72 hours

4. **Access Contact Info Anytime** (within 72 hours)
   ```
   GET /api/v1/properties/{property_id}/visit/status/
   ```
   - Returns `has_paid: true` with contact information

---

## Verification

✅ **All APIs are working** - Django system check passed  
✅ **All APIs are documented** - ViewSets auto-documented, custom actions explicitly documented  
✅ **Smart phone logic implemented** - Uses correct phone number based on user role and payment type  
✅ **Phone number stored** - Stored in transaction request_payload  
✅ **Phone number returned** - Included in API response  
✅ **Visit payment support** - Fully implemented for house properties with smart phone logic  

---

## Ready for Mobile App

All payment APIs are ready and documented for mobile app integration:

1. **Booking Payments** (`/payments/{id}/initiate-gateway/`)
   - Works for hotel, house, lodge, venue
   - Smart phone logic: Admin uses customer phone, Customer uses own phone

2. **Visit Payments** (`/properties/{id}/visit/initiate/`)
   - Works for **house properties only**
   - Smart phone logic: Always uses customer's own phone (regardless of admin status)
   - One-time payment to access owner contact and location
   - Expires after 72 hours

Both payment types use AZAM Pay gateway and the smart phone logic we implemented.
