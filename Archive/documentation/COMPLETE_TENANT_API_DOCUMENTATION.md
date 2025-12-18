# Complete Tenant API Documentation

## Table of Contents
1. [Overview](#overview)
2. [API Architecture](#api-architecture)
3. [Authentication](#authentication)
4. [Public APIs](#public-apis)
5. [Protected APIs](#protected-apis)
6. [Property Types](#property-types)
7. [API Examples](#api-examples)
8. [Testing Guide](#testing-guide)
9. [Summary](#summary)

---

## Overview

### Base URL
```
http://127.0.0.1:8001/api/v1
```

### Total APIs Available
- **Public APIs**: 9 endpoints (no authentication)
- **Protected APIs**: 7 endpoints (JWT authentication required)
- **Grand Total**: 16 core APIs

### Property Types Supported
All APIs work for ALL property types:
- ✅ **House** (1) - Residential rental properties
- ✅ **Hotel** (2) - Commercial hotels with rooms
- ✅ **Lodge** (3) - Lodge/accommodation facilities
- ✅ **Venue** (4) - Event venues and spaces

---

## API Architecture

### Unified API System

**Key Point**: The same API endpoints work for ALL property types. There are NO separate APIs for house, hotel, lodge, or venue.

```
┌─────────────────────────────────────────────────────┐
│        UNIFIED API SYSTEM                           │
│  ┌────────────────────────────────────────────┐     │
│  │  GET  /properties/                         │     │
│  │  GET  /properties/{id}/                   │     │
│  │  POST /search/                            │     │
│  │  GET  /featured/                           │     │
│  │  GET  /recent/                            │     │
│  │  GET  /favorites/                         │     │
│  └────────────────────────────────────────────┘     │
│               ↓                                      │
│  Works for: House ✅ Hotel ✅ Lodge ✅ Venue ✅     │
└─────────────────────────────────────────────────────┘
```

### Filtering by Property Type

To get specific property types, use the `property_type` filter parameter:

```
GET /api/v1/properties/?property_type=<id>
```

**Property Type IDs:**
- `1` = House
- `2` = Hotel
- `3` = Lodge
- `4` = Venue

---

## Authentication

### Getting JWT Tokens

#### 1. User Signup (Public)
```http
POST /api/v1/auth/signup/
Content-Type: application/json

{
  "username": "tenant_user",
  "email": "tenant@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+254712345678",
  "role": "tenant"
}
```

**Response**: Returns user data with pending approval status

#### 2. User Login (Public)
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "tenant@example.com",
  "password": "securepassword123"
}
```

**Response**: Returns JWT tokens + user data
```json
{
  "success": true,
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 1,
    "username": "tenant_user",
    "email": "tenant@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Using JWT Tokens

Add this header to all protected API requests:
```
Authorization: Bearer <access_token>
```

---

## Public APIs

### Base URL
```
http://127.0.0.1:8001/api/v1
```

### Authentication: NOT Required ✅

#### 1. User Signup
```http
POST /auth/signup/
```
Register a new tenant account (requires admin approval)

#### 2. User Login
```http
POST /auth/login/
```
Login and get JWT tokens

#### 3. List All Properties (All Types)
```http
GET /properties/
```

**Query Parameters:**
- `property_type` - Filter by type ID (1=House, 2=Hotel, 3=Lodge, 4=Venue)
- `search` - Search in title, description, address
- `min_rent` - Minimum rent amount
- `max_rent` - Maximum rent amount
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `region` - Filter by region ID
- `status` - Filter by status (available, rented, under_maintenance)
- `is_furnished` - Filter furnished properties
- `pets_allowed` - Filter pet-friendly properties
- `page` - Page number for pagination

**Examples:**
```bash
# Get all properties
GET /properties/

# Get only houses
GET /properties/?property_type=1

# Get hotels with specific rent range
GET /properties/?property_type=2&min_rent=50&max_rent=200
```

#### 4. Get Property Details
```http
GET /properties/{id}/
```
Get detailed information about a specific property

**Response varies by property type:**

**House Response:**
```json
{
  "id": 1,
  "title": "Modern 3BR House",
  "property_type": {"id": 1, "name": "House"},
  "bedrooms": 3,
  "bathrooms": 2,
  "size_sqft": 1500,
  "rent_amount": "1200.00",
  "deposit_amount": "1200.00",
  "address": "123 Main Street",
  "region": {"id": 1, "name": "Downtown"},
  "amenities": [...]
}
```

**Hotel Response:**
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
  "base_rate": "80.00",
  "address": "456 Beach Road",
  "amenities": [...]
}
```

**Venue Response:**
```json
{
  "id": 3,
  "title": "Conference Hall",
  "property_type": {"id": 4, "name": "Venue"},
  "capacity": 500,
  "venue_type": "Conference",
  "rent_amount": "5000.00",
  "address": "789 Business Park",
  "amenities": [...]
}
```

#### 5. List Property Types
```http
GET /property-types/
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

#### 6. List Regions
```http
GET /regions/
```

#### 7. List Amenities
```http
GET /amenities/
```

#### 8. Featured Properties (All Types)
```http
GET /featured/
```

#### 9. Recent Properties (All Types)
```http
GET /recent/
```

---

## Protected APIs

### Base URL
```
http://127.0.0.1:8001/api/v1
```

### Authentication: Required ✅

**Header Required:**
```
Authorization: Bearer <access_token>
```

#### 1. Get User Profile
```http
GET /auth/profile/
Authorization: Bearer <access_token>
```

#### 2. Update User Profile
```http
PUT /auth/profile/update/
Authorization: Bearer <access_token>

{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+254712345679"
}
```

#### 3. Change Password
```http
POST /auth/change-password/
Authorization: Bearer <access_token>

{
  "current_password": "oldpassword123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

#### 4. Verify Token
```http
POST /auth/verify/
Authorization: Bearer <access_token>
```

#### 5. Refresh Token
```http
POST /auth/refresh/

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 6. Logout
```http
POST /auth/logout/
Authorization: Bearer <access_token>

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 7. Advanced Search (All Types)
```http
POST /search/
Authorization: Bearer <access_token>

{
  "query": "beach hotel",
  "filters": {
    "property_types": [1, 2, 3, 4],
    "rent_range": {
      "min": 50,
      "max": 300
    },
    "bedrooms": [1, 2, 3],
    "amenities": [1, 2, 5],
    "regions": [1, 2]
  }
}
```

#### 8. Get My Properties (All Types)
```http
GET /my-properties/
Authorization: Bearer <access_token>
```

Returns all properties owned by the authenticated user (all types)

#### 9. Toggle Favorite (All Types)
```http
POST /toggle-favorite/
Authorization: Bearer <access_token>

{
  "property_id": 1
}
```

#### 10. Get Favorite Properties (All Types)
```http
GET /favorites/
Authorization: Bearer <access_token>
```

Returns all favorited properties (all types)

---

## Property Types

### Common to All Types
These fields exist for ALL property types:
- `id`, `title`, `description`
- `address`, `region`, `latitude`, `longitude`
- `property_type` (ID and name)
- `rent_amount`, `deposit_amount`
- `status`, `amenities`, `images`
- `is_furnished`, `is_featured`, `is_active`
- `created_at`, `updated_at`

### House-Specific Fields
```json
{
  "bedrooms": 3,
  "bathrooms": 2,
  "size_sqft": 1500,
  "floor_number": 2,
  "total_floors": 5,
  "pets_allowed": true
}
```

### Hotel/Lodge-Specific Fields
```json
{
  "total_rooms": 50,
  "room_types": {
    "standard": 20,
    "deluxe": 20,
    "suite": 10
  },
  "base_rate": "80.00"
}
```

### Venue-Specific Fields
```json
{
  "capacity": 500,
  "venue_type": "Conference",
  "event_facilities": ["sound system", "projector", "stage"]
}
```

---

## API Examples

### Example 1: Browse All Property Types
```bash
curl http://127.0.0.1:8001/api/v1/properties/
```
Returns: Houses, Hotels, Lodges, and Venues together

### Example 2: Filter by Property Type
```bash
# Get only houses
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=1"

# Get only hotels
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=2"

# Get only lodges
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=3"

# Get only venues
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=4"
```

### Example 3: Search with Filters
```bash
curl -X POST http://127.0.0.1:8001/api/v1/search/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "beach",
    "filters": {
      "property_types": [1, 2],
      "rent_range": {"min": 50, "max": 200}
    }
  }'
```

### Example 4: Get Property Details
```bash
curl http://127.0.0.1:8001/api/v1/properties/1/
```
Returns different fields based on whether it's a house, hotel, lodge, or venue

### Example 5: List My Favorites
```bash
curl http://127.0.0.1:8001/api/v1/favorites/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Returns all favorited properties regardless of type

---

## Testing Guide

### Test Credentials
```
Email: api_test@example.com
Password: test123
Role: Tenant
Status: ✅ Approved
```

### Access Swagger UI
```
http://127.0.0.1:8001/swagger/
```

### Test via Python
```bash
# Test public endpoints
python test_apis.py

# Test protected endpoints
python test_apis_with_auth.py
```

### Quick Test Commands

#### 1. Test API Root
```bash
curl http://127.0.0.1:8001/api/v1/
```

#### 2. Test User Signup
```bash
curl -X POST http://127.0.0.1:8001/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "test123456",
    "confirm_password": "test123456",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+254712345678",
    "role": "tenant"
  }'
```

#### 3. Test Login
```bash
curl -X POST http://127.0.0.1:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "api_test@example.com",
    "password": "test123"
  }'
```

#### 4. Test Properties List
```bash
curl http://127.0.0.1:8001/api/v1/properties/
```

#### 5. Test Filter by Type
```bash
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=2"
```

---

## Summary

### Quick Facts

| Feature | Details |
|---------|---------|
| **Total APIs** | 16 endpoints |
| **Public APIs** | 9 (no auth) |
| **Protected APIs** | 7 (JWT auth) |
| **Property Types** | 4 (House, Hotel, Lodge, Venue) |
| **Unified System** | ✅ Same APIs for all types |
| **Filtering** | By `property_type` parameter |
| **Base URL** | http://127.0.0.1:8001/api/v1 |

### Property Type IDs

| ID | Type | Description |
|----|------|-------------|
| 1 | House | Residential rental properties |
| 2 | Hotel | Commercial hotels with rooms |
| 3 | Lodge | Lodge/accommodation facilities |
| 4 | Venue | Event venues and spaces |

### Complete API List

**Public APIs (9):**
1. POST /auth/signup/
2. POST /auth/login/
3. GET /properties/
4. GET /properties/{id}/
5. GET /property-types/
6. GET /regions/
7. GET /amenities/
8. GET /featured/
9. GET /recent/

**Protected APIs (7):**
1. GET /auth/profile/
2. PUT /auth/profile/update/
3. POST /auth/change-password/
4. POST /auth/verify/
5. POST /auth/refresh/
6. POST /auth/logout/
7. POST /search/
8. GET /my-properties/
9. POST /toggle-favorite/
10. GET /favorites/

### Key Points

✅ **Unified System** - Same APIs work for all property types
✅ **Filtering** - Use `property_type` parameter to filter
✅ **Different Fields** - Responses vary by property type
✅ **Flexible** - Browse all or filter by specific type
✅ **Complete** - 16 endpoints cover all tenant needs

---

## Related Documents

- **API_DOCUMENTATION.md** - Original API documentation
- **COMPLETE_API_TEST_SUMMARY.md** - Test results
- **SWAGGER_TESTING_GUIDE.md** - How to use Swagger UI
- **PROPERTY_TYPE_API_GUIDE.md** - Detailed property type guide

---

**This is the complete tenant API documentation. All APIs work for all property types!** 🎉

