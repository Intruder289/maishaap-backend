# Complete Mobile App API Summary

**All APIs Available for Mobile App Consumption**

**Base URL:** `https://portal.maishaapp.co.tz/api/v1/`

**Authentication:** All endpoints require JWT Bearer Token:
```
Authorization: Bearer <your_jwt_token>
```

---

## ✅ Implementation Status: 100% COMPLETE

| Booking/Payment Type | Booking API | Payment API | Status |
|----------------------|-------------|-------------|--------|
| **Hotel** | ✅ REST API | ✅ REST API | ✅ **READY** |
| **Lodge** | ✅ REST API | ✅ REST API | ✅ **READY** |
| **Venue** | ✅ REST API | ✅ REST API | ✅ **READY** |
| **House Rent** | N/A (uses invoices) | ✅ REST API | ✅ **READY** |

---

## 📋 Complete API List

### 1. HOTEL BOOKINGS ✅

#### 1.1 Get Available Rooms
```http
GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=2026-02-01&check_out_date=2026-02-05
```

#### 1.2 Create Booking
```http
POST /api/v1/properties/bookings/create/
{
  "property_id": 123,
  "property_type": "hotel",
  "room_number": "10",
  "room_type": "Deluxe",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "total_amount": "200000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000"
}
```

#### 1.3 Create Payment
```http
POST /api/v1/payments/payments/
{
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"
}
```

#### 1.4 Initiate Payment
```http
POST /api/v1/payments/payments/{payment_id}/initiate-gateway/
```

#### 1.5 Check Payment Status
```http
GET /api/v1/payments/payments/{payment_id}/
```

---

### 2. LODGE BOOKINGS ✅

**Same endpoints as Hotel, use `property_type: "lodge"`**

#### 2.1 Get Available Rooms
```http
GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=2026-02-01&check_out_date=2026-02-05
```

#### 2.2 Create Booking
```http
POST /api/v1/properties/bookings/create/
{
  "property_id": 123,
  "property_type": "lodge",  // ← Use "lodge"
  "room_number": "10",
  "room_type": "Deluxe",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "total_amount": "200000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000"
}
```

#### 2.3-2.5 Payment APIs
Same as Hotel (Steps 1.3-1.5)

---

### 3. VENUE BOOKINGS ✅

#### 3.1 Create Booking
```http
POST /api/v1/properties/bookings/create/
{
  "property_id": 123,
  "property_type": "venue",  // ← Use "venue"
  "event_name": "Wedding Reception",
  "event_type": "Wedding",
  "event_date": "2026-02-15",  // Used as check_in_date
  "check_out_date": "2026-02-15",  // Optional, defaults to event_date
  "expected_guests": 200,
  "total_amount": "500000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000",
  "special_requests": "Need sound system"
}
```

**Response:**
```json
{
  "success": true,
  "booking_id": 789,
  "booking_reference": "VEN-000789",
  "event_name": "Wedding Reception",
  "event_type": "Wedding",
  "event_date": "2026-02-15",
  "message": "Booking VEN-000789 created successfully!"
}
```

**Note:** Venues don't have rooms, so no `room_number` or `available-rooms` endpoint needed.

#### 3.2-3.4 Payment APIs
Same as Hotel (Steps 1.3-1.5)

---

### 4. HOUSE RENT PAYMENTS ✅

#### 4.1 Get Rent Invoices
```http
GET /api/v1/rent/invoices/
```

**Response:**
```json
{
  "count": 5,
  "results": [
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
  ]
}
```

#### 4.2 Get Invoice Details
```http
GET /api/v1/rent/invoices/{invoice_id}/
```

#### 4.3 Create Rent Payment
```http
POST /api/v1/rent/payments/
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
  "created_at": "2026-01-25T10:30:00Z"
}
```

