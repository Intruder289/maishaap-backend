# 📱 Maisha Backend API Documentation

## 🚀 Flutter App Authentication API

This API is designed specifically for your Flutter mobile application to handle tenant authentication and profile management.

### 🔧 Setup Instructions

1. **Install Required Packages:**
```bash
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.0  
pip install django-cors-headers==4.3.1
```

2. **Run Database Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Tenant Users:**
```bash
python create_users.py
```

4. **Start Server:**
```bash
python manage.py runserver
```

---

## 🌐 Base URL
```
http://127.0.0.1:8000/api/v1/
```

---

## 🔐 Authentication Endpoints

### 1. **User Signup (Tenant or Owner)** 
**POST** `/api/v1/auth/signup/`

Register a new user account as either a tenant or property owner. Account requires admin approval before login.

**Request Body:**
```json
{
    "username": "user_username",
    "email": "user@example.com", 
    "password": "securepassword123",
    "confirm_password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+254712345678",
    "role": "tenant"
}
```

**Role Options:**
- `"tenant"` - Property tenant (default)
- `"owner"` - Property owner

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Account created successfully. Your account is pending admin approval. You will be able to login once approved.",
    "user": {
        "id": 1,
        "username": "user_username",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "role": ["Tenant"],
        "date_joined": "2025-10-01T10:30:00Z"
    },
    "status": "pending_approval"
}
```

**Error Response (400 Bad Request):**
```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "email": ["Email already exists"],
        "password": ["Password too short"]
    }
}
```

---

### 2. **User Login (Tenant or Owner)**
**POST** `/api/v1/auth/login/`

Login with email and password. Only works for approved users.

**Request Body:**
```json
{
    "email": "tenant@example.com",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "tenant_username",
        "email": "tenant@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "role": ["Tenant"],
        "date_joined": "2025-10-01T10:30:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

**Error Response (400 Bad Request - Pending Approval):**
```json
{
    "success": false,
    "message": "Login failed",
    "errors": {
        "non_field_errors": ["Your account is pending admin approval. Please wait for approval before logging in."]
    }
}
```

**Error Response (400 Bad Request - Invalid Credentials):**
```json
{
    "success": false,
    "message": "Login failed",
    "errors": {
        "non_field_errors": ["Invalid email or password"]
    }
}
```

---

### 3. **Logout**
**POST** `/api/v1/auth/logout/`

Logout and blacklist refresh token.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

---

### 4. **Refresh Token**
**POST** `/api/v1/auth/refresh/`

Get new access token using refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 5. **Verify Token**
**GET** `/api/v1/auth/verify/`

Check if access token is valid.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Token is valid",
    "user_id": 1,
    "username": "tenant_username"
}
```

---

## 👤 Profile Management Endpoints

### 6. **Get Profile**
**GET** `/api/v1/auth/profile/`

Get current user profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "user": {
        "id": 1,
        "username": "tenant_username",
        "email": "tenant@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "role": ["Tenant"],
        "date_joined": "2025-10-01T10:30:00Z",
        "phone": "+254712345678"
    }
}
```

---

### 7. **Update Profile**
**PUT** `/api/v1/auth/profile/update/`

Update user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Smith", 
    "phone": "+254712345679"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "user": {
        "id": 1,
        "username": "tenant_username",
        "email": "tenant@example.com",
        "first_name": "John",
        "last_name": "Smith",
        "full_name": "John Smith",
        "role": ["Tenant"],
        "date_joined": "2025-10-01T10:30:00Z",
        "phone": "+254712345679"
    }
}
```

---

### 8. **Change Password**
**POST** `/api/v1/auth/change-password/`

Change user password.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "current_password": "oldpassword123",
    "new_password": "newpassword456",
    "confirm_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Password changed successfully"
}
```

---

## 🔒 Security Features

