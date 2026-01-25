# Complete Mobile App Booking Flow

**From Hotel Selection to Payment Completion**

This document explains the complete API flow for a mobile app user booking a hotel room and making payment.

---

## 📱 User Journey

1. **Browse Hotels** → User sees list of hotels
2. **Select Hotel** → User selects a specific hotel
3. **View Available Rooms** → User sees available rooms with prices
4. **Select Room** → User selects Room 10
5. **Enter Booking Details** → User enters dates, guests, customer info
6. **Create Booking** → Booking created with Room 10 assigned
7. **Create Payment** → Payment record created
8. **Initiate Payment** → Payment prompt sent to user's phone
9. **Complete Payment** → User approves payment on phone
10. **Confirm Booking** → Booking confirmed, receipt shown

---

## 🔄 Complete API Flow

### Step 1: Browse Hotels (Optional - if you need hotel list)

**Endpoint:** `GET /api/v1/properties/`

**Query Parameters:**
- `property_type=hotel` - Filter hotels only
- `region` - Filter by region (optional)
- `search` - Search by name (optional)

**Request:**
```http
GET /api/v1/properties/?property_type=hotel&region=1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 123,
      "title": "Grand Hotel",
      "property_type": {"name": "Hotel"},
      "region": {"name": "Dar es Salaam"},
      "address": "123 Main Street",
      "rent_amount": null,
      "primary_image": {...}
    }
  ]
}
```

---

### Step 2: Get Hotel Details (Optional - if you need full details)

**Endpoint:** `GET /api/v1/properties/{property_id}/`

**Request:**
```http
GET /api/v1/properties/123/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 123,
  "title": "Grand Hotel",
  "description": "Luxury hotel in the heart of the city",
  "address": "123 Main Street, Dar es Salaam",
  "property_type": {"name": "Hotel"},
  "images": [...],
  "amenities": [...]
}
```

---

### Step 3: Get Available Rooms ⭐ **CRITICAL STEP**

**Endpoint:** `GET /api/v1/properties/available-rooms/`

**Query Parameters:**
- `property_id` (required) - Hotel ID
- `check_in_date` (optional) - Check-in date (YYYY-MM-DD)
- `check_out_date` (optional) - Check-out date (YYYY-MM-DD)

**Request:**
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

**What Mobile App Should Do:**
- Display list of available rooms
- Show room number, type, price (`base_rate`), capacity
- Allow user to select a room (e.g., Room 10)
- Calculate total amount: `base_rate × number_of_nights`

---

### Step 4: Create Booking with Selected Room ⭐ **CRITICAL STEP**

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**Request:**
```http
POST /api/v1/properties/bookings/create/
Authorization: Bearer <token>
Content-Type: application/json

{
  "property_id": 123,
  "property_type": "hotel",
  "room_number": "10",              // ← Selected room from Step 3
  "room_type": "Deluxe",            // ← From room object
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "number_of_guests": 2,
  "total_amount": "200000.00",      // ← base_rate × 4 nights
  "customer_name": "John Doe",
  "email": "john@example.com",
  "phone": "+255700000000",
  "special_requests": "Late check-in requested"
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

**Response (Error - Room Not Available):**
```json
{
  "success": false,
  "error": "Room 10 is not available (Status: occupied). Please select an available room."
}
```

**What Mobile App Should Do:**
- Show loading spinner
- Display success message with booking reference
- Store `booking_id` for payment step
- If error, show error message and allow user to select another room

---

### Step 5: Create Payment Record ⭐ **CRITICAL STEP**

**Endpoint:** `POST /api/v1/payments/payments/`

**Request:**
```http
POST /api/v1/payments/payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "booking": 456,                   // ← booking_id from Step 4
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

**What Mobile App Should Do:**
- Store `payment_id` (69) for next step
- Show "Preparing payment..." message

---

### Step 6: Initiate Gateway Payment ⭐ **CRITICAL STEP**

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

**What Mobile App Should Do:**
- Show "Payment prompt sent to your phone" message
- Display phone number used: `255700000000`
- Show "Please approve payment on your phone" instruction
- Start polling payment status (Step 7)

---

### Step 7: Poll Payment Status ⭐ **CRITICAL STEP**

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
  "status": "completed",           // ← Payment successful!
  "booking_reference": "HTL-000456",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**Response (Failed):**