#### 4.4 Initiate Gateway Payment
```http
POST /api/v1/rent/payments/{payment_id}/initiate-gateway/
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

#### 4.5 Verify Payment (Optional)
```http
POST /api/v1/rent/payments/{payment_id}/verify/
```

#### 4.6 Check Payment Status
```http
GET /api/v1/rent/payments/{payment_id}/
```

---

## 🔄 Complete Flows

### Flow 1: Hotel Booking
```
1. GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=...&check_out_date=...
2. POST /api/v1/properties/bookings/create/ (with room_number: "10")
3. POST /api/v1/payments/payments/
4. POST /api/v1/payments/payments/{id}/initiate-gateway/
5. GET /api/v1/payments/payments/{id}/ (poll until completed)
```

### Flow 2: Lodge Booking
```
Same as Hotel, use property_type: "lodge"
```

### Flow 3: Venue Booking
```
1. POST /api/v1/properties/bookings/create/ (with property_type: "venue", event_name, event_type, event_date)
2. POST /api/v1/payments/payments/
3. POST /api/v1/payments/payments/{id}/initiate-gateway/
4. GET /api/v1/payments/payments/{id}/ (poll until completed)
```

### Flow 4: House Rent Payment
```
1. GET /api/v1/rent/invoices/ (or GET /api/v1/rent/invoices/{id}/)
2. POST /api/v1/rent/payments/
3. POST /api/v1/rent/payments/{id}/initiate-gateway/
4. POST /api/v1/rent/payments/{id}/verify/ (optional)
5. GET /api/v1/rent/payments/{id}/ (poll until completed)
```

---

## 📊 API Endpoints Summary

### Booking Endpoints
| Endpoint | Method | Purpose | Property Types |
|----------|--------|---------|----------------|
| `/properties/available-rooms/` | GET | Get available rooms | Hotel, Lodge |
| `/properties/bookings/create/` | POST | Create booking | Hotel, Lodge, Venue |

### Payment Endpoints
| Endpoint | Method | Purpose | Payment Types |
|----------|--------|---------|---------------|
| `/payments/payments/` | POST | Create payment | Booking payments |
| `/payments/payments/{id}/initiate-gateway/` | POST | Initiate payment | Booking payments |
| `/payments/payments/{id}/` | GET | Check status | Booking payments |
| `/rent/payments/` | POST | Create rent payment | Rent payments |
| `/rent/payments/{id}/initiate-gateway/` | POST | Initiate rent payment | Rent payments |
| `/rent/payments/{id}/verify/` | POST | Verify rent payment | Rent payments |
| `/rent/payments/{id}/` | GET | Check rent payment status | Rent payments |

### Supporting Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rent/invoices/` | GET | List rent invoices |
| `/rent/invoices/{id}/` | GET | Get invoice details |
| `/payments/providers/` | GET | List payment providers |

---

## ✅ Final Status

**ALL APIs ARE IMPLEMENTED AND READY FOR MOBILE APP!** 🎉

- ✅ **Hotel Bookings** - Complete REST API with room selection
- ✅ **Lodge Bookings** - Complete REST API with room selection
- ✅ **Venue Bookings** - Complete REST API with event details
- ✅ **House Rent Payments** - Complete REST API with payment gateway

**All endpoints:**
- ✅ Use JWT Bearer token authentication
- ✅ Accept JSON request/response
- ✅ Are documented in Swagger
- ✅ Support AZAM Pay payment gateway
- ✅ Include error handling
- ✅ Return proper status codes

---

## 📚 Documentation Files

- `MOBILE_APP_COMPLETE_BOOKING_FLOW.md` - Complete hotel booking flow
- `ROOM_BOOKING_AND_PAYMENT_FLOW.md` - Room selection and payment guide
- `MOBILE_PAYMENT_INTEGRATION_GUIDE.md` - Payment integration guide
- `MOBILE_APP_PAYMENT_APIS.md` - Payment APIs reference
- `MOBILE_APP_API_STATUS.md` - Implementation status

---

**Ready for Mobile App Integration!** 🚀
