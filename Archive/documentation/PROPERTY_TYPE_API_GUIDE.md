# Property Type API Guide - How to Access House, Hotel, Lodge, and Venue

## Overview

**YES!** A tenant can access ALL property types (House, Hotel, Lodge, Venue) using the **SAME API endpoints**. The differences are in the **data fields** returned, not in separate endpoints.

---

## 🏠 Property Types Available

1. **House** - Residential properties for rent
2. **Hotel** - Commercial hotel properties with rooms
3. **Lodge** - Lodge/accommodation facilities
4. **Venue** - Event venues and spaces

---

## 📊 API Architecture

### Single Set of APIs for All Property Types

All property types use the **same API endpoints**. You distinguish between them using:

1. **property_type** filter parameter
2. **Different data fields** in responses
3. **Filtering by property_type_id**

---

## 🔓 Public APIs (No Authentication Required)

### 1. List All Properties (All Types)
```http
GET /api/v1/properties/
```

**Filter by property type:**
```http
GET /api/v1/properties/?property_type=<type_id>
```

**Available Property Type IDs:**
- Get type IDs: `GET /api/v1/property-types/`

**Example - Get only houses:**
```http
GET /api/v1/properties/?property_type=1
```

**Example - Get only hotels:**
```http
GET /api/v1/properties/?property_type=2
```

**Example - Get only lodges:**
```http
GET /api/v1/properties/?property_type=3
```

**Example - Get only venues:**
```http
GET /api/v1/properties/?property_type=4
```

### 2. Search Properties (All Types)
```http
POST /api/v1/search/
```

**Request Body Example:**
```json
{
  "query": "beach",
  "filters": {
    "property_types": [1, 2, 3, 4],  // House, Hotel, Lodge, Venue
    "rent_range": {"min": 100, "max": 500},
    "regions": [1]
  }
}
```

### 3. Get Property Details (All Types)
```http
GET /api/v1/properties/{id}/
```

Returns different fields based on type:

**House Response Example:**
```json
{
  "id": 1,
  "title": "Modern 3BR House",
  "property_type": {"id": 1, "name": "House"},
  "bedrooms": 3,
  "bathrooms": 2,
  "rent_amount": "1200.00"
}
```

**Hotel Response Example:**
```json
{
  "id": 2,
  "title": "Beachfront Hotel",
  "property_type": {"id": 2, "name": "Hotel"},
  "total_rooms": 50,
  "room_types": {
    "standard": 20,
    "deluxe": 20,
    "suite": 10
  },
  "base_rate": "80.00"
}
```

**Venue Response Example:**
```json
{
  "id": 3,
  "title": "Conference Hall",
  "property_type": {"id": 4, "name": "Venue"},
  "capacity": 500,
  "venue_type": "Conference",
  "rent_amount": "5000.00"
}
```

### 4. List Property Types
```http
GET /api/v1/property-types/
```

**Response:**
```json
[
  {"id": 1, "name": "House", "description": "Residential properties"},
  {"id": 2, "name": "Hotel", "description": "Commercial hotels with rooms"},
  {"id": 3, "name": "Lodge", "description": "Accommodation lodges"},
  {"id": 4, "name": "Venue", "description": "Event venues and spaces"}
]
```

### 5. Featured Properties (All Types)
```http
GET /api/v1/featured/
```

### 6. Recent Properties (All Types)
```http
GET /api/v1/recent/
```

---

## 🔒 Protected APIs (Authentication Required)

### 1. Search with Filters (All Types)
```http
POST /api/v1/search/
Authorization: Bearer <access_token>
```

### 2. Get My Properties (All Types)
```http
GET /api/v1/my-properties/
Authorization: Bearer <access_token>
```

Returns all property types owned by the user.

### 3. Toggle Favorite (All Types)
```http
POST /api/v1/toggle-favorite/
Authorization: Bearer <access_token>

Body: {"property_id": 1}
```

### 4. Get Favorites (All Types)
```http
GET /api/v1/favorites/
Authorization: Bearer <access_token>
```

---

## 📋 Field Differences by Property Type

### Common Fields (All Types)
- `id`, `title`, `description`
- `address`, `region`, `latitude`, `longitude`
- `property_type` (ID and name)
- `rent_amount`, `deposit_amount`
- `status`, `amenities`
- `images`, `created_at`, `updated_at`

### House-Specific Fields
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `size_sqft` - Square footage
- `floor_number` - Floor number
- `total_floors` - Total floors
- `is_furnished` - Whether furnished
- `pets_allowed` - Pet policy

### Hotel/Lodge-Specific Fields
- `total_rooms` - Total number of rooms
- `room_types` - JSON object with room types
  ```json
  {
    "standard": 20,
    "deluxe": 15,
    "suite": 10,
    "penthouse": 2
  }
  ```
- `base_rate` - Base room rate

