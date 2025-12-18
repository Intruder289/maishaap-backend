# Complete Tenant API Reference

## Overview
This document lists ALL APIs available to a **Tenant** user - both public (no authentication) and protected (requires JWT token).

---

## 🔐 Authentication & Account Management

### Public Endpoints (No Auth Required)

#### 1. **User Signup**
- **Method**: `POST`
- **Endpoint**: `/api/v1/auth/signup/`
- **Description**: Register a new tenant account
- **Request Body**:
```json
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
- **Response**: Returns user data with pending approval status

#### 2. **User Login**
- **Method**: `POST`
- **Endpoint**: `/api/v1/auth/login/`
- **Description**: Login and get JWT tokens (for approved users only)
- **Request Body**:
```json
{
  "email": "tenant@example.com",
  "password": "securepassword123"
}
```
- **Response**: Returns JWT access & refresh tokens + user data

---

### Protected Endpoints (Auth Required)

#### 3. **Get User Profile**
- **Method**: `GET`
- **Endpoint**: `/api/v1/auth/profile/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get current tenant's profile information
- **Response**: User profile with role, name, email, etc.

#### 4. **Update User Profile**
- **Method**: `PUT`
- **Endpoint**: `/api/v1/auth/profile/update/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Update tenant's profile information
- **Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+254712345679"
}
```

#### 5. **Change Password**
- **Method**: `POST`
- **Endpoint**: `/api/v1/auth/change-password/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Change tenant's password
- **Request Body**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456",
  "confirm_password": "newpassword456"
}
```

#### 6. **Verify Token**
- **Method**: `POST`
- **Endpoint**: `/api/v1/auth/verify/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Verify if JWT token is valid
- **Response**: Token validation status

#### 7. **Refresh Token**
- **Method**: `POST`
- **Endpoint**: `/api/v1/auth/refresh/`
- **Description**: Get new access token using refresh token
- **Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 8. **Logout**
- **Method**: `POST`
- **Endpoint**: `/api/v1/auth/logout/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Logout and blacklist refresh token
- **Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 🏠 Properties

### Public Endpoints (No Auth Required)

#### 9. **List All Properties**
- **Method**: `GET`
- **Endpoint**: `/api/v1/properties/`
- **Description**: Browse all available properties
- **Query Parameters**:
  - `search` - Search in title, description, address
  - `min_rent` - Minimum rent amount
  - `max_rent` - Maximum rent amount
  - `bedrooms` - Number of bedrooms
  - `bathrooms` - Number of bathrooms
  - `region` - Filter by region ID
  - `property_type` - Filter by property type ID
  - `status` - Filter by status (available, rented, under_maintenance)
  - `is_furnished` - Filter furnished properties
  - `pets_allowed` - Filter pet-friendly properties
  - `utilities_included` - Filter properties with utilities included
  - `page` - Page number for pagination
- **Example**: `GET /api/v1/properties/?min_rent=800&max_rent=1500&bedrooms=2`
- **Response**: Paginated list of properties

#### 10. **Get Property Details**
- **Method**: `GET`
- **Endpoint**: `/api/v1/properties/{id}/`
- **Description**: Get detailed information about a specific property
- **Example**: `GET /api/v1/properties/1/`

#### 11. **List Property Types**
- **Method**: `GET`
- **Endpoint**: `/api/v1/property-types/`
- **Description**: Get all available property types
- **Response**: List of property types (Apartment, House, Condo, etc.)

#### 12. **List Regions**
- **Method**: `GET`
- **Endpoint**: `/api/v1/regions/`
- **Description**: Get all available regions/locations
- **Response**: List of regions

#### 13. **List Amenities**
- **Method**: `GET`
- **Endpoint**: `/api/v1/amenities/`
- **Description**: Get all available amenities
- **Response**: List of amenities (Swimming Pool, Gym, Parking, etc.)

#### 14. **Featured Properties**
- **Method**: `GET`
- **Endpoint**: `/api/v1/featured/`
- **Description**: Get featured properties
- **Response**: List of featured properties

#### 15. **Recent Properties**
- **Method**: `GET`
- **Endpoint**: `/api/v1/recent/`
- **Description**: Get recently added properties
- **Response**: List of recent properties

---

### Protected Endpoints (Auth Required)

