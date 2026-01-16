# APIs That Return Hotel Room Status, Venue Status, or Lodge Room Status

## Summary

This document lists all APIs that return status information for hotel rooms, lodge rooms, or venues.

---

## 1. Available Rooms API (Hotels & Lodges)

**Endpoint:** `GET /api/v1/available-rooms/`

**Description:** Returns available rooms for hotel or lodge properties with their status information.

**Query Parameters:**
- `property_id` (required): The ID of the hotel/lodge property
- `check_in_date` (optional): Check-in date in YYYY-MM-DD format
- `check_out_date` (optional): Check-out date in YYYY-MM-DD format

**Response includes:**
- `property_id`: Property ID
- `property_title`: Property name
- `property_type`: "hotel" or "lodge"
- `total_rooms`: Total number of rooms in the property
- `available_count`: Number of available rooms
- `check_in_date`: Check-in date filter (if provided)
- `check_out_date`: Check-out date filter (if provided)
- `rooms`: Array of room objects, each containing:
  - `id`: Room ID
  - `room_number`: Room number/identifier
  - `room_type`: Type of room (e.g., "Standard", "Deluxe", "Suite")
  - `floor_number`: Floor number (nullable)
  - `capacity`: Maximum occupancy
  - `bed_type`: Type of bed (nullable)
  - `amenities`: Room amenities (nullable)
  - `base_rate`: Room price per night
  - **`status`**: Room status - one of:
    - `"available"` - Room is available for booking
    - `"occupied"` - Room is currently occupied
    - `"maintenance"` - Room is under maintenance
    - `"out_of_order"` - Room is out of order
  - **`is_available`**: Boolean indicating if room is available

**Example Request:**
```http
GET /api/v1/available-rooms/?property_id=1&check_in_date=2024-01-15&check_out_date=2024-01-20
```

**Example Response:**
```json
{
  "property_id": 1,
  "property_title": "Grand Hotel",
  "property_type": "hotel",
  "total_rooms": 50,
  "available_count": 35,
  "check_in_date": "2024-01-15",
  "check_out_date": "2024-01-20",
  "rooms": [
    {
      "id": 101,
      "room_number": "101",
      "room_type": "Standard",
      "floor_number": 1,
      "capacity": 2,
      "bed_type": "Double",
      "amenities": "WiFi, TV, AC",
      "base_rate": "150.00",
      "status": "available",
      "is_available": true
    },
    {
      "id": 102,
      "room_number": "102",
      "room_type": "Deluxe",
      "floor_number": 1,
      "capacity": 2,
      "bed_type": "Queen",
      "amenities": "WiFi, TV, AC, Mini Bar",
      "base_rate": "200.00",
      "status": "occupied",
      "is_available": false
    }
  ]
}
```

**Swagger Documentation:** ✅ Fully documented

**Notes:**
- Only returns rooms with `status = "available"` by default
- Automatically syncs room status from bookings before returning results
- Filters out rooms with conflicting bookings if date range is provided
- Public endpoint (no authentication required)

---

## 2. Property Detail API (Includes Status)

**Endpoint:** `GET /api/v1/properties/{pk}/`

**Description:** Returns detailed property information including status. For hotels and lodges, includes available rooms information.

**URL Parameters:**
- `pk`: The ID of the property

**Response includes:**
- **`status`**: Property status - one of:
  - `"available"` - Available for booking
  - `"rented"` - Currently rented
  - `"occupied"` - Currently occupied
  - `"under_maintenance"` - Under maintenance
  - `"unavailable"` - Unavailable
- For hotels/lodges: `available_rooms` array with room status
- All property details (title, description, location, etc.)

**Example Request:**
```http
GET /api/v1/properties/1/
```

**Swagger Documentation:** ✅ Fully documented

**Authentication:** Required (IsAuthenticated)

---

## 3. Property List API (Includes Status)

**Endpoint:** `GET /api/v1/properties/`

**Description:** Returns a list of properties. Each property includes its status.

**Query Parameters:**
- `status` (optional): Filter by property status

**Response includes:**
- `status`: Property status for each property

**Swagger Documentation:** ✅ Fully documented

---

## Room Status Values

All room status APIs return one of these status values:

1. **`"available"`** - Room is available for booking
   - No active bookings
   - Not under maintenance
   - Not out of order

2. **`"occupied"`** - Room is currently occupied
   - Has active booking (pending, confirmed, or checked_in)
   - Guest is currently staying

3. **`"maintenance"`** - Room is under maintenance
   - Manually set by admin
   - Not available for booking

4. **`"out_of_order"`** - Room is out of order
   - Manually set by admin
   - Not available for booking

---

## Venue Status

For **venues**, the system uses the same property status values:
- `"available"` - Available for booking
- `"rented"` - Currently rented
- `"occupied"` - Currently occupied
- `"under_maintenance"` - Under maintenance
- `"unavailable"` - Unavailable

Venues don't have individual rooms, so use the **Property Availability API** to check venue status.

---

## Summary Table

| API Endpoint | Property Types | Returns Room Status | Returns Property Status | Swagger Docs |
|-------------|----------------|---------------------|------------------------|--------------|
| `/api/v1/available-rooms/` | Hotels, Lodges | ✅ Yes | ✅ Yes | ✅ Yes |
| `/api/v1/properties/{id}/` | All types | ✅ Yes (hotels/lodges) | ✅ Yes | ✅ Yes |
| `/api/v1/properties/` | All types | ❌ No | ✅ Yes | ✅ Yes |

---

## Recommended Usage

### For Hotel/Lodge Room Status:
Use **`GET /api/v1/available-rooms/?property_id={id}`** - This is specifically designed for hotels and lodges and returns detailed room status information.

### For Venue Status:
Use **`GET /api/v1/properties/{id}/`** - This returns venue status and all property details.

### For General Property Status:
Use **`GET /api/v1/properties/{id}/`** - Returns comprehensive property information including status.

---

**Last Updated:** Analysis Date
