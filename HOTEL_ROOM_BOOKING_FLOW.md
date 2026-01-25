# Hotel Room Booking Flow - Mobile App Guide

**Complete Step-by-Step Flow: Select Hotel → Select Room → Book → Pay**

**Base URL:** `https://portal.maishaapp.co.tz/api/v1/`

**Authentication:** All endpoints require JWT Bearer Token:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔄 Complete Hotel Room Booking Flow

```
1. List/Search Hotels → 2. Select Hotel → 3. Get Available Rooms → 4. Select Room → 5. Create Booking → 6. Pay → 7. Done!
```

---

## Step 1: List/Search Hotels

**Get all available hotels or search for specific hotels.**

### Option A: List All Hotels

**Endpoint:** `GET /api/v1/properties/`

**Query Parameters:**
- `category=hotel` - Filter to show only hotels
- `status=available` - Show only available hotels
- `page=1` - Page number
- `page_size=20` - Items per page

**Example:**
```http
GET /api/v1/properties/?category=hotel&status=available&page=1&page_size=20
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
      "address": "123 Main Street",
      "rent_amount": "200000.00",
      "images": [
        {
          "id": 1,
          "image": "https://portal.maishaapp.co.tz/media/properties/image1.jpg",
          "is_primary": true
        }
      ],
      "amenities": ["WiFi", "Parking", "Pool", "Restaurant"],
      "status": "available",
      "property_type": {
        "id": 2,
        "name": "hotel"
      }
    },
    {
      "id": 124,
      "title": "Beach Resort Hotel",
      "description": "Beachfront hotel with ocean views",
      "address": "456 Beach Road",
      "rent_amount": "300000.00",
      "images": [...],
      "amenities": ["WiFi", "Pool", "Spa"],
      "status": "available"
    }
  ]
}
```

**Mobile App Code:**
```typescript
async function getHotels(page: number = 1) {
  const params = new URLSearchParams({
    category: 'hotel',
    status: 'available',
    page: page.toString(),
    page_size: '20',
  });
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  return await response.json();
}
```

### Option B: Search Hotels

**Endpoint:** `GET /api/v1/properties/search/`

**Query Parameters:**
- `search` - Search query (hotel name, location, etc.)
- `category=hotel` - Filter to hotels only
- `region` - Filter by region ID
- `min_rent` - Minimum price
- `max_rent` - Maximum price

**Example:**
```http
GET /api/v1/properties/search/?search=beach&category=hotel&min_rent=100000&max_rent=500000
```

**Mobile App Code:**
```typescript
async function searchHotels(query: string, filters?: {
  region?: number;
  minRent?: number;
  maxRent?: number;
}) {
  const params = new URLSearchParams({
    search: query,
    category: 'hotel',
    page: '1',
    page_size: '20',
  });
  
  if (filters?.region) params.append('region', filters.region.toString());
  if (filters?.minRent) params.append('min_rent', filters.minRent.toString());
  if (filters?.maxRent) params.append('max_rent', filters.maxRent.toString());
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/search/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  return await response.json();
}
```

---

## Step 2: Get Hotel Details

**Get detailed information about a specific hotel.**

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
  "description": "Luxury hotel in city center with 50 rooms",
  "address": "123 Main Street",
  "latitude": "-6.7924",
  "longitude": "39.2083",
  "rent_amount": "200000.00",
  "capacity": 100,
  "bedrooms": 50,
  "bathrooms": 50,
  "images": [
    {
      "id": 1,
      "image": "https://portal.maishaapp.co.tz/media/properties/image1.jpg",
      "is_primary": true
    },
    {
      "id": 2,
      "image": "https://portal.maishaapp.co.tz/media/properties/image2.jpg",
      "is_primary": false
    }
  ],
  "amenities": ["WiFi", "Parking", "Pool", "Restaurant", "Gym"],
  "status": "available",
  "available_rooms": 25,
  "property_type": {
    "id": 2,
    "name": "hotel"
  }
}
```

**Mobile App Code:**
```typescript
async function getHotelDetails(hotelId: number) {
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/${hotelId}/`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  if (!response.ok) {
    throw new Error('Hotel not found');
  }
  
  return await response.json();
}
```

**Mobile App Should:**
- Display hotel details (name, description, images, amenities)
- Show "Check Availability" or "Select Dates" button
- Allow user to select check-in and check-out dates

---

## Step 3: Get Available Rooms ⭐ **CRITICAL**

**Get list of available rooms for selected dates.**

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
      "amenities": ["WiFi", "TV", "AC", "Mini Bar"],
      "description": "Spacious deluxe room with city view"
    },
    {
      "id": 11,
      "room_number": "102",
      "room_type": "Standard",
      "price_per_night": "30000.00",
      "capacity": 2,
      "amenities": ["WiFi", "TV"],
      "description": "Comfortable standard room"
    },
    {
      "id": 12,
      "room_number": "201",
      "room_type": "Deluxe",
      "price_per_night": "50000.00",
      "capacity": 2,
      "amenities": ["WiFi", "TV", "AC", "Mini Bar", "Balcony"],
      "description": "Deluxe room with balcony"
    },
    {
      "id": 13,
      "room_number": "301",
      "room_type": "Suite",
      "price_per_night": "80000.00",
      "capacity": 4,
      "amenities": ["WiFi", "TV", "AC", "Mini Bar", "Balcony", "Living Room"],
      "description": "Luxury suite with separate living area"
    }
  ]
}
```

**Mobile App Code:**
```typescript
async function getAvailableRooms(
  propertyId: number,
  checkInDate: string,
  checkOutDate: string
) {
  const params = new URLSearchParams({
    property_id: propertyId.toString(),
    check_in_date: checkInDate,  // Format: YYYY-MM-DD
    check_out_date: checkOutDate, // Format: YYYY-MM-DD
  });
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/available-rooms/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to get available rooms');
  }
  
  return await response.json();
}
```

**Mobile App Should:**
- Display list of available rooms
- Show room details: number, type, price, capacity, amenities
- Allow user to select a specific room
- Calculate total price: `price_per_night × number_of_nights`

**Example Calculation:**
```typescript
function calculateTotalPrice(
  pricePerNight: string,
  checkIn: string,
  checkOut: string
): string {
  const checkInDate = new Date(checkIn);
  const checkOutDate = new Date(checkOut);
  const nights = Math.ceil(
    (checkOutDate.getTime() - checkInDate.getTime()) / (1000 * 60 * 60 * 24)
  );
  
  const price = parseFloat(pricePerNight);
  const total = price * nights;
  
  return total.toFixed(2);
}

