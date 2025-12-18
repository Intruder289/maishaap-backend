# Swagger UI Testing Guide

## 🌐 Access Swagger UI

Swagger UI is available and working at these URLs:

### Primary URLs
1. **Swagger UI**: http://127.0.0.1:8001/swagger/
2. **Swagger UI (without trailing slash)**: http://127.0.0.1:8001/swagger
3. **Swagger JSON Schema**: http://127.0.0.1:8001/swagger.json
4. **ReDoc Documentation**: http://127.0.0.1:8001/redoc/

### API Base URL
- **API Base**: http://127.0.0.1:8001/api/v1/

---

## 🧪 Testing via Swagger UI

### Step 1: Open Swagger UI
Open your browser and navigate to:
```
http://127.0.0.1:8001/swagger/
```

### Step 2: Available API Endpoints

The Swagger UI will display all available API endpoints organized by categories:

#### 1. Authentication Endpoints
- **POST** `/api/v1/auth/signup/` - User Registration
- **POST** `/api/v1/auth/login/` - User Login
- **POST** `/api/v1/auth/logout/` - User Logout
- **GET** `/api/v1/auth/profile/` - Get User Profile
- **PUT** `/api/v1/auth/profile/update/` - Update Profile
- **POST** `/api/v1/auth/change-password/` - Change Password
- **POST** `/api/v1/auth/refresh/` - Refresh Token
- **POST** `/api/v1/auth/verify/` - Verify Token

#### 2. Properties Endpoints
- **GET** `/api/v1/properties/` - List Properties
- **POST** `/api/v1/properties/` - Create Property
- **GET** `/api/v1/properties/{id}/` - Get Property Details
- **GET** `/api/v1/my-properties/` - Get My Properties
- **GET** `/api/v1/property-types/` - List Property Types
- **GET** `/api/v1/regions/` - List Regions
- **GET** `/api/v1/amenities/` - List Amenities

#### 3. Rent Endpoints
- **GET** `/api/v1/rent/invoices/` - List Rent Invoices
- **GET** `/api/v1/rent/payments/` - List Rent Payments
- **GET** `/api/v1/rent/late-fees/` - List Late Fees
- **GET** `/api/v1/rent/reminders/` - List Rent Reminders

#### 4. Payments Endpoints
- **GET** `/api/v1/payments/providers/` - List Payment Providers
- **GET** `/api/v1/payments/invoices/` - List Invoices
- **GET** `/api/v1/payments/payments/` - List Payments
- **GET** `/api/v1/payments/transactions/` - List Transactions
- **GET** `/api/v1/payments/expenses/` - List Expenses

#### 5. Maintenance Endpoints
- **GET** `/api/v1/maintenance/requests/` - List Maintenance Requests

#### 6. Admin Endpoints
- **GET** `/api/v1/admin/pending-users/` - Get Pending Users
- **POST** `/api/v1/admin/approve-user/` - Approve User

---

## 🔐 How to Test Protected Endpoints

### Step 1: Get Authentication Token

1. Click on **POST** `/api/v1/auth/login/`
2. Click "Try it out"
3. Enter the test credentials:
   ```json
   {
     "email": "api_test@example.com",
     "password": "test123"
   }
   ```
4. Click "Execute"
5. Copy the `access` token from the response

### Step 2: Authorize in Swagger

1. Click the **Authorize** button (top right of Swagger UI)
2. In the "Value" field, enter: `Bearer <your_access_token>`
   - Example: `Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
3. Click "Authorize"
4. Close the authorization dialog

### Step 3: Test Protected Endpoints

Now you can test any protected endpoint:
1. Click on the endpoint you want to test
2. Click "Try it out"
3. Fill in any required parameters
4. Click "Execute"

---

## 📝 Example Testing Workflow

### Test 1: User Signup (No Auth Required)

1. **Endpoint**: `POST /api/v1/auth/signup/`
2. **Request Body**:
   ```json
   {
     "username": "testuser_swagger",
     "email": "swagger@example.com",
     "password": "test123456",
     "confirm_password": "test123456",
     "first_name": "Swagger",
     "last_name": "Test",
     "phone": "+254712345678",
     "role": "tenant"
   }
   ```
3. **Expected Response**: 201 Created with user data

### Test 2: Get User Profile (Auth Required)

1. **Endpoint**: `GET /api/v1/auth/profile/`
2. **Headers**: `Authorization: Bearer <token>`
3. **Expected Response**: 200 OK with profile data

### Test 3: List Properties (No Auth Required)

1. **Endpoint**: `GET /api/v1/properties/`
2. **Expected Response**: 200 OK with list of properties

### Test 4: List Payment Providers (Auth Required)

1. **Endpoint**: `GET /api/v1/payments/providers/`
2. **Headers**: `Authorization: Bearer <token>`
3. **Expected Response**: 200 OK with list of payment providers

---

## 🔍 Swagger UI Features

### 1. Interactive API Testing
- Click any endpoint to expand it
- View request/response schemas
- Execute requests directly from the UI
- See real-time responses

### 2. Authorization
- Click "Authorize" button to set JWT tokens
- Tokens are used for all protected endpoints
- You can set multiple authorization methods

### 3. Schema Documentation
- View request body schemas
- View response schemas
- See required vs optional fields
- See data types and validation rules

### 4. Examples
- See example request bodies
- See example responses
- Understand data formats

---

## 🎯 Quick Test Credentials

For testing via Swagger UI, use these credentials:

```json
{
  "email": "api_test@example.com",
  "password": "test123"
}
```

This user has:
- ✅ Approved status
- ✅ Active account
- ✅ Tenant role
- ✅ Full API access

---

## 📊 Testing Checklist

### Public Endpoints (No Auth)
- [ ] GET /api/v1/ - API Root
- [ ] GET /api/v1/properties/ - List Properties
- [ ] GET /api/v1/property-types/ - List Property Types
- [ ] GET /api/v1/regions/ - List Regions
- [ ] GET /api/v1/amenities/ - List Amenities
- [ ] POST /api/v1/auth/signup/ - User Signup

### Protected Endpoints (Auth Required)
- [ ] POST /api/v1/auth/login/ - User Login
- [ ] GET /api/v1/auth/profile/ - Get Profile
- [ ] GET /api/v1/my-properties/ - My Properties
- [ ] GET /api/v1/rent/invoices/ - Rent Invoices
- [ ] GET /api/v1/payments/providers/ - Payment Providers
- [ ] GET /api/v1/maintenance/requests/ - Maintenance Requests

---

## 🛠️ Troubleshooting

### Issue: "401 Unauthorized"
**Solution**: Click "Authorize" and add your JWT token

### Issue: "400 Bad Request"
**Solution**: Check the request body format matches the schema

### Issue: Swagger UI shows login page
**Solution**: The Swagger URL is correct. Make sure you're accessing:
- http://127.0.0.1:8001/swagger/

### Issue: Cannot see all endpoints
**Solution**: Check the server is running on port 8001

---

## 📚 Additional Resources

- **API Documentation**: See `API_DOCUMENTATION.md`
- **Test Scripts**: 
  - `test_apis.py` - Public endpoints
  - `test_apis_with_auth.py` - Protected endpoints
- **Test Results**: See `COMPLETE_API_TEST_SUMMARY.md`

---

## ✅ Summary

Swagger UI is fully functional and accessible at:
- **URL**: http://127.0.0.1:8001/swagger/
- **Status**: ✅ Working
- **API Base**: http://127.0.0.1:8001/api/v1/

**You can now test all APIs interactively through the Swagger UI!** 🎉


