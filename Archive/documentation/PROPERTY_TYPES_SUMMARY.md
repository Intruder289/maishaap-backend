# Property Types API - Quick Answer

## Your Question
> "A user/tenant can wish for any of these (house, hotel, lodge or venue) so do we have both public and protect APIs?"

## ✅ YES! Same APIs for All Property Types

A tenant can access **house, hotel, lodge, AND venue** using the **same unified API system**.

---

## 🎯 How It Works

### ONE API System for ALL Types

```
┌─────────────────────────────────────────┐
│  API Endpoints (Same for All Types)    │
├─────────────────────────────────────────┤
│  GET  /api/v1/properties/              │  ← Houses ✅
│  GET  /api/v1/properties/{id}/         │  ← Hotels ✅
│  POST /api/v1/search/                  │  ← Lodges ✅
│  GET  /api/v1/featured/                │  ← Venues ✅
│  GET  /api/v1/recent/                  │  ← All Types ✅
│  GET  /api/v1/favorites/               │  ← All Types ✅
└─────────────────────────────────────────┘
```

### Filter by Property Type

Use the `property_type` parameter to filter:

```bash
# Get all types
GET /api/v1/properties/

# Get only houses
GET /api/v1/properties/?property_type=1

# Get only hotels
GET /api/v1/properties/?property_type=2

# Get only lodges
GET /api/v1/properties/?property_type=3

# Get only venues
GET /api/v1/properties/?property_type=4
```

---

## 📊 API Categories

### 🔓 Public APIs (No Auth Required) - 9 Endpoints

| Endpoint | Works For |
|----------|-----------|
| `GET /properties/` | ✅ All types |
| `GET /properties/{id}/` | ✅ All types |
| `GET /property-types/` | ✅ Lists all types |
| `GET /regions/` | ✅ All locations |
| `GET /amenities/` | ✅ All amenities |
| `GET /featured/` | ✅ All types |
| `GET /recent/` | ✅ All types |
| `POST /auth/signup/` | ✅ User signup |
| `POST /auth/login/` | ✅ User login |

### 🔒 Protected APIs (Auth Required) - 7 Endpoints

| Endpoint | Works For |
|----------|-----------|
| `POST /search/` | ✅ All types |
| `GET /my-properties/` | ✅ All types |
| `POST /toggle-favorite/` | ✅ All types |
| `GET /favorites/` | ✅ All types |
| `GET /auth/profile/` | ✅ User data |
| `PUT /auth/profile/update/` | ✅ Update profile |
| `POST /auth/change-password/` | ✅ Change password |

---

## 🏠 Property Types Breakdown

### 1. House
- **Fields**: bedrooms, bathrooms, size_sqft
- **Use Case**: Residential rental
- **Example**: 3BR apartment

### 2. Hotel
- **Fields**: total_rooms, room_types, base_rate
- **Use Case**: Hotel accommodation
- **Example**: 50-room beachfront hotel

### 3. Lodge
- **Fields**: total_rooms, room_types, capacity
- **Use Case**: Lodge accommodation
- **Example**: 20-room safari lodge

### 4. Venue
- **Fields**: capacity, venue_type
- **Use Case**: Event spaces
- **Example**: Conference hall for 500

---

## 🔍 Response Examples

### House Response
```json
{
  "id": 1,
  "title": "Modern 3BR House",
  "property_type": {"id": 1, "name": "House"},
  "bedrooms": 3,
  "bathrooms": 2,
  "size_sqft": 1500,
  "rent_amount": "1200.00"
}
```

### Hotel Response
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

### Venue Response
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

---

## ✅ Bottom Line

### Your Question: Are there both public and protected APIs for all types?

**YES! Here's what you have:**

1. ✅ **Public APIs** (9 endpoints) - Work for all 4 types
2. ✅ **Protected APIs** (7 endpoints) - Work for all 4 types
3. ✅ **Same endpoints** - No separate APIs needed
4. ✅ **Filtering** - Use `property_type` parameter
5. ✅ **Different fields** - Response varies by type

### Total APIs Available:
- **Public**: 9 endpoints
- **Protected**: 7 endpoints  
- **Total**: 16 core APIs
- **All work for**: House ✅ Hotel ✅ Lodge ✅ Venue ✅

### Property Type IDs:
- 1 = House
- 2 = Hotel  
- 3 = Lodge
- 4 = Venue

---

## 🎯 Quick Test

```bash
# Test all types together
curl http://127.0.0.1:8001/api/v1/properties/

# Test specific types
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=1"  # Houses
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=2"  # Hotels
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=3"  # Lodges
curl "http://127.0.0.1:8001/api/v1/properties/?property_type=4"  # Venues
```

---

## 📚 Full Documentation

- **PROPERTY_TYPE_API_GUIDE.md** - Complete detailed guide
- **TENANT_API_REFERENCE.md** - All tenant APIs
- **SWAGGER_TESTING_GUIDE.md** - How to test

---

**Summary: One unified API system serves all property types!** 🎉


