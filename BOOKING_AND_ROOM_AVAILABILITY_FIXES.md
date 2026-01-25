# Booking and Room Availability Fixes

**Date:** January 25, 2026

---

## ✅ Issues Fixed

### 1. **Mobile App Bookings Not Showing in Hotel Management** ✅

**Problem:** Bookings created via mobile app were not visible in hotel management interface.

**Root Cause:** The web view (`hotel_bookings`) filters bookings but mobile app bookings should appear since they use the same `properties.Booking` model.

**Solution:** Created a new REST API endpoint for retrieving bookings that property owners can use:

**New Endpoint:** `GET /api/v1/properties/bookings/`

**Query Parameters:**
- `property_id` - Filter by specific property (optional)
- `property_type` - Filter by type: `hotel`, `lodge`, `venue` (optional)
- `status` - Filter by booking status: `pending`, `confirmed`, `checked_in`, `checked_out`, `cancelled` (optional)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Example:**
```http
GET /api/v1/properties/bookings/?property_type=hotel&status=confirmed
```

**Response:**
```json
{
  "count": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "results": [
    {
      "id": 456,
      "booking_reference": "HTL-000456",
      "property_id": 123,
      "property_title": "Grand Hotel",
      "property_type": "hotel",
      "customer": {
        "id": 10,
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+255700000000"
      },
      "check_in_date": "2026-02-01",
      "check_out_date": "2026-02-05",
      "room_number": "101",
      "room_type": "Deluxe",
      "booking_status": "confirmed",
      "payment_status": "paid",
      "total_amount": "200000.00",
      "created_at": "2026-01-25 10:30:00"
    }
  ]
}
```

**Features:**
- ✅ Returns bookings from `properties.Booking` model (mobile app bookings)
- ✅ Filters by property owner (multi-tenancy)
- ✅ Supports pagination
- ✅ Supports filtering by property, type, and status
- ✅ Includes all booking details

---

### 2. **Available Rooms Showing Booked/Occupied Rooms** ✅

**Problem:** Available rooms API was showing rooms that were booked or occupied, allowing users to book unavailable rooms.

**Root Cause:** The API was not properly checking for active bookings, especially when dates weren't provided.

