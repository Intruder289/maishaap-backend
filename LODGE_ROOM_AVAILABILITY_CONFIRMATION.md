# Lodge Room Availability - Confirmation

## ✅ Confirmation: All Fixes Apply to Lodges

All the room availability fixes implemented for hotels **also apply to lodges** because they share the same underlying system.

## Shared Infrastructure

### 1. Same Room Model
- **File**: `properties/models.py`
- Lodges and hotels use the **same `Room` model** (line 987: `"""Model for hotel/lodge rooms"""`)
- Both property types have rooms with the same fields: `room_number`, `room_type`, `status`, `current_booking`, etc.

### 2. Same Room Status Sync Logic
- **File**: `properties/models.py` - `Room.sync_status_from_bookings()`
- The `sync_status_from_bookings()` method works for **both hotels and lodges**
- Uses `check_out_date__gt=today` (fixed) - rooms become available on checkout day
- Property type check: `self.property_obj.is_hotel or property_type.name.lower() == 'lodge'` (line 1082)

### 3. Same Available Rooms API
- **File**: `properties/api_views.py` - `available_rooms_api()`
- **Endpoint**: `GET /api/v1/properties/available-rooms/?property_id=X`
- Explicitly accepts both `'hotel'` and `'lodge'` property types (line 3637)
- Uses `check_out_date__gt=today` for consistency
- Returns only truly available rooms

### 4. Same Booking Creation API
- **File**: `properties/api_views.py` - `create_booking_with_room_api()`
- **Endpoint**: `POST /api/v1/properties/bookings/create/`
- Accepts `property_type: "lodge"` (line 3984, 3991)
- Generates lodge booking reference: `LDG-XXXXXX` (line 4214)
- Room assignment logic applies to lodges (line 4239: `if property_type != 'venue'`)

### 5. Same Automatic Status Sync Signal
- **File**: `properties/signals.py` - `sync_room_status_on_booking_change()`
- Works for **any booking with a room_number**, regardless of property type
- Automatically syncs room status when lodge bookings are checked out or cancelled

### 6. Same Daily Sync Command
- **File**: `properties/management/commands/sync_room_status.py`
- Explicitly includes both hotels and lodges (line 36):
  ```python
  properties_query = Property.objects.filter(
      property_type__name__in=['hotel', 'lodge']
  )
  ```

## Lodge-Specific Features Verified

### ✅ Room Assignment
- Lodges require room assignment (same as hotels)
- Room validation and conflict checking works identically
- Room status updates automatically when bookings end

### ✅ Booking Reference Format
- Hotels: `HTL-XXXXXX`
- Lodges: `LDG-XXXXXX` (line 4214)
- Venues: `VEN-XXXXXX`

### ✅ Date Handling
- Same date validation logic
- Same conflict detection
- Rooms become available on checkout day
- Future bookings allowed starting day after checkout

## Example: Lodge Booking Flow

### Scenario: Lodge Room Booking 25/1-27/1, New Booking 28/1-30/1

1. **Create Lodge Booking**:
   ```json
   POST /api/v1/properties/bookings/create/
   {
     "property_id": 123,
     "property_type": "lodge",
     "room_number": "10",
     "room_type": "Deluxe",
     "check_in_date": "2026-01-25",
     "check_out_date": "2026-01-27",
     "number_of_guests": 2,
     "total_amount": "200000.00",
     "customer_name": "John Doe",
     "email": "john@example.com",
     "phone": "+255700000000"
   }
   ```
   - ✅ Room 10 becomes "occupied"
   - ✅ Booking reference: `LDG-000001`

2. **On 27/1 (Checkout Day)**:
   - ✅ `check_out_date__gt=today` → FALSE (27/1 is NOT > 27/1)
   - ✅ Room status syncs → Room becomes "available"
   - ✅ Signal fires automatically → Room status updated

3. **Create New Booking Starting 28/1**:
   ```json
   POST /api/v1/properties/bookings/create/
   {
     "property_id": 123,
     "property_type": "lodge",
     "room_number": "10",
     "check_in_date": "2026-01-28",
     "check_out_date": "2026-01-30",
     ...
   }
   ```
   - ✅ Conflict check: `28/1 < 27/1` = FALSE → No conflict
   - ✅ Room is available → Booking allowed
   - ✅ New booking reference: `LDG-000002`

## Available Rooms API for Lodges

### Get Available Lodge Rooms
```http
GET /api/v1/properties/available-rooms/?property_id=123&check_in_date=2026-01-28&check_out_date=2026-01-30
```

**Response**:
```json
{
  "property_id": 123,
  "property_title": "Mountain Lodge",
  "property_type": "lodge",
  "total_rooms": 20,
  "available_count": 15,
  "check_in_date": "2026-01-28",
  "check_out_date": "2026-01-30",
  "rooms": [
    {
      "room_id": 10,
      "room_number": "10",
      "room_type": "Deluxe",
      "status": "available",
      "base_rate": "100000.00",
      ...
    }
  ]
}
```

## Summary

✅ **All fixes apply to lodges**:
- ✅ Automatic room availability on checkout day
- ✅ Future bookings allowed (day after checkout)
- ✅ Automatic status sync via signals
- ✅ Daily sync command includes lodges
- ✅ Same Room model and logic
- ✅ Same API endpoints (with property_type="lodge")
- ✅ Same date conflict detection
- ✅ Same room status management

**Lodges work identically to hotels** - all the room availability fixes are fully functional for lodges!