#### 16. **Property Search**
- **Method**: `POST`
- **Endpoint**: `/api/v1/search/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Advanced property search
- **Request Body**:
```json
{
  "query": "modern apartment downtown",
  "filters": {
    "rent_range": {
      "min": 800,
      "max": 2000
    },
    "bedrooms": [1, 2, 3],
    "amenities": [1, 2, 5]
  }
}
```

#### 17. **Get My Properties**
- **Method**: `GET`
- **Endpoint**: `/api/v1/my-properties/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get properties owned/managed by the tenant
- **Response**: List of properties

#### 18. **Toggle Property Favorite**
- **Method**: `POST`
- **Endpoint**: `/api/v1/toggle-favorite/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Add or remove property from favorites
- **Request Body**:
```json
{
  "property_id": 1
}
```

#### 19. **Get Favorite Properties**
- **Method**: `GET`
- **Endpoint**: `/api/v1/favorites/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get all favorited properties
- **Response**: List of favorite properties

#### 20. **Track Property View**
- **Method**: `POST`
- **Endpoint**: `/api/v1/properties/{id}/view/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Track when a user views a property
- **Request Body**:
```json
{
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1"
}
```

---

## 💰 Rent Management

### Protected Endpoints (Auth Required)

#### 21. **List Rent Invoices**
- **Method**: `GET`
- **Endpoint**: `/api/v1/rent/invoices/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get all rent invoices for the tenant
- **Query Parameters**:
  - `status` - Filter by status (paid, pending, overdue)
  - `page` - Page number
- **Response**: Paginated list of rent invoices

#### 22. **Get Rent Invoice Details**
- **Method**: `GET`
- **Endpoint**: `/api/v1/rent/invoices/{id}/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get details of a specific rent invoice
- **Response**: Invoice details

#### 23. **List Rent Payments**
- **Method**: `GET`
- **Endpoint**: `/api/v1/rent/payments/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get payment history
- **Query Parameters**:
  - `invoice_id` - Filter by invoice
  - `date_from` - Filter from date
  - `date_to` - Filter to date
  - `page` - Page number
- **Response**: Paginated list of rent payments

#### 24. **List Late Fees**
- **Method**: `GET`
- **Endpoint**: `/api/v1/rent/late-fees/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get late fee charges
- **Query Parameters**:
  - `status` - Filter by status
  - `page` - Page number
- **Response**: Paginated list of late fees

#### 25. **List Rent Reminders**
- **Method**: `GET`
- **Endpoint**: `/api/v1/rent/reminders/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get rent payment reminders
- **Query Parameters**:
  - `upcoming` - Show only upcoming reminders
  - `page` - Page number
- **Response**: Paginated list of rent reminders

---

## 💳 Payments

### Protected Endpoints (Auth Required)

#### 26. **List Payment Providers**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/providers/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get available payment methods
- **Response**: List of payment providers (M-Pesa, Airtel Money, Tigo Pesa, Bank Transfer, Cash)

#### 27. **List Invoices**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/invoices/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get all invoices
- **Query Parameters**:
  - `status` - Filter by status
  - `property_id` - Filter by property
  - `page` - Page number
- **Response**: Paginated list of invoices

#### 28. **Get Invoice Details**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/invoices/{id}/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get details of a specific invoice
- **Response**: Invoice details

#### 29. **List Payments**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/payments/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get payment history
- **Query Parameters**:
  - `invoice_id` - Filter by invoice
  - `provider` - Filter by payment provider
  - `page` - Page number
- **Response**: Paginated list of payments

#### 30. **Get Payment Details**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/payments/{id}/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get details of a specific payment
- **Response**: Payment details

#### 31. **List Transactions**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/transactions/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get transaction history
- **Query Parameters**:
  - `status` - Filter by status
  - `date_from` - Filter from date
  - `date_to` - Filter to date
  - `page` - Page number
- **Response**: Paginated list of transactions

#### 32. **List Expenses**
- **Method**: `GET`
- **Endpoint**: `/api/v1/payments/expenses/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get expenses
- **Query Parameters**:
  - `category` - Filter by category
  - `date_from` - Filter from date
  - `date_to` - Filter to date
  - `page` - Page number
- **Response**: Paginated list of expenses

---

## 🔧 Maintenance Requests

### Protected Endpoints (Auth Required)

#### 33. **List Maintenance Requests**
- **Method**: `GET`
- **Endpoint**: `/api/v1/maintenance/requests/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get all maintenance requests submitted by tenant
- **Query Parameters**:
  - `status` - Filter by status (pending, in_progress, completed)
  - `priority` - Filter by priority (low, medium, high, urgent)
  - `property_id` - Filter by property
  - `page` - Page number
- **Response**: Paginated list of maintenance requests