```json
{
  "id": 69,
  "booking": 456,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "failed",              // ← Payment failed
  "booking_reference": "HTL-000456",
  "created_at": "2026-01-25T10:30:00Z"
}
```

**What Mobile App Should Do:**
- Poll every 2-3 seconds after initiating payment
- Show loading spinner with "Waiting for payment confirmation..."
- When `status === "completed"`:
  - Show success message
  - Display booking confirmation
  - Show receipt/download option
- When `status === "failed"`:
  - Show error message
  - Allow user to retry payment
- Stop polling after 2-3 minutes (timeout)

---

## 📱 Complete Mobile App Implementation Example

### TypeScript/JavaScript Flow

```typescript
// Complete flow: Hotel Selection → Room Selection → Booking → Payment

interface Hotel {
  id: number;
  title: string;
  address: string;
}

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

interface PaymentResponse {
  id: number;
  booking: number;
  amount: string;
  status: string;
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

// Step 2: Create Booking
async function createBooking(
  propertyId: number,
  propertyType: string,
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
  },
  specialRequests?: string
): Promise<BookingResponse> {
  const response = await fetch('/api/v1/properties/bookings/create/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      property_id: propertyId,
      property_type: propertyType,
      room_number: roomNumber,
      room_type: roomType,
      check_in_date: checkInDate,
      check_out_date: checkOutDate,
      number_of_guests: numberOfGuests,
      total_amount: totalAmount,
      customer_name: customerDetails.name,
      email: customerDetails.email,
      phone: customerDetails.phone,
      special_requests: specialRequests || ''
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create booking');
  }
  
  return await response.json();
}

// Step 3: Create Payment
async function createPayment(
  bookingId: number,
  amount: string,
  mobileMoneyProvider: string
): Promise<PaymentResponse> {
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
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create payment');
  }
  
  return await response.json();
}

// Step 4: Initiate Payment
async function initiatePayment(
  paymentId: number,
  mobileMoneyProvider: string
) {
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
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to initiate payment');
  }
  
  return await response.json();
}

// Step 5: Poll Payment Status
async function pollPaymentStatus(paymentId: number): Promise<boolean> {
  return new Promise((resolve, reject) => {
    const maxAttempts = 60; // 2 minutes (60 × 2 seconds)
    let attempts = 0;
    
    const interval = setInterval(async () => {
      attempts++;
      
      try {
        const response = await fetch(
          `/api/v1/payments/payments/${paymentId}/`,
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );
        
        if (!response.ok) {
          clearInterval(interval);
          reject(new Error('Failed to check payment status'));
          return;
        }
        
        const payment = await response.json();
        
        if (payment.status === 'completed') {
          clearInterval(interval);
          resolve(true);
        } else if (payment.status === 'failed') {
          clearInterval(interval);
          resolve(false);
        } else if (attempts >= maxAttempts) {
          clearInterval(interval);
          reject(new Error('Payment timeout - please check manually'));
        }
      } catch (error) {
        clearInterval(interval);
        reject(error);
      }
    }, 2000); // Poll every 2 seconds
  });
}

// Complete Flow Function
async function completeBookingFlow(
  hotelId: number,
  checkInDate: string,
  checkOutDate: string,
  selectedRoomNumber: string,
  numberOfGuests: number,
  customerDetails: {
    name: string;
    email: string;
    phone: string;
  },
  mobileMoneyProvider: string = 'AIRTEL'
) {
  try {
    // Step 1: Get available rooms
    console.log('📋 Fetching available rooms...');
    const rooms = await getAvailableRooms(hotelId, checkInDate, checkOutDate);
    
    // Find selected room
    const selectedRoom = rooms.find(r => r.room_number === selectedRoomNumber);
    if (!selectedRoom) {
      throw new Error(`Room ${selectedRoomNumber} not found in available rooms`);
    }
    
    if (selectedRoom.status !== 'available') {
      throw new Error(`Room ${selectedRoomNumber} is ${selectedRoom.status}`);
    }
    
    // Calculate total amount
    const checkIn = new Date(checkInDate);
    const checkOut = new Date(checkOutDate);
    const nights = Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24));
    const totalAmount = (parseFloat(selectedRoom.base_rate) * nights).toFixed(2);
    
    console.log(`💰 Total amount: ${totalAmount} TZS (${nights} nights × ${selectedRoom.base_rate} TZS/night)`);
    
    // Step 2: Create booking
    console.log(`🏨 Creating booking for Room ${selectedRoomNumber}...`);
    const booking = await createBooking(
      hotelId,
      'hotel',  // or 'lodge'
      selectedRoomNumber,
      selectedRoom.room_type,
      checkInDate,
      checkOutDate,
      numberOfGuests,
      totalAmount,
      customerDetails
    );
    
    console.log(`✅ Booking created: ${booking.booking_reference}`);
    console.log(`   Booking ID: ${booking.booking_id}`);
    console.log(`   Room: ${booking.room_number}`);
    
    // Step 3: Create payment
    console.log('💳 Creating payment record...');
    const payment = await createPayment(
      booking.booking_id,
      totalAmount,
      mobileMoneyProvider
    );
    
    console.log(`✅ Payment created: Payment ID ${payment.id}`);
    
    // Step 4: Initiate payment
    console.log('📱 Initiating payment...');
    const gatewayResponse = await initiatePayment(payment.id, mobileMoneyProvider);
    
    console.log(`✅ Payment initiated`);
    console.log(`   Transaction ID: ${gatewayResponse.transaction_id}`);
    console.log(`   Phone: ${gatewayResponse.phone_number_used}`);
    console.log(`   Message: ${gatewayResponse.message}`);
    
    // Step 5: Poll for payment completion
    console.log('⏳ Waiting for payment confirmation...');
    console.log('   Please approve payment on your phone');
    
    const success = await pollPaymentStatus(payment.id);
    
    if (success) {
      console.log('🎉 Payment completed successfully!');
      console.log(`✅ Booking confirmed: ${booking.booking_reference}`);
      return {
        success: true,
        booking: booking,
        payment: payment,
        message: 'Booking and payment completed successfully!'
      };
    } else {
      console.log('❌ Payment failed');
      return {
        success: false,
        booking: booking,
        payment: payment,
        message: 'Payment failed. Please try again.'
      };
    }
  } catch (error) {
    console.error('❌ Error in booking flow:', error);
    throw error;
  }
}

// Usage Example
completeBookingFlow(
  123,  // hotel_id
  '2026-02-01',  // check_in_date
  '2026-02-05',  // check_out_date
  '10',  // selected_room_number
  2,  // number_of_guests
  {
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+255700000000'
  },
  'AIRTEL'  // mobile_money_provider
);
```

