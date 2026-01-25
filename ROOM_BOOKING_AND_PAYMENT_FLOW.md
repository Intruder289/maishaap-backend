# Room Booking & Payment Flow Guide

**For Mobile App Integration - Booking Individual Rooms (e.g., Room 10)**

**Base URL:** `https://portal.maishaapp.co.tz/api/v1/`

**Authentication:** All endpoints require JWT Bearer Token:
```
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Complete Flow: From Room Selection to Payment

### Overview
When a user wants to book a specific room (e.g., Room 10) in a hotel or lodge, follow this flow:

1. **Get Available Rooms** → User sees list of rooms (including Room 10)
2. **Select Room** → User selects Room 10
3. **Create Booking** → Create booking with Room 10 assigned
4. **Create Payment** → Create payment record for the booking
5. **Initiate Payment** → Process payment via AZAM Pay
6. **Verify Payment** → Confirm payment completion

---

## 🔄 Step-by-Step Flow

### Step 1: Get Available Rooms

**Endpoint:** `GET /api/v1/properties/available-rooms/`

**Query Parameters:**
- `property_id` (required) - The hotel/lodge property ID
- `check_in_date` (optional) - Check-in date in `YYYY-MM-DD` format
- `check_out_date` (optional) - Check-out date in `YYYY-MM-DD` format

**Example Request:**
```http
GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=2026-02-01&check_out_date=2026-02-05
Authorization: Bearer <token>
```

**Response:**
```json
{
  "property_id": 123,
  "property_title": "Grand Hotel",
  "property_type": "hotel",
  "total_rooms": 50,
  "available_count": 15,
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "rooms": [
    {
      "id": 45,
      "room_number": "10",
      "room_type": "Deluxe",
      "capacity": 2,
      "base_rate": "50000.00",
      "status": "available",
      "floor_number": 1,
      "bed_type": "Queen",
      "amenities": "WiFi, TV, AC, Mini Bar"
    },
    {
      "id": 46,
      "room_number": "11",
      "room_type": "Standard",
      "capacity": 2,
      "base_rate": "35000.00",
      "status": "available",
      "floor_number": 1,
      "bed_type": "Double",
      "amenities": "WiFi, TV"
    }
  ]
}
```

**Key Fields:**
- `room_number` - The room number (e.g., "10")
- `base_rate` - Price per night for this specific room
- `status` - Must be "available" to book
- `room_type` - Type of room (Deluxe, Standard, etc.)

---

### Step 2: Create Booking with Room Number

**✅ NEW REST API ENDPOINT AVAILABLE!**

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**✅ Features:**
- ✅ Accepts JWT Bearer token authentication
- ✅ Accepts JSON request body
- ✅ Accepts `property_id` and `property_type` directly
- ✅ Accepts `room_number` parameter (e.g., "10")
- ✅ Validates room availability
- ✅ Assigns room to booking
- ✅ Returns booking details with `booking_id`

**Request:**
```http
POST /api/v1/properties/bookings/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_id": 123,
  "property_type": "hotel",  // or "lodge"
  "room_number": "10",       // ← SPECIFIC ROOM NUMBER
  "room_type": "Deluxe",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "total_amount": "200000.00",
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000",
  "special_requests": "Late check-in requested"  // Optional
}
```

**Response (Success - 201 Created):**
```json
{
  "success": true,
  "booking_id": 456,
  "booking_reference": "HTL-000456",
  "room_number": "10",
  "room_type": "Deluxe",
  "message": "Booking HTL-000456 created successfully!",
  "room_message": "Room 10 assigned successfully"
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "success": false,
  "error": "Room 10 is not available (Status: occupied). Please select an available room."
}
```

---

**⚠️ OLD ENDPOINT (Web Forms Only):**

The endpoint `/properties/api/create-booking/` **DOES exist** and **DOES accept `room_number`**, but it's designed for **web forms**, not REST API:

**Current Endpoint:** `POST /properties/api/create-booking/`

**Current Limitations:**
1. Uses Django session authentication (`@login_required`) - not JWT Bearer token
2. Relies on session data to determine property (`request.session.get('selected_hotel_property_id')`)
3. Uses `request.POST` (form data) - may not accept JSON directly
4. Determines property type from HTTP_REFERER header

**What It Does:**
- ✅ Accepts `room_number` parameter (line 6654 in `properties/views.py`)
- ✅ Validates room exists and is available (lines 6777-6802)
- ✅ Assigns room to booking (line 6785)
- ✅ Updates room status to 'occupied' (line 6787)
- ✅ Returns booking details with room assignment confirmation

**For Mobile App Integration, You Have Two Options:**

**Option A: Modify Existing Endpoint** (Recommended)

Modify `/properties/api/create-booking/` to support:
- JWT Bearer token authentication
- JSON request body
- Accept `property_id` directly in request (not from session)
- Accept `property_type` in request (not from HTTP_REFERER)

**Option B: Create New REST API Endpoint**

Create a new endpoint: `POST /api/v1/properties/bookings/create/`

This endpoint should:
- Use DRF `@api_view` decorator
- Accept JWT Bearer token (`@permission_classes([IsAuthenticated])`)
- Accept JSON request body
- Accept `property_id` and `property_type` in request
- Accept `room_number` parameter
- Validate room availability
- Create booking with room assignment

**Example Request (What It Should Accept):**
```http
POST /api/v1/properties/bookings/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_id": 123,
  "property_type": "hotel",  // or "lodge"
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000",
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "room_type": "Deluxe",
  "room_number": "10",  // ← SPECIFIC ROOM NUMBER
  "total_amount": "200000.00",  // base_rate × number of nights
  "special_requests": "Late check-in requested"
}
```

**Option C: Use Existing Endpoint with Modifications** (If you can't create new endpoint)

If you must use the existing endpoint, you'll need to:
1. Send form data (not JSON) - use `application/x-www-form-urlencoded`
2. Set session cookie for authentication (not JWT)
3. Set HTTP_REFERER header to indicate property type
4. Set property in session before calling endpoint

**⚠️ This is NOT recommended for mobile apps** - Option A or B is better.

If there's no REST API endpoint for creating bookings with room numbers, you may need to:

1. **Create a custom API endpoint** that accepts:
   - `property_id`
   - `room_number` (e.g., "10")
   - `check_in_date`
   - `check_out_date`
   - `number_of_guests`
   - Customer details
   - `total_amount`

2. **Backend Logic** (what the endpoint should do):
   ```python
   # Pseudo-code for what the endpoint should do:
   
   # 1. Validate room is available
   room = Room.objects.get(
       property_obj=property_id,
       room_number="10",
       status="available"
   )
   
   # 2. Check for date conflicts
   conflicting_bookings = Booking.objects.filter(
       property_obj=property_id,
       room_number="10",
       booking_status__in=['pending', 'confirmed', 'checked_in'],
       check_in_date__lt=check_out_date,
       check_out_date__gt=check_in_date
   ).exists()
   
   if conflicting_bookings:
       return error("Room 10 is not available for selected dates")
   
   # 3. Create booking
   booking = Booking.objects.create(
       property_obj=property,
       customer=customer,
       room_number="10",  # ← SPECIFIC ROOM
       room_type=room.room_type,
       check_in_date=check_in_date,
       check_out_date=check_out_date,
       number_of_guests=number_of_guests,
       total_amount=total_amount,
       booking_status='pending'
   )
   
   # 4. Assign room to booking
   room.current_booking = booking
   room.status = 'occupied'
   room.save()
   ```

**Expected Response:**
```json
{
  "success": true,
  "booking_id": 456,
  "booking_reference": "HTL-000456",
  "room_number": "10",
  "room_type": "Deluxe",
  "message": "Booking created successfully. Room 10 assigned.",
  "room_message": "Room 10 assigned successfully"
}
```

---

### Step 3: Create Payment Record

**Endpoint:** `POST /api/v1/payments/payments/`

**Request:**
```http
POST /api/v1/payments/payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking": 456,  // ← Booking ID from Step 2
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "notes": "Payment for Room 10 booking HTL-000456"
}
```

**Response:**
```json
{
  "id": 69,
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "booking_reference": "HTL-000456",
  "booking_id": 456,
  "created_at": "2026-01-25T10:30:00Z"
}
```

---

### Step 4: Initiate Gateway Payment

**Endpoint:** `POST /api/v1/payments/payments/{payment_id}/initiate-gateway/`

**Request:**
```http
POST /api/v1/payments/payments/69/initiate-gateway/
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
  "transaction_reference": "BOOKING-HTL-000456-1769145132",
  "gateway_transaction_id": "AZM019be9446ac770a2a65c6243434f61d8",
  "message": "Payment initiated successfully. The customer will receive a payment prompt on their phone.",
  "phone_number_used": "255700000000",
  "booking_reference": "HTL-000456"
}
```

**What Happens:**
- Customer receives payment prompt on their phone
- AZAM Pay processes the payment
- Backend receives webhook notification when payment completes

---

### Step 5: Check Payment Status (Polling)

**Endpoint:** `GET /api/v1/payments/payments/{payment_id}/`

**Request:**
```http
GET /api/v1/payments/payments/69/
Authorization: Bearer <token>
```

**Response (Pending):**
```json
{
  "id": 69,
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "booking_reference": "HTL-000456",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Response (Completed):**
```json
{
  "id": 69,
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "completed",  // ← Payment successful
  "booking_reference": "HTL-000456",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Polling Strategy:**
- Poll every 2-3 seconds after initiating payment
- Stop polling when status changes to `completed` or `failed`
- Maximum polling duration: 2-3 minutes

---

## 📱 Complete Mobile App Flow Example

### TypeScript/JavaScript Implementation

```typescript
interface Room {
  id: number;
  room_number: string;
  room_type: string;
  base_rate: string;
  status: string;
  capacity: number;
}

interface BookingResponse {
  success: boolean;
  booking_id: number;
  booking_reference: string;
  room_number: string;
}

// Step 1: Get Available Rooms
async function getAvailableRooms(
  propertyId: number,
  checkInDate: string,
  checkOutDate: string
): Promise<Room[]> {
  const response = await fetch(
    `/api/v1/properties/available-rooms/?property_id=${propertyId}&check_in_date=${checkInDate}&check_out_date=${checkOutDate}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  const data = await response.json();
  return data.rooms;
}

// Step 2: Create Booking with Room Number
async function createBookingWithRoom(
  propertyId: number,
  roomNumber: string,
  roomType: string,
  checkInDate: string,
  checkOutDate: string,
  numberOfGuests: number,
  totalAmount: string,
  customerDetails: {
    name: string;
    email: string;
    phone: string;
  }
): Promise<BookingResponse> {
  // ✅ Endpoint is now available!
  const response = await fetch('/api/v1/properties/bookings/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      property_id: propertyId,
      room_number: roomNumber,  // ← Room 10
      room_type: roomType,
      check_in_date: checkInDate,
      check_out_date: checkOutDate,
      number_of_guests: numberOfGuests,
      total_amount: totalAmount,
      customer_name: customerDetails.name,
      email: customerDetails.email,
      phone: customerDetails.phone
    })
  });
  return await response.json();
}

// Step 3: Create Payment
async function createPayment(
  bookingId: number,
  amount: string,
  mobileMoneyProvider: string
) {
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
      mobile_money_provider: mobileMoneyProvider
    })
  });
  return await response.json();
}

// Step 4: Initiate Payment
async function initiatePayment(paymentId: number, mobileMoneyProvider: string) {
  const response = await fetch(
    `/api/v1/payments/payments/${paymentId}/initiate-gateway/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        mobile_money_provider: mobileMoneyProvider
      })
    }
  );
  return await response.json();
}