#### 34. **Get Maintenance Request Details**
- **Method**: `GET`
- **Endpoint**: `/api/v1/maintenance/requests/{id}/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get details of a specific maintenance request
- **Response**: Request details

#### 35. **Create Maintenance Request**
- **Method**: `POST`
- **Endpoint**: `/api/v1/maintenance/requests/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Submit a new maintenance request
- **Request Body**:
```json
{
  "property_id": 1,
  "title": "Leaking pipe in kitchen",
  "description": "Water leaking from pipe under sink",
  "priority": "high",
  "category": "plumbing",
  "photos": []
}
```
- **Response**: Created maintenance request

#### 36. **Update Maintenance Request**
- **Method**: `PUT` or `PATCH`
- **Endpoint**: `/api/v1/maintenance/requests/{id}/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Update an existing maintenance request
- **Request Body**: Updated fields
- **Response**: Updated request

---

## 📄 Documents

### Protected Endpoints (Auth Required)

#### 37. **List Documents**
- **Method**: `GET`
- **Endpoint**: `/api/v1/documents/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get all documents
- **Query Parameters**:
  - `category` - Filter by category
  - `property_id` - Filter by property
  - `page` - Page number
- **Response**: Paginated list of documents

#### 38. **Upload Document**
- **Method**: `POST`
- **Endpoint**: `/api/v1/documents/upload/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Upload a new document
- **Request**: Multipart form data with file
- **Response**: Uploaded document info

---

## 📊 Reports

### Protected Endpoints (Auth Required)

#### 39. **List Reports**
- **Method**: `GET`
- **Endpoint**: `/api/v1/reports/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get available reports
- **Response**: List of reports

---

## 📝 Complaints

### Protected Endpoints (Auth Required)

#### 40. **List Complaints**
- **Method**: `GET`
- **Endpoint**: `/api/v1/complaints/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Get all complaints
- **Query Parameters**:
  - `status` - Filter by status
  - `page` - Page number
- **Response**: Paginated list of complaints

#### 41. **Create Complaint**
- **Method**: `POST`
- **Endpoint**: `/api/v1/complaints/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Description**: Submit a complaint
- **Request Body**:
```json
{
  "subject": "Noise complaint",
  "description": "Loud music from neighbor",
  "priority": "medium"
}
```
- **Response**: Created complaint

---

## 📈 Summary

### Endpoints by Category

| Category | Count | Public | Protected |
|----------|-------|-------|-----------|
| **Authentication** | 8 | 2 | 6 |
| **Properties** | 12 | 7 | 5 |
| **Rent** | 5 | 0 | 5 |
| **Payments** | 6 | 0 | 6 |
| **Maintenance** | 4 | 0 | 4 |
| **Documents** | 2 | 0 | 2 |
| **Reports** | 1 | 0 | 1 |
| **Complaints** | 2 | 0 | 2 |
| **TOTAL** | **40** | **9** | **31** |

### Key Statistics

- **Total API Endpoints**: 40
- **Public Endpoints** (no auth): 9
- **Protected Endpoints** (auth required): 31
- **Authentication Method**: JWT Bearer Token
- **Base URL**: `http://127.0.0.1:8001/api/v1`

---

## 🔑 Getting Started as a Tenant

### Step 1: Register Account
```bash
POST /api/v1/auth/signup/
```
Create your tenant account (requires admin approval).

### Step 2: Wait for Approval
Your account will be pending until an admin approves it.

### Step 3: Login
```bash
POST /api/v1/auth/login/
```
Once approved, login to get JWT tokens.

### Step 4: Use APIs
Use the access token to access all protected endpoints:

```
Authorization: Bearer <your_access_token>
```

---

## 🛠️ Testing

### Test Credentials
- **Email**: api_test@example.com
- **Password**: test123
- **Status**: Approved ✓
- **Role**: Tenant ✓

### Test via Swagger UI
Access: http://127.0.0.1:8001/swagger/

### Test via Python Scripts
```bash
# Test public endpoints
python test_apis.py

# Test protected endpoints with auth
python test_apis_with_auth.py
```

---

## 📚 Additional Resources

- **Full API Documentation**: `API_DOCUMENTATION.md`
- **Swagger UI**: http://127.0.0.1:8001/swagger/
- **ReDoc**: http://127.0.0.1:8001/redoc/
- **Test Results**: `COMPLETE_API_TEST_SUMMARY.md`
- **Swagger Testing Guide**: `SWAGGER_TESTING_GUIDE.md`

---

**This is the complete list of all APIs available to a Tenant user!** 🎉