---

## 🎯 Quick Reference: API Endpoints Summary

| Step | Endpoint | Method | Purpose |
|------|----------|--------|---------|
| 1 | `/api/v1/properties/` | GET | List hotels (optional) |
| 2 | `/api/v1/properties/{id}/` | GET | Get hotel details (optional) |
| 3 | `/api/v1/properties/available-rooms/` | GET | **Get available rooms** ⭐ |
| 4 | `/api/v1/properties/bookings/create/` | POST | **Create booking with room** ⭐ |
| 5 | `/api/v1/payments/payments/` | POST | **Create payment record** ⭐ |
| 6 | `/api/v1/payments/payments/{id}/initiate-gateway/` | POST | **Initiate payment** ⭐ |
| 7 | `/api/v1/payments/payments/{id}/` | GET | **Check payment status** ⭐ |

---

## ✅ Complete Flow Summary

**User Journey:**
1. User selects hotel → **Get available rooms** (Step 3)
2. User selects Room 10 → **Create booking** (Step 4)
3. User confirms booking → **Create payment** (Step 5)
4. User initiates payment → **Initiate gateway payment** (Step 6)
5. User approves on phone → **Poll status** (Step 7)
6. Payment confirmed → **Show success** ✅

**All APIs are ready and working!** 🎉

---

## 🔑 Important Notes

### Room Selection
- Always call **Step 3** (Get Available Rooms) before booking
- Use `base_rate` from room object to calculate total
- Validate `status === "available"` before allowing selection
- Room numbers are strings (e.g., "10", "101", "A-10")

### Booking Creation
- `room_number` is **mandatory** for hotel/lodge bookings
- `property_type` must be exactly `"hotel"` or `"lodge"`
- Total amount = `base_rate × number_of_nights`
- Booking is created with `status: "pending"` until payment

### Payment Flow
- Payment status changes: `pending` → `completed` (or `failed`)
- Poll every 2-3 seconds, max 2-3 minutes
- Phone number is automatically selected based on user role
- Webhook updates payment status automatically

---

**Need Help?** Check Swagger documentation at `/swagger/` for detailed API schemas.
