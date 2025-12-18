# Mobile App API Documentation for Flutter

## For Tenant/Customer Mobile App

This documentation provides all necessary API endpoints for building a Flutter mobile application where tenants/customers can browse and interact with House, Hotel, Venue, and Lodge properties.

---

## Summary

**Total APIs Available:** 33 endpoints

### Public APIs (No Authentication Required) - 9 Endpoints
- User Signup & Login
- Browse Properties (all types)
- Get Property Details
- Get Featured/Recent Properties
- Property Types, Regions, Amenities

### Protected APIs (JWT Authentication Required) - 24 Endpoints
- User Profile Management
- Property Search
- Favorites Management
- **Rent Management** (Invoices, Payments, Late Fees, Reminders)
- **Payment System** (Providers, Invoices/Receipts, Payment History, Transactions, Expenses)
- **Maintenance Requests** (List, Create, Update)

### Supported Property Types
All APIs support: **House (1), Hotel (2), Lodge (3), Venue (4)**

### Base URL
```
http://127.0.0.1:8001/api/v1
```

### Authentication
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <access_token>`
- **Token Storage**: SharedPreferences (recommended)

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Base Configuration](#base-configuration)
3. [Authentication APIs](#authentication-apis)
4. [Property Browsing APIs](#property-browsing-apis)
5. [Property Details & Search](#property-details--search)
6. [User Profile APIs](#user-profile-apis)
7. [Favorites APIs](#favorites-apis)
8. [Rent Management APIs](#rent-management-apis)
9. [Payment APIs](#payment-apis)
10. [Maintenance Request APIs](#maintenance-request-apis)
11. [Property Types](#property-types)
12. [Dart Implementation Examples](#dart-implementation-examples)
13. [Complete API Reference](#complete-api-reference)

---

## Getting Started

### Base URL
```
http://127.0.0.1:8001/api/v1
```

### Important Notes
- ✅ All APIs work for ALL property types (House, Hotel, Venue, Lodge)
- ✅ Use `property_type` parameter to filter by type
- ✅ JWT authentication required for protected endpoints
- ✅ Include JWT token in header: `Authorization: Bearer <token>`

### Property Type IDs
```dart
enum PropertyType {
  house(1),
  hotel(2),
  lodge(3),
  venue(4);
  
  final int id;
  const PropertyType(this.id);
}
```

---

## Base Configuration

### Add to your pubspec.yaml
```yaml
dependencies:
  http: ^1.1.0
  shared_preferences: ^2.2.0