// Usage:
const total = calculateTotalPrice(
  room.price_per_night,  // "50000.00"
  "2026-02-01",          // check-in
  "2026-02-05"           // check-out
); // Returns "200000.00" (4 nights × 50000)
```

---

## Step 4: Select Room

**User selects a specific room from available rooms.**

**Mobile App Should:**
- Show selected room details
- Display:
  - Room Number: `101`
  - Room Type: `Deluxe`
  - Price per Night: `50000.00`
  - Total Price: `200000.00` (4 nights)
  - Capacity: `2 guests`
  - Amenities: `WiFi, TV, AC, Mini Bar`
- Show "Book Now" or "Continue to Booking" button

**Selected Room Data:**
```typescript
const selectedRoom = {
  roomId: 10,
  roomNumber: "101",
  roomType: "Deluxe",
  pricePerNight: "50000.00",
  totalPrice: "200000.00",
  capacity: 2,
  amenities: ["WiFi", "TV", "AC", "Mini Bar"],
};
```

---

## Step 5: Create Booking ⭐ **CRITICAL**

**Create booking with selected room.**

**Endpoint:** `POST /api/v1/properties/bookings/create/`

**Request Body:**
```json
{
  "property_id": 123,              // ← Hotel ID from Step 2
  "property_type": "hotel",        // ← Must be "hotel"
  "room_number": "101",            // ← Selected room number from Step 4
  "room_type": "Deluxe",            // ← Selected room type from Step 4
  "check_in_date": "2026-02-01",   // ← Selected check-in date
  "check_out_date": "2026-02-05",  // ← Selected check-out date
  "number_of_guests": 2,           // ← Number of guests
  "total_amount": "200000.00",     // ← Calculated total price
  "customer_name": "John Doe",     // ← Customer name
  "email": "john@example.com",     // ← Customer email
  "phone": "+255700000000",        // ← Customer phone
  "special_requests": "Late check-in preferred"  // Optional
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
  "number_of_guests": 2,
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
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
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

**Mobile App Should:**
- Save `booking_id` (456) for payment step
- Save `booking_reference` (HTL-000456) for display
- Show booking confirmation with details
- Show "Proceed to Payment" button

---

## Step 6: Payment Flow

**Complete payment flow (see `MOBILE_APP_PAYMENT_FLOW_GUIDE.md` for details)**

### 6.1 Create Payment

**Endpoint:** `POST /api/v1/payments/payments/`

**Request:**
```json
{
  "booking": 456,              // ← Booking ID from Step 5
  "amount": "200000.00",       // ← Total amount from booking
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"  // AIRTEL, TIGO, MPESA, HALOPESA
}
```

**Response:**
```json
{
  "id": 80,                    // ← Payment ID
  "booking": 456,
  "amount": "200000.00",
  "status": "pending"
}
```

### 6.2 Initiate Payment Gateway

**Endpoint:** `POST /api/v1/payments/payments/{payment_id}/initiate-gateway/`

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "phone_number_used": "+255700000000",
  "message": "Payment initiated successfully. The customer will receive a payment prompt on their phone."
}
```

### 6.3 Poll Payment Status

**Endpoint:** `GET /api/v1/payments/payments/{payment_id}/`

**Poll every 2-3 seconds until `status` is `completed`**

---

## Step 7: Booking Complete! ✅

**After payment is completed:**

**Mobile App Should:**
- Show success message
- Display booking confirmation:
  - Booking Reference: `HTL-000456`
  - Hotel: `Grand Hotel`
  - Room: `101 - Deluxe`
  - Check-in: `2026-02-01`
  - Check-out: `2026-02-05`
  - Guests: `2`
  - Total Paid: `200000.00`
- Show "View Booking Details" button
- Option to save booking to favorites

---

## 📱 Complete Mobile App Flow Example

```typescript
// Complete Hotel Room Booking Flow
async function completeHotelRoomBooking(
  hotelId: number,
  checkIn: string,
  checkOut: string,
  roomNumber: string,
  customerData: {
    name: string;
    email: string;
    phone: string;
    numberOfGuests: number;
  },
  paymentProvider: string
) {
  try {
    // Step 1: Get available rooms
    const roomsData = await getAvailableRooms(hotelId, checkIn, checkOut);
    
    // Step 2: Find selected room
    const selectedRoom = roomsData.available_rooms.find(
      (room: any) => room.room_number === roomNumber
    );
    
    if (!selectedRoom) {
      throw new Error('Selected room is no longer available');
    }
    
    // Step 3: Calculate total price
    const totalPrice = calculateTotalPrice(
      selectedRoom.price_per_night,
      checkIn,
      checkOut
    );
    
    // Step 4: Create booking
    const booking = await createHotelBooking({
      propertyId: hotelId,
      roomNumber: selectedRoom.room_number,
      roomType: selectedRoom.room_type,
      checkIn,
      checkOut,
      numberOfGuests: customerData.numberOfGuests,
      totalAmount: totalPrice,
      customerName: customerData.name,
      email: customerData.email,
      phone: customerData.phone,
    });
    
    // Step 5: Create payment
    const payment = await fetch('/api/v1/payments/payments/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        booking: booking.booking_id,
        amount: booking.total_amount,
        payment_method: 'mobile_money',
        mobile_money_provider: paymentProvider,
      }),
    }).then(r => r.json());
    
    // Step 6: Initiate payment gateway
    const gateway = await fetch(
      `/api/v1/payments/payments/${payment.id}/initiate-gateway/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ mobile_money_provider: paymentProvider }),
      }
    ).then(r => r.json());
    
    // Step 7: Poll payment status
    let status = 'pending';
    let attempts = 0;
    
    while (status === 'pending' && attempts < 60) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const check = await fetch(
        `/api/v1/payments/payments/${payment.id}/`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      ).then(r => r.json());
      
      status = check.status;
      attempts++;
      
      if (status === 'completed') {
        return {
          success: true,
          booking: booking,
          payment: check,
        };
      }
      
      if (status === 'failed' || status === 'cancelled') {
        throw new Error(`Payment ${status}`);
      }
    }
    
    throw new Error('Payment timeout');
  } catch (error) {
    console.error('Booking failed:', error);
    throw error;
  }
}
```

---

## 🔑 Key Points

### 1. **Room Selection** ✅
- Always check available rooms for selected dates
- Room availability is date-specific
- User must select a specific `room_number`

### 2. **Date Validation** 📅
- `check_out_date` must be after `check_in_date`
- Dates must be in `YYYY-MM-DD` format
- Check room availability before allowing booking

### 3. **Price Calculation** 💰
- Calculate: `price_per_night × number_of_nights`
- Number of nights = `check_out_date - check_in_date`
- Use exact amount from calculation in booking

### 4. **Error Handling** ❌
- **Room not available:** Show error, refresh available rooms
- **Booking failed:** Show error message, allow retry
- **Payment failed:** Allow retry payment

---

## ✅ Quick Reference

### Hotel Room Booking Endpoints

1. `GET /api/v1/properties/?category=hotel` - List hotels
2. `GET /api/v1/properties/search/?category=hotel` - Search hotels
3. `GET /api/v1/properties/{id}/` - Get hotel details
4. `GET /api/v1/properties/available-rooms/?property_id={id}&check_in_date={date}&check_out_date={date}` - Get available rooms
5. `POST /api/v1/properties/bookings/create/` - Create booking with room
6. `POST /api/v1/payments/payments/` - Create payment
7. `POST /api/v1/payments/payments/{id}/initiate-gateway/` - Initiate payment
8. `GET /api/v1/payments/payments/{id}/` - Check payment status

---

## 🎯 Summary

**Complete Hotel Room Booking Flow:**
1. **List/Search Hotels** → Show available hotels
2. **Select Hotel** → Show hotel details
3. **Select Dates** → User chooses check-in/check-out
4. **Get Available Rooms** → Show rooms for selected dates
5. **Select Room** → User picks specific room
6. **Create Booking** → Book selected room
7. **Pay** → Complete payment
8. **Done!** → Show booking confirmation

**Ready for Mobile App Integration!** 🚀