// Step 5: Poll Payment Status
async function pollPaymentStatus(paymentId: number): Promise<boolean> {
  return new Promise((resolve) => {
    const maxAttempts = 60; // 2 minutes (60 × 2 seconds)
    let attempts = 0;
    
    const interval = setInterval(async () => {
      attempts++;
      
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
      } else if (attempts >= maxAttempts) {
        clearInterval(interval);
        resolve(false); // Timeout
      }
    }, 2000); // Poll every 2 seconds
  });
}

// Complete Flow: Book Room 10 and Pay
async function bookRoom10AndPay(
  propertyId: number,
  checkInDate: string,
  checkOutDate: string,
  customerDetails: {
    name: string;
    email: string;
    phone: string;
  },
  mobileMoneyProvider: string = 'AIRTEL'
) {
  try {
    // Step 1: Get available rooms
    console.log('Fetching available rooms...');
    const rooms = await getAvailableRooms(propertyId, checkInDate, checkOutDate);
    
    // Find Room 10
    const room10 = rooms.find(r => r.room_number === '10');
    if (!room10) {
      throw new Error('Room 10 is not available');
    }
    
    if (room10.status !== 'available') {
      throw new Error(`Room 10 is ${room10.status}`);
    }
    
    // Calculate total amount (base_rate × number of nights)
    const checkIn = new Date(checkInDate);
    const checkOut = new Date(checkOutDate);
    const nights = Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24));
    const totalAmount = (parseFloat(room10.base_rate) * nights).toFixed(2);
    
    // Step 2: Create booking with Room 10
    console.log('Creating booking for Room 10...');
    const booking = await createBookingWithRoom(
      propertyId,
      '10',  // ← Room Number
      room10.room_type,
      checkInDate,
      checkOutDate,
      2, // number of guests
      totalAmount,
      customerDetails
    );
    
    console.log('Booking created:', booking.booking_reference);
    
    // Step 3: Create payment
    console.log('Creating payment...');
    const payment = await createPayment(
      booking.booking_id,
      totalAmount,
      mobileMoneyProvider
    );
    
    console.log('Payment created:', payment.id);
    
    // Step 4: Initiate payment
    console.log('Initiating payment...');
    const gatewayResponse = await initiatePayment(payment.id, mobileMoneyProvider);
    
    console.log('Payment initiated:', gatewayResponse.message);
    console.log('Phone number used:', gatewayResponse.phone_number_used);
    console.log('Customer will receive payment prompt on phone');
    
    // Step 5: Poll for payment completion
    console.log('Waiting for payment confirmation...');
    const success = await pollPaymentStatus(payment.id);
    
    if (success) {
      console.log('✅ Payment completed successfully!');
      console.log(`Room 10 booked: ${booking.booking_reference}`);
      return {
        success: true,
        booking: booking,
        payment: payment
      };
    } else {
      console.log('❌ Payment failed or timed out');
      return {
        success: false,
        booking: booking,
        payment: payment
      };
    }
  } catch (error) {
    console.error('Error booking room:', error);
    throw error;
  }
}

