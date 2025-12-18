# Documents Module - API Documentation

This document module manages leases, bookings, and document uploads for the Maisha property management system.

## Models

### 1. Lease
Long-term property rental agreements.

**Fields:**
- `property_ref`: Foreign key to Property
- `tenant`: Foreign key to User
- `start_date`: Date
- `end_date`: Date
- `rent_amount`: Decimal(12,2)
- `status`: Choice (active, terminated, expired)
- `created_at`: DateTime (auto)

### 2. Booking
Short-term property reservations (hotels, lodges, venues).

**Fields:**
- `property_ref`: Foreign key to Property
- `tenant`: Foreign key to User
- `check_in`: Date
- `check_out`: Date
- `total_amount`: Decimal(12,2)
- `status`: Choice (pending, confirmed, cancelled, completed)
- `created_at`: DateTime (auto)

### 3. Document
File uploads related to leases, bookings, properties, or users.

**Fields:**
- `lease`: Foreign key to Lease (optional)
- `booking`: Foreign key to Booking (optional)
- `property_ref`: Foreign key to Property (optional)
- `user`: Foreign key to User (optional)
- `file_name`: String(255)
- `file`: FileField
- `uploaded_at`: DateTime (auto)

## API Endpoints (Flutter Integration)

### Authentication
All endpoints require JWT authentication. Include the token in the header:
```
Authorization: Bearer <access_token>
```

### Leases API

#### List Leases
```
GET /api/v1/leases/
```
Returns all leases (filtered by user role).

**Query Parameters:**
- `status`: Filter by status (active, terminated, expired)
- `property_ref`: Filter by property ID
- `search`: Search by property name or tenant

**Response:**
```json
[
  {
    "id": 1,
    "property_ref": 5,
    "property_details": {
      "id": 5,
      "name": "Sunset Apartment",
      "address": "123 Main St"
    },
    "tenant": 3,
    "tenant_details": {
      "id": 3,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "rent_amount": "500000.00",
    "status": "active",
    "created_at": "2024-01-01T10:00:00Z",
    "is_active": true,
    "duration_days": 365
  }
]
```

#### Get My Leases
```
GET /api/v1/leases/my_leases/
```
Returns leases for the current user.

#### Get Active Leases
```
GET /api/v1/leases/active_leases/
```
Returns all active leases.

#### Create Lease
```
POST /api/v1/leases/
```

**Request Body:**
```json
{
  "property_ref": 5,
  "tenant": 3,
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "rent_amount": "500000.00",
  "status": "active"
}
```

#### Get Lease Details
```
GET /api/v1/leases/{id}/
```

#### Update Lease
```
PUT /api/v1/leases/{id}/
PATCH /api/v1/leases/{id}/
```

#### Terminate Lease
```
POST /api/v1/leases/{id}/terminate/
```

#### Delete Lease
```
DELETE /api/v1/leases/{id}/
```

### Bookings API

#### List Bookings
```
GET /api/v1/bookings/
```

**Query Parameters:**
- `status`: Filter by status (pending, confirmed, cancelled, completed)
- `property_ref`: Filter by property ID
- `search`: Search by property name or tenant

**Response:**
```json
[
  {
    "id": 1,
    "property_ref": 8,
    "property_details": {
      "id": 8,
      "name": "Beach Resort",
      "address": "456 Beach Rd"
    },
    "tenant": 3,
    "tenant_details": {
      "id": 3,
      "username": "john_doe",
      "email": "john@example.com"
    },
    "check_in": "2024-12-20",
    "check_out": "2024-12-25",
    "total_amount": "150000.00",
    "status": "confirmed",
    "created_at": "2024-10-01T10:00:00Z",
    "nights": 5,
    "is_upcoming": true
  }
]
```

#### Get My Bookings
```
GET /api/v1/bookings/my_bookings/
```

#### Get Pending Bookings
```
GET /api/v1/bookings/pending_bookings/
```

#### Create Booking
```
POST /api/v1/bookings/
```

**Request Body:**
```json
{
  "property_ref": 8,
  "tenant": 3,
  "check_in": "2024-12-20",
  "check_out": "2024-12-25",
  "total_amount": "150000.00",
  "status": "pending"
}
```

#### Confirm Booking
```
POST /api/v1/bookings/{id}/confirm/
```