### Venue-Specific Fields
- `capacity` - Maximum occupancy
- `venue_type` - Type of venue (conference, wedding, etc.)
- `event_facilities` - Available facilities

---

## 🎯 How to Filter by Property Type

### Method 1: Using Property Type ID
```bash
# Get houses
GET /api/v1/properties/?property_type=1

# Get hotels
GET /api/v1/properties/?property_type=2

# Get lodges
GET /api/v1/properties/?property_type=3

# Get venues
GET /api/v1/properties/?property_type=4
```

### Method 2: Using Property Type Name (in search)
```json
POST /api/v1/search/
{
  "filters": {
    "property_types": [1, 2]  // House and Hotel
  }
}
```

### Method 3: Get All Types Together
```bash
# No filter = get all types
GET /api/v1/properties/
```

---

## 📱 Mobile App Implementation Examples

### Example 1: Browse All Property Types
```dart
// Get all properties (house, hotel, lodge, venue)
GET http://127.0.0.1:8001/api/v1/properties/
```

### Example 2: Filter by Type in UI
```dart
// User selects "Hotels only"
GET http://127.0.0.1:8001/api/v1/properties/?property_type=2

// User selects "Venues only"
GET http://127.0.0.1:8001/api/v1/properties/?property_type=4
```

### Example 3: Advanced Search
```dart
POST http://127.0.0.1:8001/api/v1/search/
{
  "filters": {
    "property_types": [1, 2],  // House and Hotel
    "rent_range": {"min": 50, "max": 200},
    "regions": [1, 2]
  }
}
```

---

## 🔑 Key Points

### ✅ UNIFIED APIs
- **Same endpoints** for all property types
- **No separate APIs** for house/hotel/lodge/venue
- **Filtering** by `property_type` parameter

### ✅ RESPONSE DIFFERENCES
- **Same structure** for all properties
- **Different fields** based on type
- **Check property_type** in response to determine type

### ✅ TENANT EXPERIENCE
1. Browse all types together
2. Filter by specific type
3. View property details (fields vary by type)
4. Search across all types
5. Add any type to favorites

---

## 📊 Complete API List for All Property Types

### Public APIs (9 endpoints)
1. ✅ `GET /properties/` - List all (filterable by type)
2. ✅ `GET /properties/{id}/` - Get any property type details
3. ✅ `GET /property-types/` - List all types
4. ✅ `GET /regions/` - List all regions
5. ✅ `GET /amenities/` - List all amenities
6. ✅ `GET /featured/` - Featured properties (all types)
7. ✅ `GET /recent/` - Recent properties (all types)
8. ✅ `POST /auth/signup/` - User registration
9. ✅ `POST /auth/login/` - User login

### Protected APIs (7 endpoints)
1. ✅ `POST /search/` - Search all types
2. ✅ `GET /my-properties/` - Get my properties (all types)
3. ✅ `POST /toggle-favorite/` - Favorite any type
4. ✅ `GET /favorites/` - Get favorites (all types)
5. ✅ `GET /auth/profile/` - Get profile
6. ✅ `PUT /auth/profile/update/` - Update profile
7. ✅ `POST /auth/change-password/` - Change password

---

## 🧪 Testing Examples

### Test 1: Get All Properties
```bash
curl http://127.0.0.1:8001/api/v1/properties/
```
Returns: Houses, Hotels, Lodges, and Venues

### Test 2: Get Only Hotels
```bash
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=2"
```

### Test 3: Get Only Venues
```bash
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=4"
```

### Test 4: Search Across Types
```bash
curl -X POST http://127.0.0.1:8001/api/v1/search/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {
      "property_types": [1, 2],
      "rent_range": {"min": 100, "max": 300}
    }
  }'
```

---

## 📚 Summary

### The Answer to Your Question:

**YES!** Tenants can access **house, hotel, lodge, AND venue** through the **same public and protected APIs**. 

**How it works:**
- ✅ **Same API endpoints** for all property types
- ✅ **Filter by property_type** to get specific types
- ✅ **Same authentication** for all types
- ✅ **Different fields** in responses based on type
- ✅ **Unified search** across all types
- ✅ **Favorites work** for all types

**Total APIs Available:**
- **Public**: 9 endpoints (work for all types)
- **Protected**: 7 endpoints (work for all types)
- **Grand Total**: 16 core APIs for all property types

**Property Type IDs:**
- 1 = House
- 2 = Hotel
- 3 = Lodge
- 4 = Venue

---

## 🔗 Related Documents

- **TENANT_API_REFERENCE.md** - Complete API reference
- **TENANT_API_QUICK_REFERENCE.md** - Quick reference card
- **COMPLETE_API_TEST_SUMMARY.md** - Test results
- **SWAGGER_TESTING_GUIDE.md** - How to test in Swagger UI

---

**Bottom Line:** One unified API system works for ALL property types! 🏠🏨🏕️🎪