// Usage Example
bookRoom10AndPay(
  123,  // property_id
  '2026-02-01',  // check_in_date
  '2026-02-05',  // check_out_date
  {
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+255700000000'
  },
  'AIRTEL'
);
```

---

## 🔑 Important Notes

### Room Selection Requirements

1. **Room Must Be Available:**
   - `status` must be `"available"`
   - No conflicting bookings for the selected dates
   - Room must exist in the property

2. **Room Number Format:**
   - Room numbers are stored as strings (e.g., "10", "101", "A-10")
   - Always use the exact `room_number` from the API response
   - Case-sensitive (if applicable)

3. **Price Calculation:**
   - Use `base_rate` from the room object
   - Calculate: `total_amount = base_rate × number_of_nights`
   - Number of nights = `(check_out_date - check_in_date).days`

### Booking Creation Requirements

**Required Fields:**
- `property_id` - Property ID
- `room_number` - Specific room number (e.g., "10")
- `room_type` - Room type from room object
- `check_in_date` - Format: `YYYY-MM-DD`
- `check_out_date` - Format: `YYYY-MM-DD`
- `number_of_guests` - Number of guests
- `total_amount` - Calculated total (base_rate × nights)
- Customer details (name, email, phone)

### Payment Flow

1. **Create Payment Record** - Links payment to booking
2. **Initiate Gateway Payment** - Sends payment request to AZAM Pay
3. **Customer Receives Prompt** - Payment prompt on phone
4. **Webhook Updates Status** - Backend receives notification
5. **Poll for Status** - Mobile app checks payment status

---

## ⚠️ Current Status & Recommendations

### ✅ What Exists

**Endpoint:** `POST /properties/api/create-booking/`
- ✅ **Accepts `room_number`** parameter
- ✅ **Validates room availability**
- ✅ **Assigns room to booking**
- ✅ **Returns booking details**

### ❌ What's Missing for Mobile Apps

**Current Limitations:**
1. **Authentication:** Uses Django session (`@login_required`) instead of JWT
2. **Request Format:** Uses `request.POST` (form data) instead of JSON
3. **Property Selection:** Relies on session data instead of direct `property_id` parameter
4. **Property Type:** Determines from HTTP_REFERER instead of request parameter

### 🔧 Recommended Solution

**Create a new REST API endpoint** specifically for mobile apps:

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**Implementation Requirements:**
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # JWT Bearer token
def create_booking_api(request):
    """
    REST API endpoint for creating bookings with room numbers.
    Designed for mobile apps - accepts JSON and JWT auth.
    """
    # Accept JSON request body
    property_id = request.data.get('property_id')
    property_type = request.data.get('property_type')  # 'hotel' or 'lodge'
    room_number = request.data.get('room_number')  # e.g., "10"
    # ... rest of the logic from api_create_booking
```

