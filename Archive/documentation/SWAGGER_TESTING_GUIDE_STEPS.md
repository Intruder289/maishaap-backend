# Testing APIs via Swagger UI - Step by Step Guide

## Access Swagger UI

### Step 1: Open Swagger in Your Browser
Navigate to:
```
http://127.0.0.1:8001/swagger/
```

You should see the Swagger UI interface with all API endpoints organized by sections.

---

## Testing Public APIs (No Authentication Required)

### 1. Test Property Listings

#### Browse All Properties
1. Find **`GET /properties/`** in the Swagger interface
2. Click on it to expand
3. Click "**Try it out**" button
4. Click "**Execute**"
5. You'll see a list of all properties (House, Hotel, Lodge, Venue)

**Response:** Should return 200 OK with properties list

#### Filter by Property Type (House)
1. Expand **`GET /properties/`**
2. Click "**Try it out**"
3. In the **property_type** parameter field, enter `1`
4. Click "**Execute**"
5. You'll see only House properties

**Try these values for different types:**
- `1` = House
- `2` = Hotel
- `3` = Lodge
- `4` = Venue

#### Filter by Rent Range
1. Expand **`GET /properties/`**
2. Click "**Try it out**"
3. Fill in:
   - `min_rent`: 50
   - `max_rent`: 500
4. Click "**Execute**"
5. You'll see properties within that rent range

### 2. Test Property Details

1. Find **`GET /properties/{id}/`**
2. Click "**Try it out**"
3. Enter a property ID (e.g., `1`)
4. Click "**Execute**"
5. You'll see full property details

### 3. Test Featured Properties

1. Find **`GET /featured/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View featured properties

### 4. Test Recent Properties

1. Find **`GET /recent/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View recently added properties

### 5. Test Property Types

1. Find **`GET /property-types/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View: House, Hotel, Lodge, Venue

### 6. Test Regions

1. Find **`GET /regions/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View all regions

### 7. Test Amenities

1. Find **`GET /amenities/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View all amenities

---

## Getting Authentication Token (Required for Protected APIs)

### Step 1: Register a New User

1. Find **`POST /auth/signup/`** in Swagger
2. Click on it to expand
3. Click "**Try it out**"
4. Fill in the request body:
```json
{
  "username": "testuser_swagger",
  "email": "swagger@example.com",
  "password": "test123456",
  "confirm_password": "test123456",
  "first_name": "Test",
  "last_name": "User",
  "phone": "+254712345678",
  "role": "tenant"
}
```
5. Click "**Execute**"
6. You'll get a response showing "pending_approval"

**Note:** This user needs admin approval before login

### Step 2: Login to Get JWT Token

**Option A: Use Test Account (Recommended)**
1. Find **`POST /auth/login/`**
2. Click "**Try it out**"
3. Enter login credentials:
```json
{
  "email": "api_test@example.com",
  "password": "test123"
}
```
4. Click "**Execute**"
5. **Important:** Copy the `access` token from the response

**Option B: Use Your New Account (After Admin Approval)**
```json
{
  "email": "swagger@example.com",
  "password": "test123456"
}
```

### Step 3: Authorize in Swagger

1. Click the **"Authorize"** button (top right, with a lock icon)
2. In the "Value" field, paste your access token with "Bearer " prefix:
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```
3. Click "**Authorize**"
4. Click "**Close**"

**Now you can test protected endpoints!**

---

## Testing Protected APIs (Authentication Required)

### 1. Test User Profile

1. Find **`GET /auth/profile/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. You'll see your user profile information

### 2. Test Property Search

1. Find **`POST /search/`**
2. Click "**Try it out**"
3. Enter search criteria:
```json
{
  "query": "hotel",
  "filters": {
    "property_types": [2],
    "rent_range": {
      "min": 50,
      "max": 300
    }
  }
}
```
4. Click "**Execute**"
5. View search results

### 3. Test Get Favorite Properties

1. Find **`GET /favorites/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View your favorite properties (if any)

### 4. Test Toggle Favorite

1. Find **`POST /toggle-favorite/`**
2. Click "**Try it out**"
3. Enter property ID:
```json
{
  "property_id": 1
}
```
4. Click "**Execute**"
5. Response shows if property is now favorited

### 5. Test Get Rent Invoices

1. Find **`GET /rent/invoices/`**
2. Click "**Try it out**"
3. (Optional) Enter status filter: `paid`, `pending`, `overdue`
4. Click "**Execute**"
5. View rent invoices

### 6. Test Get Rent Payments

1. Find **`GET /rent/payments/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View payment history

### 7. Test Get Late Fees

1. Find **`GET /rent/late-fees/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View late fee charges

### 8. Test Get Rent Reminders

1. Find **`GET /rent/reminders/`**
2. Click "**Try it out**"
3. (Optional) Enter `upcoming: true` for upcoming reminders
4. Click "**Execute**"
5. View rent reminders

### 9. Test Get Payment Providers

1. Find **`GET /payments/providers/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View: M-Pesa, Airtel Money, Tigo Pesa, Bank Transfer, Cash

### 10. Test Get Invoices/Receipts

1. Find **`GET /payments/invoices/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View all invoices/receipts

### 11. Test Get Payment History

1. Find **`GET /payments/payments/`**
2. Click "**Try it out**"
3. Click "**Execute**"
4. View payment history

### 12. Test Get Transactions

1. Find **`GET /payments/transactions/`**
2. Click "**Try it out**"
3. (Optional) Filter by status or date
4. Click "**Execute**"
5. View transactions

### 13. Test Get Maintenance Requests

1. Find **`GET /maintenance/requests/`**
2. Click "**Try it out**"
3. (Optional) Filter by status, priority, property_id
4. Click "**Execute**"
5. View maintenance requests