```

### API Service Setup
```dart
class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8001/api/v1';
  static String? accessToken;
  
  // Get headers with authentication
  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    if (accessToken != null) 'Authorization': 'Bearer $accessToken',
  };
  
  // Helper method for GET requests
  static Future<Map<String, dynamic>> get(String endpoint) async {
    final response = await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
    return jsonDecode(response.body);
  }
  
  // Helper method for POST requests
  static Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> data,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: jsonEncode(data),
    );
    return jsonDecode(response.body);
  }
}
```

---

## Authentication APIs

### 1. User Signup
**Endpoint:** `POST /auth/signup/`  
**Auth Required:** ❌ No  
**Description:** Register a new tenant account

**Request:**
```dart
Future<Map<String, dynamic>> signup({
  required String username,
  required String email,
  required String password,
  required String confirmPassword,
  required String firstName,
  required String lastName,
  String? phone,
}) async {
  return await ApiService.post('/auth/signup/', {
    'username': username,
    'email': email,
    'password': password,
    'confirm_password': confirmPassword,
    'first_name': firstName,
    'last_name': lastName,
    'phone': phone,
    'role': 'tenant',
  });
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully. Your account is pending admin approval.",
  "user": {
    "id": 1,
    "username": "tenant_user",
    "email": "tenant@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": ["Tenant"],
    "date_joined": "2025-10-27T17:00:00Z"
  },
  "status": "pending_approval"
}
```

### 2. User Login
**Endpoint:** `POST /auth/login/`  
**Auth Required:** ❌ No  
**Description:** Login and get JWT tokens

**Request:**
```dart
Future<Map<String, dynamic>> login(String email, String password) async {
  final response = await ApiService.post('/auth/login/', {
    'email': email,
    'password': password,
  });
  
  // Store tokens
  if (response['success'] == true && response['tokens'] != null) {
    ApiService.accessToken = response['tokens']['access'];
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', response['tokens']['access']);
    await prefs.setString('refresh_token', response['tokens']['refresh']);
  }
  
  return response;
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "tenant_user",
    "email": "tenant@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "role": ["Tenant"]
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 3. Get User Profile
**Endpoint:** `GET /auth/profile/`  
**Auth Required:** ✅ Yes  
**Description:** Get current user's profile

```dart
Future<Map<String, dynamic>> getProfile() async {
  return await ApiService.get('/auth/profile/');
}
```

---

## Property Browsing APIs

### 1. List All Properties (All Types)
**Endpoint:** `GET /properties/`  
**Auth Required:** ❌ No  
**Description:** Get all available properties (House, Hotel, Lodge, Venue)

**Request with Filters:**
```dart
Future<Map<String, dynamic>> getProperties({
  PropertyType? propertyType,
  String? search,
  double? minRent,
  double? maxRent,
  int? bedrooms,
  int? bathrooms,
  int? regionId,
  int? page,
}) async {
  final queryParams = <String, String>{};
  
  if (propertyType != null) {
    queryParams['property_type'] = propertyType.id.toString();
  }
  if (search != null) queryParams['search'] = search;
  if (minRent != null) queryParams['min_rent'] = minRent.toString();
  if (maxRent != null) queryParams['max_rent'] = maxRent.toString();
  if (bedrooms != null) queryParams['bedrooms'] = bedrooms.toString();
  if (bathrooms != null) queryParams['bathrooms'] = bathrooms.toString();
  if (regionId != null) queryParams['region'] = regionId.toString();
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/properties/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  return await ApiService.get(endpoint);
}
```

**Response:**
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8001/api/v1/properties/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Modern 3BR House",
      "property_type": {"id": 1, "name": "House"},
      "bedrooms": 3,
      "bathrooms": 2,
      "rent_amount": "1200.00",
      "address": "123 Main Street",
      "region": {"id": 1, "name": "Downtown"},
      "images": [...]
    },
    {
      "id": 2,
      "title": "Beachfront Hotel",
      "property_type": {"id": 2, "name": "Hotel"},
      "total_rooms": 50,
      "room_types": {"standard": 20, "deluxe": 20, "suite": 10},
      "base_rate": "80.00",
      "images": [...]
    }
  ]
}
```

### 2. Get Property Details
**Endpoint:** `GET /properties/{id}/`  
**Auth Required:** ❌ No  
**Description:** Get detailed information about a specific property

```dart
Future<Map<String, dynamic>> getPropertyDetails(int propertyId) async {
  return await ApiService.get('/properties/$propertyId/');
}
```

**Response varies by property type:**

**For House:**
```json
{
  "id": 1,
  "title": "Modern 3BR House",
  "description": "Beautiful modern house...",
  "property_type": {"id": 1, "name": "House"},
  "bedrooms": 3,
  "bathrooms": 2,
  "size_sqft": 1500,
  "rent_amount": "1200.00",
  "address": "123 Main Street",
  "amenities": [...],
  "images": [...]
}
```

**For Hotel:**
```json
{
  "id": 2,
  "title": "Beachfront Hotel",
  "description": "Luxury hotel...",
  "property_type": {"id": 2, "name": "Hotel"},
  "total_rooms": 50,
  "room_types": {
    "standard": 20,
    "deluxe": 20,
    "suite": 10
  },
  "base_rate": "80.00",
  "images": [...]
}
```

**For Venue:**
```json
{
  "id": 3,
  "title": "Conference Hall",
  "description": "Large conference venue...",
  "property_type": {"id": 4, "name": "Venue"},
  "capacity": 500,
  "venue_type": "Conference",
  "rent_amount": "5000.00",
  "images": [...]
}
```

### 3. Featured Properties
**Endpoint:** `GET /featured/`  
**Auth Required:** ❌ No  
**Description:** Get featured properties

```dart
Future<List<dynamic>> getFeaturedProperties() async {
  final response = await ApiService.get('/featured/');
  return response['results'] as List;
}
```

### 4. Recent Properties
**Endpoint:** `GET /recent/`  
**Auth Required:** ❌ No  
**Description:** Get recently added properties

```dart
Future<List<dynamic>> getRecentProperties() async {
  final response = await ApiService.get('/recent/');
  return response['results'] as List;
}
```

---

## Property Details & Search

### 1. Advanced Search (All Property Types)
**Endpoint:** `POST /search/`  
**Auth Required:** ✅ Yes  
**Description:** Advanced search across all property types

```dart
Future<Map<String, dynamic>> searchProperties({
  String? query,
  List<int>? propertyTypes, // [1, 2, 3, 4] for House, Hotel, Lodge, Venue
  double? minRent,
  double? maxRent,
  List<int>? bedrooms,
  List<int>? amenities,
  List<int>? regions,
}) async {
  return await ApiService.post('/search/', {
    if (query != null) 'query': query,
    'filters': {
      if (propertyTypes != null) 'property_types': propertyTypes,
      if (minRent != null || maxRent != null)
        'rent_range': {
          if (minRent != null) 'min': minRent,
          if (maxRent != null) 'max': maxRent,
        },
      if (bedrooms != null) 'bedrooms': bedrooms,
      if (amenities != null) 'amenities': amenities,
      if (regions != null) 'regions': regions,
    }
  });
}
```

**Request Example:**
```dart
// Search for Hotel and Venue with specific rent range
await searchProperties(
  query: 'beach',
  propertyTypes: [2, 4], // Hotel and Venue
  minRent: 50,
  maxRent: 500,
);
```

---

## User Profile APIs

### 1. Update Profile
**Endpoint:** `PUT /auth/profile/update/`  
**Auth Required:** ✅ Yes

```dart
Future<Map<String, dynamic>> updateProfile({
  String? firstName,
  String? lastName,
  String? phone,
}) async {
  return await ApiService.post('/auth/profile/update/', {
    if (firstName != null) 'first_name': firstName,
    if (lastName != null) 'last_name': lastName,
    if (phone != null) 'phone': phone,
  });
}
```

### 2. Change Password
**Endpoint:** `POST /auth/change-password/`  
**Auth Required:** ✅ Yes

```dart
Future<Map<String, dynamic>> changePassword({
  required String currentPassword,
  required String newPassword,
  required String confirmPassword,
}) async {
  return await ApiService.post('/auth/change-password/', {
    'current_password': currentPassword,
    'new_password': newPassword,
    'confirm_password': confirmPassword,
  });
}
```

---

## Favorites APIs

### 1. Toggle Favorite
**Endpoint:** `POST /toggle-favorite/`  
**Auth Required:** ✅ Yes  
**Description:** Add or remove property from favorites

```dart
Future<bool> toggleFavorite(int propertyId) async {
  final response = await ApiService.post('/toggle-favorite/', {
    'property_id': propertyId,
  });
  return response['is_favorite'] as bool;
}
```

### 2. Get Favorite Properties (All Types)
**Endpoint:** `GET /favorites/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getFavoriteProperties() async {
  final response = await ApiService.get('/favorites/');
  return response['results'] as List;
}
```

---

## Property Types

### Get Property Types
**Endpoint:** `GET /property-types/`  
**Auth Required:** ❌ No

```dart
Future<List<dynamic>> getPropertyTypes() async {
  final response = await ApiService.get('/property-types/');
  return response as List;
}
```

**Response:**
```json
[
  {"id": 1, "name": "House"},
  {"id": 2, "name": "Hotel"},
  {"id": 3, "name": "Lodge"},
  {"id": 4, "name": "Venue"}
]
```

### Get Regions
**Endpoint:** `GET /regions/`

```dart
Future<List<dynamic>> getRegions() async {
  final response = await ApiService.get('/regions/');
  return response as List;
}
```

### Get Amenities
**Endpoint:** `GET /amenities/`

```dart
Future<List<dynamic>> getAmenities() async {
  final response = await ApiService.get('/amenities/');
  return response as List;
}
```

---

## Dart Implementation Examples

### Property Model
```dart
class Property {
  final int id;
  final String title;
  final String description;
  final PropertyTypeInfo propertyType;
  final double rentAmount;
  final String address;
  final RegionInfo region;
  final List<String> images;
  
