# Regions and Districts Filtering API - Mobile App

## Overview
The mobile app API now supports filtering properties by region and district. This document explains how to use these filters.

## API Endpoints

### 1. Get All Regions
**Endpoint:** `GET /api/v1/regions/`

**Description:** Get list of all regions. Use this to get region IDs for filtering.

**Parameters:**
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of results per page

**Response:**
```json
[
  {
    "id": 1,
    "name": "Dar es Salaam",
    "description": "Commercial capital",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "Arusha",
    "description": "Tourism hub",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

**Example:**
```bash
GET /api/v1/regions/
```

---

### 2. Get Districts (Filtered by Region)
**Endpoint:** `GET /api/v1/districts/`

**Description:** Get list of districts. Can be filtered by region(s).

**Parameters:**
- `regions` (optional): Filter by region ID(s). Can be:
  - Single ID: `regions=1`
  - Multiple IDs (comma-separated): `regions=1,2,3`
- `region_id` (optional): Filter by single region ID (backward compatible)
- `page` (optional): Page number for pagination

**Response:**
```json
[
  {
    "id": 1,
    "name": "Kinondoni",
    "region": 1,
    "region_name": "Dar es Salaam",
    "description": "Northern district",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "Ilala",
    "region": 1,
    "region_name": "Dar es Salaam",
    "description": "Central district",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

**Examples:**
```bash
# Get all districts
GET /api/v1/districts/

# Get districts for region ID 1
GET /api/v1/districts/?regions=1

# Get districts for multiple regions
GET /api/v1/districts/?regions=1,2

# Backward compatible (single region)
GET /api/v1/districts/?region_id=1
```

---

### 3. Filter Properties by Region and District
**Endpoint:** `GET /api/v1/properties/`

**Description:** Get list of properties with filtering support. Can filter by region and/or district.

**Parameters:**
- `region` (optional): Filter by region ID
- `district` (optional): Filter by district ID (can be used with or without region)
- `property_type` (optional): Filter by property type ID
- `search` (optional): Search in title, description, address
- `bedrooms` (optional): Exact number of bedrooms
- `bedrooms__gte` (optional): Minimum bedrooms
- `bedrooms__lte` (optional): Maximum bedrooms
- `rent_amount__gte` (optional): Minimum rent
- `rent_amount__lte` (optional): Maximum rent
- `is_furnished` (optional): Filter furnished properties
- `pets_allowed` (optional): Filter pet-friendly properties
- `status` (optional): Filter by status
- `page` (optional): Page number
- `page_size` (optional): Results per page (max 100)

**Examples:**
```bash
# Get all properties
GET /api/v1/properties/

# Filter by region only
GET /api/v1/properties/?region=1

# Filter by district only
GET /api/v1/properties/?district=5

# Filter by both region and district
GET /api/v1/properties/?region=1&district=5

# Combined filters
GET /api/v1/properties/?region=1&district=5&bedrooms__gte=2&rent_amount__lte=50000
```

**Response:**
```json
{
  "count": 100,
  "next": "http://api/v1/properties/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Modern Apartment",
      "region": 1,
      "district": 5,
      "rent_amount": "45000.00",
      ...
    }
  ]
}
```

---

## Mobile App Usage Flow

### Step 1: Load Regions
```dart
// Get all regions
GET /api/v1/regions/
// Display in dropdown/picker
```

### Step 2: Load Districts (when region selected)
```dart
// When user selects a region (e.g., region_id = 1)
GET /api/v1/districts/?regions=1
// Display districts for selected region
```

### Step 3: Filter Properties
```dart
// Option 1: Filter by region only
GET /api/v1/properties/?region=1

// Option 2: Filter by district only
GET /api/v1/properties/?district=5

// Option 3: Filter by both (recommended for better UX)
GET /api/v1/properties/?region=1&district=5
```

---

## Implementation Status

### ✅ Completed
1. **Regions API** (`/api/v1/regions/`)
   - ✅ List all regions
   - ✅ Swagger documentation added
   - ✅ Pagination support

2. **Districts API** (`/api/v1/districts/`)
   - ✅ List all districts
   - ✅ Filter by region (single or multiple)
   - ✅ Swagger documentation
   - ✅ Pagination support
   - ✅ Backward compatible with `region_id` parameter

3. **Properties API** (`/api/v1/properties/`)
   - ✅ Filter by region
   - ✅ Filter by district (NEW)
   - ✅ Combined filtering (region + district)
   - ✅ Swagger documentation updated
   - ✅ All other filters still work

---

## API Changes Made

### 1. Added District Filter to Properties API
**File:** `properties/api_views.py`

**Changes:**
- Added `'district': ['exact']` to `filterset_fields`
- Added `district` parameter to Swagger documentation
- Updated operation description to mention region/district filtering

### 2. Added Swagger Documentation for Regions API
**File:** `properties/api_views.py`

**Changes:**
- Added `@swagger_auto_schema` decorator to `RegionListAPIView.get()`
- Documented pagination parameters
- Added proper response schema

### 3. Districts API Already Had Filtering
**Status:** ✅ Already implemented
- Supports `regions` parameter (comma-separated or single)
- Supports `region_id` parameter (backward compatible)
- Has Swagger documentation

---

## Testing

### Test Regions API:
```bash
curl -X GET "http://localhost:8000/api/v1/regions/"
```

### Test Districts Filtering:
```bash
# All districts
curl -X GET "http://localhost:8000/api/v1/districts/"

# Districts for region 1
curl -X GET "http://localhost:8000/api/v1/districts/?regions=1"

# Districts for multiple regions
curl -X GET "http://localhost:8000/api/v1/districts/?regions=1,2"
```

### Test Property Filtering:
```bash
# By region
curl -X GET "http://localhost:8000/api/v1/properties/?region=1"

# By district
curl -X GET "http://localhost:8000/api/v1/properties/?district=5"

# By both
curl -X GET "http://localhost:8000/api/v1/properties/?region=1&district=5"
```

---

## Summary

✅ **All APIs Updated:**
- Regions API: Swagger documentation added
- Districts API: Already had filtering (no changes needed)
- Properties API: District filter added and documented

✅ **Mobile App Can Now:**
1. Load all regions
2. Load districts filtered by selected region
3. Filter properties by region
4. Filter properties by district
5. Filter properties by both region and district

The API is now fully ready for region and district filtering on the mobile app! 🎉