✅ **JWT Authentication** - Secure token-based authentication  
✅ **Role-Based Access** - Only users with "Tenant" role can access  
✅ **Token Refresh** - Automatic token renewal  
✅ **Token Blacklisting** - Secure logout  
✅ **CORS Support** - Cross-origin requests enabled  
✅ **Input Validation** - Comprehensive data validation  
✅ **Error Handling** - Detailed error responses  

---

## 📱 Flutter Integration Example

### HTTP Service Class
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  
  // Login
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
      }),
    );
    
    return json.decode(response.body);
  }
  
  // Signup
  static Future<Map<String, dynamic>> signup(Map<String, String> userData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signup/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(userData),
    );
    
    return json.decode(response.body);
  }
  
  // Get Profile (with auth header)
  static Future<Map<String, dynamic>> getProfile() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    
    final response = await http.get(
      Uri.parse('$baseUrl/auth/profile/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );
    
    return json.decode(response.body);
  }
}
```

---

## 🔧 Admin Endpoints

### 1. **Get Pending Users**
**GET** `/api/v1/admin/pending-users/`

Get all users waiting for approval (Admin only).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
{
    "success": true,
    "message": "Pending users retrieved successfully",
    "pending_users": [
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+254712345678",
            "role": "tenant",
            "role_display": "Tenant",
            "date_joined": "2025-10-01T10:30:00Z",
            "is_approved": false
        }
    ],
    "count": 1
}
```

### 2. **Approve/Reject User**
**POST** `/api/v1/admin/approve-user/`

Approve or reject a pending user registration (Admin only).

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body (Approve):**
```json
{
    "user_id": 123,
    "action": "approve"
}
```

**Request Body (Reject):**
```json
{
    "user_id": 123,
    "action": "reject"
}
```

**Response (200 OK - Approve):**
```json
{
    "success": true,
    "message": "User newuser has been approved successfully"
}
```

**Response (200 OK - Reject):**
```json
{
    "success": true,
    "message": "User newuser has been rejected and removed from the system"
}
```

---

## 🧪 Testing the API

### Using cURL:

**1. Signup:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+254712345678"
  }'
```

**2. Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**3. Get Profile:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## ⚡ Quick Start Checklist

- [ ] Install required packages (`pip install -r api_requirements.txt`)
- [ ] Run migrations (`python manage.py migrate`)
- [ ] Create sample users (`python create_users.py`)
- [ ] Start server (`python manage.py runserver`)
- [ ] Test signup endpoint
- [ ] Test login endpoint
- [ ] Integrate with Flutter app

Your API is now ready for your Flutter mobile application! 🎉

---

## 🏠 Houses/Properties API Endpoints

The Houses module provides comprehensive property management functionality for both web dashboard and mobile app integration.

### 🌐 Houses Base URL
```
http://127.0.0.1:8000/api/properties/
```

---

## 📋 Properties Endpoints

### 1. **List All Properties** 
**GET** `/api/properties/`

Retrieve paginated list of all available properties with optional filtering.

**Query Parameters:**
- `search` (string): Search in title, description, address
- `region` (integer): Filter by region ID
- `property_type` (integer): Filter by property type ID
- `min_rent` (decimal): Minimum rent amount
- `max_rent` (decimal): Maximum rent amount
- `min_bedrooms` (integer): Minimum number of bedrooms
- `max_bedrooms` (integer): Maximum number of bedrooms
- `min_bathrooms` (integer): Minimum number of bathrooms
- `max_bathrooms` (integer): Maximum number of bathrooms
- `status` (string): Filter by status (available, rented, under_maintenance)
- `is_furnished` (boolean): Filter furnished properties
- `pets_allowed` (boolean): Filter pet-friendly properties
- `utilities_included` (boolean): Filter properties with utilities included
- `page` (integer): Page number for pagination

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/?min_rent=800&max_rent=1500&bedrooms=2&region=1"
```