  // House-specific fields
  final int? bedrooms;
  final int? bathrooms;
  final int? sizeSqft;
  
  // Hotel/Lodge-specific fields
  final int? totalRooms;
  final Map<String, int>? roomTypes;
  final double? baseRate;
  
  // Venue-specific fields
  final int? capacity;
  final String? venueType;
  
  Property.fromJson(Map<String, dynamic> json)
    : id = json['id'],
      title = json['title'],
      description = json['description'],
      propertyType = PropertyTypeInfo.fromJson(json['property_type']),
      rentAmount = double.parse(json['rent_amount']),
      address = json['address'],
      region = RegionInfo.fromJson(json['region']),
      images = List<String>.from(json['images']?.map((img) => img['image']) ?? []),
      bedrooms = json['bedrooms'],
      bathrooms = json['bathrooms'],
      sizeSqft = json['size_sqft'],
      totalRooms = json['total_rooms'],
      roomTypes = json['room_types'] != null 
          ? Map<String, int>.from(json['room_types']) 
          : null,
      baseRate = json['base_rate'] != null ? double.parse(json['base_rate']) : null,
      capacity = json['capacity'],
      venueType = json['venue_type'];
  
  bool get isHouse => propertyType.id == 1;
  bool get isHotel => propertyType.id == 2;
  bool get isLodge => propertyType.id == 3;
  bool get isVenue => propertyType.id == 4;
}