**This endpoint should:**
- ✅ Accept JWT Bearer token authentication
- ✅ Accept JSON request body
- ✅ Accept `property_id` directly (not from session)
- ✅ Accept `property_type` directly (not from HTTP_REFERER)
- ✅ Accept `room_number` parameter
- ✅ Validate room availability
- ✅ Create booking with room assignment
- ✅ Return booking details with `booking_id`

---

## 📚 Related Endpoints

### Get Booking Details
```http
GET /api/v1/properties/bookings/{booking_id}/details/
```

### Update Booking Status
```http
POST /api/v1/properties/bookings/{booking_id}/status-update/
```

### List All Payments for Booking
```http
GET /api/v1/payments/payments/?booking={booking_id}
```

---

## ✅ Summary

**Complete Flow for Booking Room 10:**

1. ✅ **Get Available Rooms** → `GET /api/v1/properties/available-rooms/`
2. ✅ **Create Booking** → `POST /api/v1/properties/bookings/create/` (REST API, JWT auth) **✅ NEW!**
3. ✅ **Create Payment** → `POST /api/v1/payments/payments/`
4. ✅ **Initiate Payment** → `POST /api/v1/payments/payments/{id}/initiate-gateway/`
5. ✅ **Poll Status** → `GET /api/v1/payments/payments/{id}/`

**✅ Status:**
- ✅ **REST API endpoint created:** `POST /api/v1/properties/bookings/create/`
- ✅ **JWT Bearer token authentication** supported
- ✅ **JSON request body** supported
- ✅ **Room number validation** implemented
- ✅ **Room assignment** implemented
- ✅ **Swagger documentation** included

**Ready for Mobile App Integration!** 🎉

---

**Need Help?** Check Swagger documentation at `/swagger/` or refer to `MOBILE_PAYMENT_INTEGRATION_GUIDE.md` for payment flow details.
