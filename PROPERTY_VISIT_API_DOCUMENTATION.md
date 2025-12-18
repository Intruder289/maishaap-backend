# Property Visit Payment API Documentation

## Overview
This API allows users to pay a one-time fee to access owner contact information and property location for house properties. Once paid, the user can access this information without paying again.

## Base URL
```
/api/v1/properties/{property_id}/visit/
```

## Authentication
All endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Check Visit Payment Status

**Endpoint:** `GET /api/v1/properties/{property_id}/visit/status/`

**Description:** Check if the current user has already paid for visit access to a house property.

**Request:**
```http
GET /api/v1/properties/123/visit/status/
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

**Error Responses:**
- `400 Bad Request`: Property is not a house property
- `404 Not Found`: Property not found

---

## 2. Initiate Visit Payment

**Endpoint:** `POST /api/v1/properties/{property_id}/visit/initiate/`

**Description:** Initiate a payment for visit access. Creates a payment record and returns a payment link.

**Request:**
```http
POST /api/v1/properties/123/visit/initiate/
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_method": "online"  // Optional, default: "online"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Payment initiated successfully",
  "payment_link": "https://azampay.co.tz/pay/ABC123XYZ",
  "transaction_id": "AZAM-123-1732620000",
  "reference": "VISIT-123-1732620000",
  "visit_payment_id": 45,
  "amount": 5000.00
}
```

**Response (Already Paid):**
```json
{
  "error": "You have already paid for visit access to this property.",
  "has_paid": true,
  "payment_id": 45
}
```

**Response (No Visit Cost Set):**
```json
{
  "error": "Visit cost is not set for this property."
}
```

**Error Responses:**
- `400 Bad Request`: Invalid property, already paid, or visit cost not set
- `404 Not Found`: Property not found
- `500 Internal Server Error`: Payment gateway error

---

## 3. Verify Visit Payment

**Endpoint:** `POST /api/v1/properties/{property_id}/visit/verify/`

**Description:** Verify payment completion and retrieve owner contact information and location.

**Request:**
```http
POST /api/v1/properties/123/visit/verify/
Authorization: Bearer <token>
Content-Type: application/json

{
  "transaction_id": "AZAM-123-1732620000"
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
  "paid_at": "2025-11-26T10:30:00Z"
}
```

**Response (Already Verified):**
```json
{
  "success": true,
  "message": "Payment already verified",
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

**Response (Verification Failed):**
```json
{
  "error": "Payment verification failed",
  "status": "failed"
}
```

**Error Responses:**
- `400 Bad Request`: Missing transaction_id or verification failed
- `404 Not Found`: Visit payment not found
- `500 Internal Server Error`: Server error

---

## Mobile App Integration Flow

### Step 1: Check Payment Status
When user views a house property detail page:
```javascript
GET /api/v1/properties/{property_id}/visit/status/
```

If `has_paid: false`, show "Visit Only" button with `visit_cost` amount.

### Step 2: Initiate Payment
When user clicks "Visit Only" button:
```javascript
POST /api/v1/properties/{property_id}/visit/initiate/
```

Response includes `payment_link` - redirect user to this URL for payment.

### Step 3: Handle Payment Callback
After payment is completed (via webhook or user returns to app):
```javascript
POST /api/v1/properties/{property_id}/visit/verify/
{
  "transaction_id": "<transaction_id_from_step_2>"
}
```

If successful, display owner contact and location information.

### Step 4: Store Payment Status
After successful verification, the user can access contact info anytime by calling:
```javascript
GET /api/v1/properties/{property_id}/visit/status/
```

This will return `has_paid: true` with contact information.

---

## Important Notes

1. **One-Time Payment**: Each user can only pay once per property. Subsequent calls to `/visit/status/` will return contact info without requiring payment.

2. **House Properties Only**: Visit payment is only available for properties where `property_type.name == 'house'`. Other property types will return an error.

3. **Visit Cost Required**: Property must have `visit_cost` set (greater than 0) for visit payment to work.

4. **Payment Gateway**: Currently uses placeholder payment gateway responses. Will be updated once AZAM Pay API documentation is received.

5. **Payment Records**: All payments are tracked in the unified `Payment` model and linked to `PropertyVisitPayment` for visit-specific tracking.

---

## Error Codes

| Status Code | Description |
|------------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid property, already paid, no visit cost) |
| 401 | Unauthorized (missing or invalid JWT token) |
| 404 | Not Found (property or payment not found) |
| 500 | Internal Server Error |

---

## Example Mobile App Code (React Native / Flutter)

### Check Status
```javascript
const checkVisitStatus = async (propertyId, token) => {
  const response = await fetch(
    `${API_BASE_URL}/properties/${propertyId}/visit/status/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return await response.json();
};
```

### Initiate Payment
```javascript
const initiateVisitPayment = async (propertyId, token) => {
  const response = await fetch(
    `${API_BASE_URL}/properties/${propertyId}/visit/initiate/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        payment_method: 'online'
      })
    }
  );
  return await response.json();
};
```

### Verify Payment
```javascript
const verifyVisitPayment = async (propertyId, transactionId, token) => {
  const response = await fetch(
    `${API_BASE_URL}/properties/${propertyId}/visit/verify/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        transaction_id: transactionId
      })
    }
  );
  return await response.json();
};
```