**Response:**
```json
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/properties/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Modern 2BR Downtown Apartment",
      "description": "Beautiful modern apartment with city views...",
      "rent_amount": "1200.00",
      "deposit_amount": "1200.00",
      "bedrooms": 2,
      "bathrooms": 2,
      "size_sqft": "950.00",
      "address": "123 Main Street, Downtown",
      "latitude": "40.7128",
      "longitude": "-74.0060",
      "status": "available",
      "available_from": "2025-11-01",
      "is_furnished": true,
      "pets_allowed": false,
      "smoking_allowed": false,
      "utilities_included": true,
      "is_featured": true,
      "floor_number": 5,
      "total_floors": 12,
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-01T10:00:00Z",
      "property_type": {
        "id": 1,
        "name": "Apartment",
        "description": "Multi-story residential building"
      },
      "region": {
        "id": 1,
        "name": "Downtown",
        "description": "Central business district"
      },
      "owner": {
        "id": 2,
        "username": "property_owner",
        "email": "owner@example.com",
        "first_name": "John",
        "last_name": "Smith",
        "phone": "+1234567890"
      },
      "images": [
        {
          "id": 1,
          "image": "http://127.0.0.1:8000/media/properties/living_room.jpg",
          "caption": "Spacious Living Room",
          "is_primary": true,
          "uploaded_at": "2025-10-01T10:00:00Z"
        }
      ],
      "amenities": [
        {
          "id": 1,
          "name": "Swimming Pool",
          "description": "Outdoor swimming pool"
        },
        {
          "id": 2,
          "name": "Gym",
          "description": "Fully equipped fitness center"
        }
      ],
      "views_count": 45,
      "favorites_count": 12
    }
  ]
}


```

### 2. **Get Property Details** 
**GET** `/api/properties/{id}/`

Retrieve detailed information about a specific property.

**Example Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/properties/1/
```

**Response:** Same structure as individual property in list response above.

### 3. **Create New Property** 
**POST** `/api/properties/`

Create a new property listing (Owner authentication required).

**Request Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Cozy Studio Apartment",
  "description": "Perfect for young professionals...",
  "rent_amount": 900.00,
  "deposit_amount": 900.00,
  "bedrooms": 1,
  "bathrooms": 1,
  "size_sqft": 600.00,
  "address": "456 Oak Street",
  "latitude": 40.7580,
  "longitude": -73.9855,
  "property_type": 1,
  "region": 2,
  "status": "available",
  "available_from": "2025-11-15",
  "is_furnished": false,
  "pets_allowed": true,
  "smoking_allowed": false,
  "utilities_included": false,
  "floor_number": 3,
  "total_floors": 8,
  "amenities": [1, 3, 5]
}
```

**Response:** Created property details (same structure as GET response).

### 4. **Update Property** 
**PUT** `/api/properties/{id}/`

Update an existing property (Owner authentication required - only own properties).

**Request:** Same structure as POST request.

### 5. **Delete Property** 
**DELETE** `/api/properties/{id}/`

Delete a property listing (Owner authentication required - only own properties).

**Response:** 
```json
{
  "message": "Property deleted successfully"
}
```

---

## 🏷️ Property Metadata Endpoints

### 6. **List Property Types** 
**GET** `/api/properties/property-types/`

Get all available property types.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Apartment",
    "description": "Multi-story residential building"
  },
  {
    "id": 2,
    "name": "House",
    "description": "Single-family detached home"
  },
  {
    "id": 3,
    "name": "Condo",
    "description": "Condominium unit"
  }
]
```

### 7. **List Regions** 
**GET** `/api/properties/regions/`

Get all available regions/locations.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Downtown",
    "description": "Central business district"
  },
  {
    "id": 2,
    "name": "Westside",
    "description": "Residential area west of downtown"
  }
]
```

### 8. **List Amenities** 
**GET** `/api/properties/amenities/`