class PropertyTypeInfo {
  final int id;
  final String name;
  
  PropertyTypeInfo.fromJson(Map<String, dynamic> json)
    : id = json['id'],
      name = json['name'];
}

class RegionInfo {
  final int id;
  final String name;
  
  RegionInfo.fromJson(Map<String, dynamic> json)
    : id = json['id'],
      name = json['name'];
}
```

### Usage Example in Widget
```dart
class PropertyListScreen extends StatefulWidget {
  @override
  _PropertyListScreenState createState() => _PropertyListScreenState();
}

class _PropertyListScreenState extends State<PropertyListScreen> {
  List<Property> properties = [];
  PropertyType? selectedType;
  bool isLoading = false;
  
  @override
  void initState() {
    super.initState();
    loadProperties();
  }
  
  Future<void> loadProperties() async {
    setState(() => isLoading = true);
    try {
      final response = await ApiService.getProperties(
        propertyType: selectedType,
      );
      setState(() {
        properties = (response['results'] as List)
            .map((json) => Property.fromJson(json))
            .toList();
      });
    } catch (e) {
      print('Error loading properties: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Properties')),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: properties.length,
              itemBuilder: (context, index) {
                final property = properties[index];
                return PropertyCard(property: property);
              },
            ),
    );
  }
}
```

---

## Rent Management APIs

### 1. Get Rent Invoices
**Endpoint:** `GET /rent/invoices/`  
**Auth Required:** ✅ Yes  
**Description:** Get all rent invoices for the tenant

```dart
Future<List<dynamic>> getRentInvoices({
  String? status,
  int? page,
}) async {
  final queryParams = <String, String>{};
  if (status != null) queryParams['status'] = status;
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/rent/invoices/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

### 2. Get Rent Payments
**Endpoint:** `GET /rent/payments/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getRentPayments({
  int? invoiceId,
  String? dateFrom,
  String? dateTo,
}) async {
  final queryParams = <String, String>{};
  if (invoiceId != null) queryParams['invoice_id'] = invoiceId.toString();
  if (dateFrom != null) queryParams['date_from'] = dateFrom;
  if (dateTo != null) queryParams['date_to'] = dateTo;
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/rent/payments/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

### 3. Get Late Fees
**Endpoint:** `GET /rent/late-fees/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getLateFees() async {
  final response = await ApiService.get('/rent/late-fees/');
  return response['results'] as List;
}
```

### 4. Get Rent Reminders
**Endpoint:** `GET /rent/reminders/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getRentReminders({bool? upcoming}) async {
  final endpoint = upcoming == true 
    ? '/rent/reminders/?upcoming=true' 
    : '/rent/reminders/';
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

---

## Payment APIs

### 1. Get Payment Providers
**Endpoint:** `GET /payments/providers/`  
**Auth Required:** ✅ Yes  
**Description:** Get available payment methods (M-Pesa, Airtel Money, etc.)

```dart
Future<List<dynamic>> getPaymentProviders() async {
  final response = await ApiService.get('/payments/providers/');
  return response['results'] as List;
}
```

**Response:**
```json
[
  {"id": 1, "name": "M-Pesa"},
  {"id": 2, "name": "Airtel Money"},
  {"id": 3, "name": "Tigo Pesa"},
  {"id": 4, "name": "Bank Transfer"},
  {"id": 5, "name": "Cash"}
]
```

### 2. Get Invoices (Payment Receipts)
**Endpoint:** `GET /payments/invoices/`  
**Auth Required:** ✅ Yes  
**Description:** Get all invoices/receipts

```dart
Future<List<dynamic>> getInvoices({
  String? status,
  int? propertyId,
  int? page,
}) async {
  final queryParams = <String, String>{};
  if (status != null) queryParams['status'] = status;
  if (propertyId != null) queryParams['property_id'] = propertyId.toString();
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/payments/invoices/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

### 3. Get Invoice Details (Receipt)
**Endpoint:** `GET /payments/invoices/{id}/`  
**Auth Required:** ✅ Yes  
**Description:** Get detailed invoice/receipt

```dart
Future<Map<String, dynamic>> getInvoiceDetails(int invoiceId) async {
  return await ApiService.get('/payments/invoices/$invoiceId/');
}
```

### 4. Get Payment History
**Endpoint:** `GET /payments/payments/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getPaymentHistory({
  int? invoiceId,
  int? provider,
  int? page,
}) async {
  final queryParams = <String, String>{};
  if (invoiceId != null) queryParams['invoice_id'] = invoiceId.toString();
  if (provider != null) queryParams['provider'] = provider.toString();
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/payments/payments/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

### 5. Get Payment Details (Receipt)
**Endpoint:** `GET /payments/payments/{id}/`  
**Auth Required:** ✅ Yes

```dart
Future<Map<String, dynamic>> getPaymentDetails(int paymentId) async {
  return await ApiService.get('/payments/payments/$paymentId/');
}
```

### 6. Get Transactions
**Endpoint:** `GET /payments/transactions/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getTransactions({
  String? status,
  String? dateFrom,
  String? dateTo,
  int? page,
}) async {
  final queryParams = <String, String>{};
  if (status != null) queryParams['status'] = status;
  if (dateFrom != null) queryParams['date_from'] = dateFrom;
  if (dateTo != null) queryParams['date_to'] = dateTo;
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/payments/transactions/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

### 7. Get Expenses
**Endpoint:** `GET /payments/expenses/`  
**Auth Required:** ✅ Yes

```dart
Future<List<dynamic>> getExpenses({
  String? category,
  String? dateFrom,
  String? dateTo,
  int? page,
}) async {
  final queryParams = <String, String>{};
  if (category != null) queryParams['category'] = category;
  if (dateFrom != null) queryParams['date_from'] = dateFrom;
  if (dateTo != null) queryParams['date_to'] = dateTo;
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/payments/expenses/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

---

## Maintenance Request APIs

### 1. Get Maintenance Requests
**Endpoint:** `GET /maintenance/requests/`  
**Auth Required:** ✅ Yes  
**Description:** Get all maintenance requests submitted by tenant

```dart
Future<List<dynamic>> getMaintenanceRequests({
  String? status,
  String? priority,
  int? propertyId,
  int? page,
}) async {
  final queryParams = <String, String>{};
  if (status != null) queryParams['status'] = status;
  if (priority != null) queryParams['priority'] = priority;
  if (propertyId != null) queryParams['property_id'] = propertyId.toString();
  if (page != null) queryParams['page'] = page.toString();
  
  final queryString = Uri(queryParameters: queryParams).query;
  final endpoint = '/maintenance/requests/${queryString.isNotEmpty ? '?$queryString' : ''}';
  
  final response = await ApiService.get(endpoint);
  return response['results'] as List;
}
```

### 2. Get Maintenance Request Details
**Endpoint:** `GET /maintenance/requests/{id}/`  
**Auth Required:** ✅ Yes

```dart
Future<Map<String, dynamic>> getMaintenanceRequestDetails(int requestId) async {
  return await ApiService.get('/maintenance/requests/$requestId/');
}
```

### 3. Create Maintenance Request
**Endpoint:** `POST /maintenance/requests/`  
**Auth Required:** ✅ Yes

```dart
Future<Map<String, dynamic>> createMaintenanceRequest({
  required int propertyId,
  required String title,
  required String description,
  required String priority,
  String? category,
  List<String>? photoUrls,
}) async {
  return await ApiService.post('/maintenance/requests/', {
    'property_id': propertyId,
    'title': title,
    'description': description,
    'priority': priority,
    if (category != null) 'category': category,
    if (photoUrls != null) 'photos': photoUrls,
  });
}
```

### 4. Update Maintenance Request
**Endpoint:** `PUT /maintenance/requests/{id}/`  
**Auth Required:** ✅ Yes

```dart
Future<Map<String, dynamic>> updateMaintenanceRequest(
  int requestId,
  Map<String, dynamic> updates,
) async {
  return await ApiService.post('/maintenance/requests/$requestId/', updates);
}
```

---

## Complete API Reference

### Authentication Endpoints (Public)
1. ✅ `POST /auth/signup/` - User registration
2. ✅ `POST /auth/login/` - User login

### Authentication Endpoints (Protected)
3. ✅ `GET /auth/profile/` - Get profile
4. ✅ `PUT /auth/profile/update/` - Update profile
5. ✅ `POST /auth/change-password/` - Change password
6. ✅ `POST /auth/verify/` - Verify token
7. ✅ `POST /auth/refresh/` - Refresh token
8. ✅ `POST /auth/logout/` - Logout

### Property Browsing Endpoints (Public)
9. ✅ `GET /properties/` - List all properties (filterable by type)
10. ✅ `GET /properties/{id}/` - Get property details
11. ✅ `GET /featured/` - Featured properties
12. ✅ `GET /recent/` - Recent properties

### Property Search Endpoints (Protected)
13. ✅ `POST /search/` - Advanced search

### Property Interaction (Protected)
14. ✅ `GET /favorites/` - Get favorite properties
15. ✅ `POST /toggle-favorite/` - Toggle favorite

### Metadata Endpoints (Public)
16. ✅ `GET /property-types/` - List property types
17. ✅ `GET /regions/` - List regions
18. ✅ `GET /amenities/` - List amenities

### Rent Management APIs (Protected)
19. ✅ `GET /rent/invoices/` - List rent invoices
20. ✅ `GET /rent/payments/` - List rent payments
21. ✅ `GET /rent/late-fees/` - List late fees
22. ✅ `GET /rent/reminders/` - List rent reminders

### Payment APIs (Protected)
23. ✅ `GET /payments/providers/` - List payment providers
24. ✅ `GET /payments/invoices/` - List invoices/receipts
25. ✅ `GET /payments/invoices/{id}/` - Get invoice/receipt details
26. ✅ `GET /payments/payments/` - List payment history
27. ✅ `GET /payments/payments/{id}/` - Get payment details
28. ✅ `GET /payments/transactions/` - List transactions
29. ✅ `GET /payments/expenses/` - List expenses

### Maintenance APIs (Protected)
30. ✅ `GET /maintenance/requests/` - List maintenance requests
31. ✅ `GET /maintenance/requests/{id}/` - Get request details
32. ✅ `POST /maintenance/requests/` - Create maintenance request
33. ✅ `PUT /maintenance/requests/{id}/` - Update maintenance request

---

## Quick Integration Checklist

- [ ] Add http and shared_preferences dependencies
- [ ] Create ApiService class with base URL
- [ ] Implement login/signup screens
- [ ] Implement property listing with filters
- [ ] Implement property details screen
- [ ] Handle different property types (House, Hotel, Lodge, Venue)
- [ ] Implement favorites functionality
- [ ] Add search functionality
- [ ] Implement user profile screen
- [ ] Test with all property types

---

## Testing

### Test Credentials
```
Email: api_test@example.com
Password: test123
```

### Test Base URL
```
http://127.0.0.1:8001
```

### Access Swagger UI
```
http://127.0.0.1:8001/swagger/
```

---

## Property Type Filtering

### Example: Get Only Hotels
```dart
await getProperties(propertyType: PropertyType.hotel);
```

### Example: Get Only Venues
```dart
await getProperties(propertyType: PropertyType.venue);
```

### Example: Get All Types
```dart
await getProperties(); // propertyType: null
```

---

## Important Notes

1. ✅ **All APIs work for ALL property types** - Use the same endpoints
2. ✅ **Filter by property_type** - Pass property type ID to filter
3. ✅ **Different response fields** - Based on property type (house has bedrooms, hotel has rooms, venue has capacity)
4. ✅ **JWT Authentication** - Required for protected endpoints
5. ✅ **Token Storage** - Use SharedPreferences to store tokens
6. ✅ **Pagination** - Use the `page` parameter for paginated results

---

**This documentation is complete and ready for Flutter mobile app development!** 🎉