### 14. Test Create Maintenance Request

1. Find **`POST /maintenance/requests/`**
2. Click "**Try it out**"
3. Enter request details:
```json
{
  "property_id": 1,
  "title": "Broken pipe",
  "description": "Water leaking in kitchen",
  "priority": "high",
  "category": "plumbing"
}
```
4. Click "**Execute**"
5. Response shows created maintenance request

### 15. Test Update Profile

1. Find **`PUT /auth/profile/update/`**
2. Click "**Try it out**"
3. Enter updates:
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "phone": "+254712345679"
}
```
4. Click "**Execute**"
5. View updated profile

### 16. Test Change Password

1. Find **`POST /auth/change-password/`**
2. Click "**Try it out**"
3. Enter password details:
```json
{
  "current_password": "test123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```
4. Click "**Execute**"
5. Response confirms password changed

---

## Quick Test Checklist

### Public APIs (No Auth Required)
- [ ] `GET /properties/` - List all properties
- [ ] `GET /properties/{id}/` - Get property details
- [ ] `GET /featured/` - Featured properties
- [ ] `GET /recent/` - Recent properties
- [ ] `GET /property-types/` - Property types
- [ ] `GET /regions/` - Regions
- [ ] `GET /amenities/` - Amenities
- [ ] `POST /auth/signup/` - User signup
- [ ] `POST /auth/login/` - User login

### Protected APIs (Auth Required - Get Token First!)
- [ ] `GET /auth/profile/` - Get profile
- [ ] `PUT /auth/profile/update/` - Update profile
- [ ] `POST /auth/change-password/` - Change password
- [ ] `POST /search/` - Advanced search
- [ ] `GET /favorites/` - Get favorites
- [ ] `POST /toggle-favorite/` - Toggle favorite
- [ ] `GET /rent/invoices/` - Rent invoices
- [ ] `GET /rent/payments/` - Rent payments
- [ ] `GET /rent/late-fees/` - Late fees
- [ ] `GET /rent/reminders/` - Rent reminders
- [ ] `GET /payments/providers/` - Payment providers
- [ ] `GET /payments/invoices/` - Invoices/receipts
- [ ] `GET /payments/payments/` - Payment history
- [ ] `GET /payments/transactions/` - Transactions
- [ ] `GET /maintenance/requests/` - Maintenance requests
- [ ] `POST /maintenance/requests/` - Create maintenance request

---

## Pro Tips

### 1. Understanding Responses

**Successful Responses:**
- ✅ Status: 200 OK = Success
- ✅ Status: 201 Created = Resource created
- ✅ Status: 204 No Content = Success with no response body

**Error Responses:**
- ❌ Status: 400 Bad Request = Invalid input
- ❌ Status: 401 Unauthorized = Not authenticated
- ❌ Status: 403 Forbidden = Not authorized
- ❌ Status: 404 Not Found = Resource doesn't exist
- ❌ Status: 500 Server Error = Backend error

### 2. Using Filters

Most GET endpoints support query parameters for filtering:
- **property_type**: 1 (House), 2 (Hotel), 3 (Lodge), 4 (Venue)
- **status**: Filter by status
- **page**: Pagination
- **search**: Text search
- **min_rent** / **max_rent**: Price range

### 3. Viewing Full Response

Click on the response to see:
- Response body (JSON)
- Response headers
- Response size
- Response time

### 4. Copy Request as cURL

You can copy any request as cURL command for testing:
1. Click "Copy" button in Swagger
2. Paste it in terminal
3. Execute to test from command line

### 5. Save Your Work

- Copy successful requests and responses
- Document which properties exist for testing
- Keep track of property IDs for testing favorites

---

## Troubleshooting

### Issue: "401 Unauthorized"
**Solution:** Click "Authorize" and add your Bearer token

### Issue: "400 Bad Request"
**Solution:** Check your request body format matches the schema

### Issue: "Empty Results"
**Solution:** 
- Check if there's data in the database
- Try different property IDs
- Check filters aren't too restrictive

### Issue: Swagger Shows Login Page
**Solution:** Make sure you're using the correct URL:
- ✅ Correct: `http://127.0.0.1:8001/swagger/`
- ❌ Wrong: `http://127.0.0.1:8000/swagger/`

---

## Test Credentials

For quick testing, use these credentials:

```
Email: api_test@example.com
Password: test123

This account is:
✅ Approved
✅ Active
✅ Has Tenant role
✅ Can access all endpoints
```

---

## Video Walkthrough (Text Version)

### Step-by-Step Process:

1. **Open Swagger**
   - Go to http://127.0.0.1:8001/swagger/

2. **Test Public Endpoint**
   - Expand `GET /properties/`
   - Click "Try it out"
   - Click "Execute"
   - ✅ See properties list

3. **Login**
   - Expand `POST /auth/login/`
   - Click "Try it out"
   - Enter test credentials
   - Click "Execute"
   - ✅ Copy access token

4. **Authorize**
   - Click "Authorize" button
   - Paste token with "Bearer " prefix
   - Click "Authorize"
   - ✅ Now authenticated

5. **Test Protected Endpoint**
   - Expand `GET /auth/profile/`
   - Click "Try it out"
   - Click "Execute"
   - ✅ See your profile

6. **Test Favorites**
   - Expand `GET /favorites/`
   - Click "Try it out"
   - Click "Execute"
   - ✅ See favorites

**That's it! You can now test all APIs.** 🎉

---

## Additional Resources

- **Swagger UI**: http://127.0.0.1:8001/swagger/
- **ReDoc**: http://127.0.0.1:8001/redoc/
- **API Documentation**: See FLUTTER_MOBILE_API_DOCUMENTATION.md
- **Base URL**: http://127.0.0.1:8001/api/v1

**Happy Testing!** 🚀