Get all available amenities.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Swimming Pool",
    "description": "Outdoor swimming pool"
  },
  {
    "id": 2,
    "name": "Gym",
    "description": "Fully equipped fitness center"
  },
  {
    "id": 3,
    "name": "Parking",
    "description": "Dedicated parking space"
  }
]
```

---

## 📸 Property Images Endpoints

### 9. **Upload Property Images** 
**POST** `/api/properties/{id}/images/`

Upload images for a specific property (Owner authentication required).

**Request Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
- `image`: Image file
- `caption`: Image description (optional)
- `is_primary`: Boolean indicating if this is the main image

**Response:**
```json
{
  "id": 5,
  "image": "http://127.0.0.1:8000/media/properties/bedroom_001.jpg",
  "caption": "Master Bedroom",
  "is_primary": false,
  "uploaded_at": "2025-10-01T14:30:00Z"
}
```

### 10. **Delete Property Image** 
**DELETE** `/api/properties/images/{image_id}/`

Delete a specific property image (Owner authentication required).

---

## 👀 Property Interaction Endpoints

### 11. **Track Property View** 
**POST** `/api/properties/{id}/view/`

Track when a user views a property (for analytics).

**Request Body:**
```json
{
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1"
}
```

**Response:**
```json
{
  "message": "View tracked successfully",
  "total_views": 46
}
```

### 12. **Toggle Property Favorite** 
**POST** `/api/properties/{id}/favorite/`

Add or remove property from user's favorites (User authentication required).

**Response:**
```json
{
  "is_favorite": true,
  "message": "Property added to favorites"
}
```

### 13. **Get User Favorites** 
**GET** `/api/properties/favorites/`

Get all properties favorited by the authenticated user.

**Response:** Same structure as property list response.

---

## 🔍 Advanced Search Endpoints

### 14. **Advanced Property Search** 
**POST** `/api/properties/search/`

Perform complex property searches with multiple criteria.

**Request Body:**
```json
{
  "query": "modern apartment downtown",
  "filters": {
    "rent_range": {
      "min": 800,
      "max": 2000
    },
    "bedrooms": [1, 2, 3],
    "regions": [1, 2],
    "amenities": [1, 2, 5],
    "property_features": {
      "is_furnished": true,
      "pets_allowed": true,
      "utilities_included": false
    },
    "availability": {
      "available_from": "2025-11-01",
      "status": "available"
    }
  },
  "sort_by": "rent_amount",
  "sort_order": "asc",
  "page": 1,
  "page_size": 20
}
```

### 15. **Get Properties Near Location** 
**GET** `/api/properties/nearby/`

Find properties within a certain radius of a location.

**Query Parameters:**
- `latitude` (decimal): Center latitude
- `longitude` (decimal): Center longitude  
- `radius` (decimal): Search radius in kilometers (default: 5)
- `limit` (integer): Maximum results (default: 20)

**Example Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/nearby/?latitude=40.7128&longitude=-74.0060&radius=2&limit=10"
```

---

## 📊 Analytics Endpoints

### 16. **Property Statistics** 
**GET** `/api/properties/{id}/stats/`

Get detailed statistics for a specific property (Owner authentication required).

**Response:**
```json
{
  "total_views": 145,
  "favorites_count": 23,
  "daily_views": [
    {"date": "2025-10-01", "views": 12},
    {"date": "2025-10-02", "views": 8}
  ],
  "view_sources": {
    "mobile": 89,
    "web": 56
  },
  "inquiries_count": 15,
  "average_time_on_page": "2:34"
}
```

### 17. **Owner Dashboard Stats** 
**GET** `/api/properties/owner/stats/`

Get overall statistics for all properties owned by authenticated user.

**Response:**
```json
{
  "total_properties": 5,
  "available_properties": 3,
  "rented_properties": 2,
  "total_views": 1250,
  "total_favorites": 89,
  "average_rent": "1150.00",
  "recent_activity": [
    {
      "type": "view",
      "property_id": 1,
      "property_title": "Modern 2BR Downtown Apartment",
      "timestamp": "2025-10-01T15:30:00Z"
    }
  ]
}
```

---

