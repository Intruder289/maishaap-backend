# Complete Mobile App Integration Guide

**Step-by-Step API Integration for Hotel, Lodge, Venue Bookings & House Rent Payments**

**Base URL:** `https://portal.maishaapp.co.tz/api/v1/`

---

## 📋 Table of Contents

1. [Authentication](#1-authentication)
2. [Properties APIs](#2-properties-apis)
3. [Hotel Booking Flow](#3-hotel-booking-flow)
4. [Lodge Booking Flow](#4-lodge-booking-flow)
5. [Venue Booking Flow](#5-venue-booking-flow)
6. [House Rent Payment Flow](#6-house-rent-payment-flow)
7. [Error Handling](#7-error-handling)
8. [Quick Reference](#8-quick-reference)

---

## 1. Authentication

### 1.1 Login (Get JWT Token)

**Endpoint:** `POST /api/v1/auth/login/`

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com"
  }
}
```

**Mobile App Code (JavaScript/TypeScript):**
```typescript
async function login(username: string, password: string) {
  const response = await fetch('https://portal.maishaapp.co.tz/api/v1/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  const data = await response.json();
  // Store tokens securely
  await SecureStore.setItemAsync('access_token', data.access);
  await SecureStore.setItemAsync('refresh_token', data.refresh);
  
  return data;
}
```

### 1.2 Using JWT Token

**All authenticated endpoints require:**
```
Authorization: Bearer <access_token>
```

**Helper Function:**
```typescript
async function getAuthHeaders() {
  const token = await SecureStore.getItemAsync('access_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
}
```

---

## 2. Properties APIs

### 2.1 List All Properties

**Endpoint:** `GET /api/v1/properties/`

**Query Parameters:**
- `category` - Filter by type: `hotel`, `lodge`, `venue`, `house`
- `region` - Filter by region ID
- `status` - Filter by status: `available`, `rented`, `under_maintenance`
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

**Example - Get All Hotels:**
```http
GET /api/v1/properties/?category=hotel&page=1&page_size=20
```

**Example - Get All Houses:**
```http
GET /api/v1/properties/?category=house&status=available
```

**Response:**
```json
{
  "count": 50,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "results": [
    {
      "id": 123,
      "title": "Grand Hotel",
      "description": "Luxury hotel in city center",
      "property_type": {
        "id": 2,
        "name": "hotel"
      },
      "address": "123 Main Street",
      "rent_amount": "200000.00",
      "images": [
        {
          "id": 1,
          "image": "https://portal.maishaapp.co.tz/media/properties/image1.jpg",
          "is_primary": true
        }
      ],
      "amenities": ["WiFi", "Parking", "Pool"],
      "status": "available"
    }
  ]
}
```

**Mobile App Code:**
```typescript
async function getProperties(category?: string, page: number = 1) {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: '20',
  });
  
  if (category) {
    params.append('category', category);
  }
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/?${params}`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### 2.2 Search Properties

**Endpoint:** `GET /api/v1/properties/search/`

**Query Parameters:**
- `search` - Search query (title, description, address)
- `category` - Filter by type: `hotel`, `lodge`, `venue`, `house`
- `region` - Filter by region ID
- `min_rent` - Minimum rent amount
- `max_rent` - Maximum rent amount
- `page` - Page number
- `page_size` - Items per page

**Example:**
```http
GET /api/v1/properties/search/?search=beach&category=hotel&min_rent=100000&max_rent=500000
```

**Mobile App Code:**
```typescript
async function searchProperties(query: string, filters: any) {
  const params = new URLSearchParams({
    search: query,
    page: '1',
    page_size: '20',
  });
  
  if (filters.category) params.append('category', filters.category);
  if (filters.min_rent) params.append('min_rent', filters.min_rent.toString());
  if (filters.max_rent) params.append('max_rent', filters.max_rent.toString());
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/search/?${params}`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### 2.3 Get Property Details

**Endpoint:** `GET /api/v1/properties/{property_id}/`

**Example:**
```http
GET /api/v1/properties/123/
```

**Response:**
```json
{
  "id": 123,
  "title": "Grand Hotel",
  "description": "Luxury hotel in city center",
  "property_type": {
    "id": 2,
  "name": "hotel"
  },
  "address": "123 Main Street",
  "latitude": "-6.7924",
  "longitude": "39.2083",
  "bedrooms": 50,
  "bathrooms": 50,
  "rent_amount": "200000.00",
  "capacity": 100,
  "images": [
    {
      "id": 1,
      "image": "https://portal.maishaapp.co.tz/media/properties/image1.jpg",
      "is_primary": true
    }
  ],
  "amenities": ["WiFi", "Parking", "Pool"],
  "status": "available",
  "available_rooms": 25
}
```

**Mobile App Code:**
```typescript
async function getPropertyDetails(propertyId: number) {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/${propertyId}/`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  if (!response.ok) {
    throw new Error('Property not found');
  }
  
  return await response.json();
}
```

---

## 3. Hotel Booking Flow

**Complete flow from property selection to payment completion.**

### Step 1: Get Available Rooms

**Endpoint:** `GET /api/v1/properties/available-rooms/`

**Query Parameters:**
- `property_id` - Hotel property ID (required)
- `check_in_date` - Check-in date: `YYYY-MM-DD` (required)
- `check_out_date` - Check-out date: `YYYY-MM-DD` (required)

**Example:**
```http
GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=2026-02-01&check_out_date=2026-02-05
```

**Response:**
```json
{
  "property_id": 123,
  "property_name": "Grand Hotel",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "available_rooms": [
    {
      "id": 10,
      "room_number": "101",
      "room_type": "Deluxe",
      "price_per_night": "50000.00",
      "capacity": 2,
      "amenities": ["WiFi", "TV", "AC"]
    },
    {
      "id": 11,
      "room_number": "102",
      "room_type": "Standard",
      "price_per_night": "30000.00",
      "capacity": 2,
      "amenities": ["WiFi", "TV"]
    }
  ]
}
```

**Mobile App Code:**
```typescript
async function getAvailableRooms(propertyId: number, checkIn: string, checkOut: string) {
  const params = new URLSearchParams({
    property_id: propertyId.toString(),
    check_in_date: checkIn,
    check_out_date: checkOut,
  });
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/available-rooms/?${params}`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### Step 2: Create Booking

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**Request Body:**
```json
{
  "property_id": 123,
  "property_type": "hotel",
  "room_number": "101",
  "room_type": "Deluxe",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "total_amount": "200000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000",
  "special_requests": "Late check-in preferred"
}
```

**Response:**
```json
{
  "success": true,
  "booking_id": 456,
  "booking_reference": "HTL-000456",
  "room_number": "101",
  "room_type": "Deluxe",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "total_amount": "200000.00",
  "message": "Booking HTL-000456 created successfully!"
}
```

**Mobile App Code:**
```typescript
async function createHotelBooking(bookingData: {
  propertyId: number;
  roomNumber: string;
  roomType: string;
  checkIn: string;
  checkOut: string;
  numberOfGuests: number;
  totalAmount: string;
  customerName: string;
  email: string;
  phone: string;
  specialRequests?: string;
}) {
  const response = await fetch(
    'https://portal.maishaapp.co.tz/api/v1/properties/bookings/create/',
    {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        property_id: bookingData.propertyId,
        property_type: 'hotel',
        room_number: bookingData.roomNumber,
        room_type: bookingData.roomType,
        check_in_date: bookingData.checkIn,
        check_out_date: bookingData.checkOut,
        number_of_guests: bookingData.numberOfGuests,
        total_amount: bookingData.totalAmount,
        customer_name: bookingData.customerName,
        email: bookingData.email,
        phone: bookingData.phone,
        special_requests: bookingData.specialRequests || '',
      }),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Booking creation failed');
  }
  
  return await response.json();
}
```

### Step 3: Create Payment

**Endpoint:** `POST /api/v1/payments/payments/`

**Request Body:**
```json
{
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"
}
```

**Response:**
```json
{
  "id": 80,
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Mobile App Code:**
```typescript
async function createPayment(bookingId: number, amount: string, provider: string) {
  const response = await fetch(
    'https://portal.maishaapp.co.tz/api/v1/payments/payments/',
    {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        booking: bookingId,
        amount: amount,
        payment_method: 'mobile_money',
        mobile_money_provider: provider, // AIRTEL, TIGO, MPESA, HALOPESA
      }),
    }
  );
  
  return await response.json();
}
```

### Step 4: Initiate Payment Gateway

**Endpoint:** `POST /api/v1/payments/payments/{payment_id}/initiate-gateway/`

**Request Body (Optional):**
```json
{
  "mobile_money_provider": "AIRTEL"
}
```

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "transaction_id": 20,
  "transaction_reference": "HTL-80-1769145132",
  "phone_number_used": "+255700000000",
  "message": "Payment initiated successfully. The customer will receive a payment prompt on their phone."
}
```

**Mobile App Code:**
```typescript
async function initiatePayment(paymentId: number, provider?: string) {
  const body: any = {};
  if (provider) {
    body.mobile_money_provider = provider;
  }
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/payments/payments/${paymentId}/initiate-gateway/`,
    {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify(body),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Payment initiation failed');
  }
  
  return await response.json();
}
```

### Step 5: Check Payment Status (Polling)

**Endpoint:** `GET /api/v1/payments/payments/{payment_id}/`

**Response:**
```json
{
  "id": 80,
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "completed",  // pending, completed, failed, cancelled
  "created_at": "2026-01-25T10:30:00Z",
  "updated_at": "2026-01-25T10:35:00Z"
}
```

**Mobile App Code (Polling):**
```typescript
async function checkPaymentStatus(paymentId: number): Promise<string> {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/payments/payments/${paymentId}/`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  const payment = await response.json();
  return payment.status; // pending, completed, failed, cancelled
}

// Poll payment status every 2-3 seconds
async function pollPaymentStatus(paymentId: number, onComplete: () => void) {
  const maxAttempts = 60; // 2-3 minutes max
  let attempts = 0;
  
  const interval = setInterval(async () => {
    attempts++;
    
    try {
      const status = await checkPaymentStatus(paymentId);
      
      if (status === 'completed') {
        clearInterval(interval);
        onComplete();
      } else if (status === 'failed' || status === 'cancelled') {
        clearInterval(interval);
        throw new Error(`Payment ${status}`);
      } else if (attempts >= maxAttempts) {
        clearInterval(interval);
        throw new Error('Payment timeout');
      }
    } catch (error) {
      clearInterval(interval);
      throw error;
    }
  }, 2000); // Check every 2 seconds
}
```

### Complete Hotel Booking Flow Example

```typescript
async function completeHotelBookingFlow(
  propertyId: number,
  roomNumber: string,
  checkIn: string,
  checkOut: string,
  customerData: any,
  paymentProvider: string
) {
  try {
    // Step 1: Get available rooms
    const rooms = await getAvailableRooms(propertyId, checkIn, checkOut);
    
    // Step 2: Create booking
    const booking = await createHotelBooking({
      propertyId,
      roomNumber,
      roomType: rooms.available_rooms.find(r => r.room_number === roomNumber)?.room_type || '',
      checkIn,
      checkOut,
      numberOfGuests: customerData.numberOfGuests,
      totalAmount: customerData.totalAmount,
      customerName: customerData.name,
      email: customerData.email,
      phone: customerData.phone,
    });
    
    // Step 3: Create payment
    const payment = await createPayment(booking.booking_id, booking.total_amount, paymentProvider);
    
    // Step 4: Initiate payment gateway
    const gatewayResult = await initiatePayment(payment.id, paymentProvider);
    
    // Step 5: Poll payment status
    await pollPaymentStatus(payment.id, () => {
      console.log('Payment completed!');
    });
    
    return { success: true, booking, payment };
  } catch (error) {
    console.error('Booking failed:', error);
    throw error;
  }
}
```

---

## 4. Lodge Booking Flow

**Same as Hotel Booking Flow, but use `property_type: "lodge"`**

### Step 1: Get Available Rooms
```http
GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=2026-02-01&check_out_date=2026-02-05
```
*(Same as hotel)*

### Step 2: Create Booking
```json
{
  "property_id": 123,
  "property_type": "lodge",  // ← Use "lodge" instead of "hotel"
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

### Steps 3-5: Payment Flow
*(Same as hotel - Steps 3-5)*

---

## 5. Venue Booking Flow

**Venues don't have rooms, so skip Step 1 (Get Available Rooms)**

### Step 1: Create Venue Booking

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**Request Body:**
```json
{
  "property_id": 123,
  "property_type": "venue",
  "event_name": "Wedding Reception",
  "event_type": "Wedding",
  "event_date": "2026-02-15",
  "check_out_date": "2026-02-15",
  "expected_guests": 200,
  "total_amount": "500000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000",
  "special_requests": "Need sound system and catering"
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
  "total_amount": "500000.00",
  "message": "Booking VEN-000789 created successfully!"
}
```

**Mobile App Code:**
```typescript
async function createVenueBooking(bookingData: {
  propertyId: number;
  eventName: string;
  eventType: string;
  eventDate: string;
  expectedGuests: number;
  totalAmount: string;
  customerName: string;
  email: string;
  phone: string;
  specialRequests?: string;
}) {
  const response = await fetch(
    'https://portal.maishaapp.co.tz/api/v1/properties/bookings/create/',
    {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        property_id: bookingData.propertyId,
        property_type: 'venue',
        event_name: bookingData.eventName,
        event_type: bookingData.eventType,
        event_date: bookingData.eventDate,
        check_out_date: bookingData.eventDate, // Same as event_date
        expected_guests: bookingData.expectedGuests,
        total_amount: bookingData.totalAmount,
        customer_name: bookingData.customerName,
        email: bookingData.email,
        phone: bookingData.phone,
        special_requests: bookingData.specialRequests || '',
      }),
    }
  );
  
  return await response.json();
}
```

### Steps 2-4: Payment Flow
*(Same as hotel - Steps 3-5, but use venue booking ID)*

---

## 6. House Rent Payment Flow

**House rent uses invoices, not bookings**

### Step 1: Get Rent Invoices

**Endpoint:** `GET /api/v1/rent/invoices/`

**Query Parameters:**
- `status` - Filter by status: `pending`, `paid`, `overdue`
- `page` - Page number
- `page_size` - Items per page

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

**Mobile App Code:**
```typescript
async function getRentInvoices(status?: string) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/rent/invoices/?${params}`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### Step 2: Get Invoice Details

**Endpoint:** `GET /api/v1/rent/invoices/{invoice_id}/`

**Example:**
```http
GET /api/v1/rent/invoices/45/
```

**Mobile App Code:**
```typescript
async function getInvoiceDetails(invoiceId: number) {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/rent/invoices/${invoiceId}/`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### Step 3: Create Rent Payment

**Endpoint:** `POST /api/v1/rent/payments/`

**Request Body:**
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
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Mobile App Code:**
```typescript
async function createRentPayment(invoiceId: number, amount: string, provider: string) {
  const response = await fetch(
    'https://portal.maishaapp.co.tz/api/v1/rent/payments/',
    {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({
        rent_invoice: invoiceId,
        amount: amount,
        payment_method: 'mobile_money',
        mobile_money_provider: provider,
        reference_number: `REF-${Date.now()}`,
      }),
    }
  );
  
  return await response.json();
}
```

### Step 4: Initiate Gateway Payment

**Endpoint:** `POST /api/v1/rent/payments/{payment_id}/initiate-gateway/`

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

**Mobile App Code:**
```typescript
async function initiateRentPayment(paymentId: number) {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/rent/payments/${paymentId}/initiate-gateway/`,
    {
      method: 'POST',
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### Step 5: Verify Payment (Optional)

**Endpoint:** `POST /api/v1/rent/payments/{payment_id}/verify/`

**Mobile App Code:**
```typescript
async function verifyRentPayment(paymentId: number) {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/rent/payments/${paymentId}/verify/`,
    {
      method: 'POST',
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

### Step 6: Check Payment Status

**Endpoint:** `GET /api/v1/rent/payments/{payment_id}/`

**Mobile App Code:**
```typescript
async function checkRentPaymentStatus(paymentId: number) {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/rent/payments/${paymentId}/`,
    {
      headers: await getAuthHeaders(),
    }
  );
  
  return await response.json();
}
```

---

## 7. Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "error": "Validation error message",
  "details": {}
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Server Error:**
```json
{
  "error": "Internal server error"
}
```

### Error Handling Helper

```typescript
async function handleApiError(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.error || error.detail || 'API request failed');
  }
  return response;
}

// Usage:
try {
  const response = await fetch(url, options);
  await handleApiError(response);
  return await response.json();
} catch (error) {
  console.error('API Error:', error);
  // Show error to user
  throw error;
}
```

---

## 8. Quick Reference

### API Endpoints Summary

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|----------------|
| `/auth/login/` | POST | Login | No |
| `/properties/` | GET | List properties | No |
| `/properties/search/` | GET | Search properties | No |
| `/properties/{id}/` | GET | Property details | No |
| `/properties/available-rooms/` | GET | Get available rooms | Yes |
| `/properties/bookings/create/` | POST | Create booking | Yes |
| `/payments/payments/` | POST | Create payment | Yes |
| `/payments/payments/{id}/initiate-gateway/` | POST | Initiate payment | Yes |
| `/payments/payments/{id}/` | GET | Check payment status | Yes |
| `/rent/invoices/` | GET | List rent invoices | Yes |
| `/rent/invoices/{id}/` | GET | Get invoice details | Yes |
| `/rent/payments/` | POST | Create rent payment | Yes |
| `/rent/payments/{id}/initiate-gateway/` | POST | Initiate rent payment | Yes |
| `/rent/payments/{id}/verify/` | POST | Verify rent payment | Yes |
| `/rent/payments/{id}/` | GET | Check rent payment status | Yes |

### Payment Providers

- `AIRTEL` - Airtel Money
- `TIGO` - Tigo Pesa
- `MPESA` - M-Pesa (Vodacom)
- `HALOPESA` - HaloPesa

### Payment Statuses

- `pending` - Payment initiated, waiting for completion
- `completed` - Payment successful
- `failed` - Payment failed
- `cancelled` - Payment cancelled

### Property Categories

- `hotel` - Hotel properties
- `lodge` - Lodge properties
- `venue` - Event venues
- `house` - Residential houses

---

## ✅ Complete Integration Checklist

- [ ] Authentication implemented (login, token storage)
- [ ] Properties listing implemented
- [ ] Property search implemented
- [ ] Property details implemented
- [ ] Hotel booking flow implemented
- [ ] Lodge booking flow implemented
- [ ] Venue booking flow implemented
- [ ] House rent payment flow implemented
- [ ] Payment status polling implemented
- [ ] Error handling implemented
- [ ] Loading states implemented
- [ ] Success/error messages implemented

---

**Ready for Mobile App Integration!** 🚀

For questions or support, refer to:
- `MOBILE_APP_SMART_PHONE_LOGIC.md` - Smart phone logic explanation
- `PHONE_NUMBER_SOURCES_EXPLAINED.md` - Phone number sources
- `COMPLETE_MOBILE_API_SUMMARY.md` - Complete API summary