**Solution:** Enhanced the available rooms API to:
- ✅ Always check for active bookings (even when dates aren't provided)
- ✅ Only return truly available rooms
- ✅ Optionally show unavailable rooms with booking dates

**Updated Endpoint:** `GET /api/v1/properties/available-rooms/`

**New Query Parameter:**
- `show_unavailable` - If `true`, also returns unavailable rooms with booking dates (default: `false`)

**Enhanced Logic:**
1. **Syncs room status** from bookings (`room.sync_status_from_bookings()`)
2. **Checks for active bookings** (even if dates aren't provided):
   - Status: `pending`, `confirmed`, `checked_in`
   - Check-out date >= today
   - Not deleted (`is_deleted=False`)
   - Excludes: `cancelled`, `checked_out`, `no_show`
3. **Checks for date conflicts** when dates are provided
4. **Only returns available rooms** by default

**Response (Default - Only Available Rooms):**
```json
{
  "property_id": 123,
  "property_title": "Grand Hotel",
  "property_type": "hotel",
  "total_rooms": 50,
  "available_count": 25,
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "rooms": [
    {
      "id": 10,
      "room_number": "101",
      "room_type": "Deluxe",
      "base_rate": "50000.00",
      "status": "available",
      "is_available": true
    }
  ]
}
```

**Response (With `show_unavailable=true`):**
```json
{
  "property_id": 123,
  "property_title": "Grand Hotel",
  "property_type": "hotel",
  "total_rooms": 50,
  "available_count": 25,
  "unavailable_count": 25,
  "check_in_date": "2026-02-01",
  "check_out_date": "2026-02-05",
  "rooms": [
    {
      "id": 10,
      "room_number": "101",
      "room_type": "Deluxe",
      "status": "available",
      "is_available": true
    }
  ],
  "unavailable_rooms": [
    {
      "room_id": 11,
      "room_number": "102",
      "room_type": "Standard",
      "status": "occupied",
      "reason": "booked",
      "booked_from": "2026-01-20",
      "booked_until": "2026-02-10",
      "booking_reference": "HTL-000123"
    },
    {
      "room_id": 12,
      "room_number": "201",
      "room_type": "Deluxe",
      "status": "maintenance",
      "reason": "room_status_maintenance"
    }
  ]
}
```

**Key Improvements:**
- ✅ **Always checks active bookings** - Rooms with active bookings are excluded
- ✅ **Checks room status** - Only `available` status rooms are shown
- ✅ **Checks current_booking** - Rooms with current bookings are excluded
- ✅ **Date conflict checking** - When dates provided, checks for conflicts
- ✅ **Booking dates shown** - If `show_unavailable=true`, shows when room will be free

---

## 🔧 Technical Details

### Available Rooms API Logic Flow

```
1. Get all active rooms for property
2. For each room:
   a. Sync room status from bookings
   b. Check for active bookings (status: pending/confirmed/checked_in, check_out >= today)
   c. If dates provided, check for date conflicts
   d. If room has conflicts OR status != 'available' OR has current_booking:
      - Skip (don't add to available list)
      - If show_unavailable=true, add to unavailable_rooms with booking dates
   e. If room passes all checks:
      - Add to available_rooms list
3. Return only available rooms (or include unavailable if requested)
```

### Bookings List API Logic Flow

```
1. Get bookings for properties owned by user (or all if admin)
2. Filter by property_id if provided
3. Filter by property_type if provided
4. Filter by status if provided
5. Exclude soft-deleted bookings (is_deleted=False)
6. Paginate results
7. Return serialized booking data
```

---

## 📋 API Endpoints Summary

### New Endpoint: List Bookings

**Endpoint:** `GET /api/v1/properties/bookings/`

**Authentication:** Required (JWT Bearer Token)

**Permissions:**
- Property owners see bookings for their properties
- Admins/staff see all bookings

**Use Cases:**
- Mobile app: Property owners can view their bookings
- Hotel management: Can use this API to display bookings
- Filtering: Filter by property, type, status

---

### Updated Endpoint: Available Rooms

**Endpoint:** `GET /api/v1/properties/available-rooms/`

**Changes:**
- ✅ Only returns truly available rooms (not booked/occupied)
- ✅ Checks active bookings even when dates aren't provided
- ✅ New parameter: `show_unavailable` (optional)

**Query Parameters:**
- `property_id` (required)
- `check_in_date` (optional)
- `check_out_date` (optional)
- `show_unavailable` (optional) - If `true`, includes unavailable rooms with booking dates

---

## ✅ Verification

**Available Rooms API:**
- ✅ Only shows rooms with `status='available'`
- ✅ Excludes rooms with active bookings
- ✅ Excludes rooms with `current_booking`
- ✅ Checks date conflicts when dates provided
- ✅ Optionally shows unavailable rooms with booking dates

**Bookings List API:**
- ✅ Returns bookings from `properties.Booking` model
- ✅ Filters by property owner
- ✅ Supports pagination
- ✅ Supports filtering
- ✅ Excludes soft-deleted bookings

---

## 🎯 Mobile App Integration

### View Bookings (Property Owner)

```typescript
async function getMyBookings(propertyType?: string, status?: string) {
  const params = new URLSearchParams({
    page: '1',
    page_size: '20',
  });
  
  if (propertyType) params.append('property_type', propertyType);
  if (status) params.append('status', status);
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/bookings/?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  return await response.json();
}
```

### Get Available Rooms (Enhanced)

```typescript
async function getAvailableRooms(
  propertyId: number,
  checkIn?: string,
  checkOut?: string,
  showUnavailable: boolean = false
) {
  const params = new URLSearchParams({
    property_id: propertyId.toString(),
  });
  
  if (checkIn) params.append('check_in_date', checkIn);
  if (checkOut) params.append('check_out_date', checkOut);
  if (showUnavailable) params.append('show_unavailable', 'true');
  
  const response = await fetch(
    `https://portal.maishaapp.co.tz/api/v1/properties/available-rooms/?${params}`,
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

## ✅ Summary

**Fixed Issues:**
1. ✅ **Bookings List API** - Property owners can now view their bookings via API
2. ✅ **Available Rooms Filtering** - Only truly available rooms are shown
3. ✅ **Booking Dates Display** - Unavailable rooms show booking dates (optional)

**Ready for Mobile App Integration!** 🚀