## 🎯 Flutter Integration Examples

### **1. Fetch Properties for Mobile App:**
```dart
// Flutter HTTP request example
Future<List<Property>> fetchProperties({
  double? minRent,
  double? maxRent,
  int? bedrooms,
  String? region,
}) async {
  final queryParams = <String, String>{};
  if (minRent != null) queryParams['min_rent'] = minRent.toString();
  if (maxRent != null) queryParams['max_rent'] = maxRent.toString();
  if (bedrooms != null) queryParams['min_bedrooms'] = bedrooms.toString();
  if (region != null) queryParams['region'] = region;
  
  final uri = Uri.parse('http://127.0.0.1:8000/api/properties/')
      .replace(queryParameters: queryParams);
      
  final response = await http.get(uri);
  
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return (data['results'] as List)
        .map((json) => Property.fromJson(json))
        .toList();
  }
  
  throw Exception('Failed to load properties');
}
```

### **2. Property Detail Screen Integration:**
```dart
// Get property details
Future<Property> getPropertyDetails(int propertyId) async {
  final response = await http.get(
    Uri.parse('http://127.0.0.1:8000/api/properties/$propertyId/')
  );
  
  if (response.statusCode == 200) {
    // Track the view
    http.post(Uri.parse('http://127.0.0.1:8000/api/properties/$propertyId/view/'));
    
    return Property.fromJson(json.decode(response.body));
  }
  
  throw Exception('Failed to load property');
}
```

### **3. Search Implementation:**
```dart
// Advanced search
Future<List<Property>> searchProperties({
  String? query,
  double? minRent,
  double? maxRent,
  List<int>? bedrooms,
  List<int>? amenities,
}) async {
  final searchData = {
    'query': query,
    'filters': {
      'rent_range': {
        'min': minRent,
        'max': maxRent,
      },
      'bedrooms': bedrooms,
      'amenities': amenities,
    }
  };
  
  final response = await http.post(
    Uri.parse('http://127.0.0.1:8000/api/properties/search/'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode(searchData),
  );
  
  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return (data['results'] as List)
        .map((json) => Property.fromJson(json))
        .toList();
  }
  
  throw Exception('Search failed');
}
```

---

## 🔒 Authentication for Houses API

Most property management endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

**Owner Permissions:**
- Create, update, delete own properties
- Upload/delete images for own properties
- View detailed analytics for own properties

**Tenant Permissions:**
- View all available properties
- Search and filter properties
- Track property views
- Add/remove favorites
- View property statistics (limited)

---

## 🧪 Testing Houses API

### **Test Property Listing:**
```bash
curl -X GET http://127.0.0.1:8000/api/properties/
```

### **Test Property Search:**
```bash
curl -X GET "http://127.0.0.1:8000/api/properties/?search=apartment&min_rent=800&max_rent=1500"
```

### **Test Property Creation (with auth):**
```bash
curl -X POST http://127.0.0.1:8000/api/properties/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Property",
    "description": "A test property",
    "rent_amount": 1000,
    "bedrooms": 2,
    "bathrooms": 1,
    "size_sqft": 800,
    "address": "123 Test St",
    "property_type": 1,
    "region": 1
  }'
```

---

## 📱 Complete API Integration Checklist

### Backend Setup:
- [ ] Properties app installed and configured
- [ ] Database migrations completed
- [ ] Sample properties created
- [ ] API endpoints tested with Postman/curl
- [ ] CORS configured for mobile app
- [ ] JWT authentication working

### Mobile App Integration:
- [ ] HTTP client configured in Flutter
- [ ] Property model classes created
- [ ] API service class implemented
- [ ] Property listing screen functional
- [ ] Property detail screen implemented
- [ ] Search and filter functionality added
- [ ] Favorites system integrated
- [ ] Image loading and caching working
- [ ] Error handling implemented
- [ ] Loading states added

Your comprehensive Properties API is now fully documented and ready for Flutter integration! 🏠📱🚀