#### Cancel Booking
```
POST /api/v1/bookings/{id}/cancel/
```

### Documents API

#### List Documents
```
GET /api/v1/documents/
```

**Query Parameters:**
- `lease`: Filter by lease ID
- `booking`: Filter by booking ID
- `property_ref`: Filter by property ID
- `user`: Filter by user ID

**Response:**
```json
[
  {
    "id": 1,
    "lease": 1,
    "lease_details": {
      "id": 1,
      "property_details": {"name": "Sunset Apartment"}
    },
    "booking": null,
    "property_ref": null,
    "user": null,
    "file_name": "lease_agreement.pdf",
    "file": "/media/documents/2024/10/01/lease_agreement.pdf",
    "file_url": "http://example.com/media/documents/2024/10/01/lease_agreement.pdf",
    "file_size": 245678,
    "uploaded_at": "2024-10-01T10:00:00Z"
  }
]
```

#### Upload Document
```
POST /api/v1/documents/
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
lease: 1 (optional)
booking: null (optional)
property_ref: null (optional)
user: null (optional)
file_name: "Lease Agreement" (optional, auto-generated from file)
file: <binary file data>
```

**Note:** At least one of (lease, booking, property_ref, user) must be provided.

#### Get My Documents
```
GET /api/v1/documents/my_documents/
```

#### Get Lease Documents
```
GET /api/v1/documents/lease_documents/?lease_id=1
```

#### Get Booking Documents
```
GET /api/v1/documents/booking_documents/?booking_id=1
```

#### Download Document
```
GET /api/v1/documents/{id}/
```

The response includes `file_url` which you can use to download the file.

#### Delete Document
```
DELETE /api/v1/documents/{id}/
```

## Flutter Integration Example

### Setup HTTP Client
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiClient {
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  String? accessToken;
  
  Map<String, String> get headers => {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json',
  };
}
```

### Fetch Leases
```dart
Future<List<Lease>> getMyLeases() async {
  final response = await http.get(
    Uri.parse('$baseUrl/leases/my_leases/'),
    headers: headers,
  );
  
  if (response.statusCode == 200) {
    final List data = json.decode(response.body);
    return data.map((json) => Lease.fromJson(json)).toList();
  } else {
    throw Exception('Failed to load leases');
  }
}
```

### Create Booking
```dart
Future<Booking> createBooking(Booking booking) async {
  final response = await http.post(
    Uri.parse('$baseUrl/bookings/'),
    headers: headers,
    body: json.encode(booking.toJson()),
  );
  
  if (response.statusCode == 201) {
    return Booking.fromJson(json.decode(response.body));
  } else {
    throw Exception('Failed to create booking');
  }
}
```

### Upload Document
```dart
Future<Document> uploadDocument({
  required File file,
  int? leaseId,
  int? bookingId,
  String? fileName,
}) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('$baseUrl/documents/'),
  );
  
  request.headers['Authorization'] = 'Bearer $accessToken';
  
  if (leaseId != null) request.fields['lease'] = leaseId.toString();
  if (bookingId != null) request.fields['booking'] = bookingId.toString();
  if (fileName != null) request.fields['file_name'] = fileName;
  
  request.files.add(await http.MultipartFile.fromPath('file', file.path));
  
  final response = await request.send();
  final responseData = await response.stream.bytesToString();
  
  if (response.statusCode == 201) {
    return Document.fromJson(json.decode(responseData));
  } else {
    throw Exception('Failed to upload document');
  }
}
```

## Web Interface

### URLs
- `/documents/leases/` - List all leases
- `/documents/bookings/` - List all bookings
- `/documents/documents/` - List all documents

### Dashboard Integration
The dashboard now shows:
- Active Leases count
- Pending Bookings count
- Links to lease and booking management

## Permissions

- **Staff/Admin**: Can view and manage all leases, bookings, and documents
- **Tenants**: Can only view/manage their own leases, bookings, and related documents

## Notes

- File uploads are stored in `MEDIA_ROOT/documents/YYYY/MM/DD/`
- Maximum file size is configured in Django settings
- Supported file types: PDF, DOC, DOCX, JPG, PNG (configurable)
- Documents can be related to leases, bookings, properties, or users
- At least one relationship (lease/booking/property/user) is required per document
