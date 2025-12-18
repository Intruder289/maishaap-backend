# Mobile Signup & Web Activation Test Guide

## Overview
This guide tests the complete user registration flow:
1. **Mobile App**: User signs up via API
2. **Web Admin**: Admin activates the user
3. **Mobile App**: User logs in successfully

---

## Prerequisites

1. Django dev server running: `python manage.py runserver`
2. Admin user created and logged into web interface
3. Terminal/PowerShell for API testing

---

## Test Flow

### Step 1: Mobile Signup (API)

**Endpoint:** `POST http://127.0.0.1:8000/api/v1/auth/signup/`

**PowerShell Command:**
```powershell
$body = @{
    username = "mobileuser1"
    email = "mobileuser1@example.com"
    password = "SecurePass123!"
    confirm_password = "SecurePass123!"
    first_name = "Mobile"
    last_name = "User"
    phone = "+254712345678"
    role = "tenant"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/signup/" -Method POST -Body $body -ContentType "application/json"
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Account created successfully. Your account is pending admin approval. You will be able to login once approved.",
  "user": {
    "id": 10,
    "username": "mobileuser1",
    "email": "mobileuser1@example.com",
    "first_name": "Mobile",
    "last_name": "User",
    "is_active": false,
    "profile": {
      "phone": "+254712345678",
      "role": "tenant",
      "is_approved": false
    }
  },
  "status": "pending_approval"
}
```

**Key Points:**
- ✅ User created successfully
- ⚠️ `is_active: false` - User cannot login yet
- ⚠️ `is_approved: false` - Requires admin approval

---

### Step 2: Try Login BEFORE Activation (Should Fail)

**Endpoint:** `POST http://127.0.0.1:8000/api/v1/auth/login/`

**PowerShell Command:**
```powershell
$loginBody = @{
    email = "mobileuser1@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
```

**Expected Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Your account is pending admin approval. Please wait for activation."
}
```

**Key Point:**
- ❌ Login blocked - user not activated

---

### Step 3: Web Activation

**Manual Steps:**

1. **Open Browser:** Navigate to `http://127.0.0.1:8000/login/`

2. **Login as Admin:** Use your admin credentials

3. **Go to User List:** 
   - Click **User Management** in sidebar
   - Click **User** submenu
   - OR direct URL: `http://127.0.0.1:8000/user-list/`

4. **Find New User:** Look for `mobileuser1` in the list
   - Should show **red inactive icon** 🔴
   - Email: `mobileuser1@example.com`

5. **Activate User:** Click the **"Activate"** button

6. **Verify Activation:**
   - Status changes to **green active icon** 🟢
   - Success message: "User 'mobileuser1' has been activated successfully."

**Screenshot Location:** User should appear in the list with activate button

---

### Step 4: Login AFTER Activation (Should Succeed)

**Endpoint:** `POST http://127.0.0.1:8000/api/v1/auth/login/`

**PowerShell Command (same as Step 2):**
```powershell
$loginBody = @{
    email = "mobileuser1@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login/" -Method POST -Body $loginBody -ContentType "application/json"
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 10,
    "username": "mobileuser1",
    "email": "mobileuser1@example.com",
    "first_name": "Mobile",
    "last_name": "User",
    "is_active": true,
    "profile": {
      "phone": "+254712345678",
      "role": "tenant",
      "is_approved": true
    }
  }
}
```

**Key Points:**
- ✅ Login successful
- ✅ JWT tokens provided (`access` and `refresh`)
- ✅ `is_active: true` and `is_approved: true`

---

### Step 5: Make Authenticated Request

**Endpoint:** `GET http://127.0.0.1:8000/api/v1/auth/profile/`

**PowerShell Command:**
```powershell
# Use the access token from Step 4
$token = "eyJ0eXAiOiJKV1QiLCJhbGc..."  # Replace with actual token

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/profile/" -Method GET -Headers $headers
```

**Expected Response (200 OK):**
```json
{
  "id": 10,
  "username": "mobileuser1",
  "email": "mobileuser1@example.com",
  "first_name": "Mobile",
  "last_name": "User",
  "is_active": true,
  "profile": {
    "phone": "+254712345678",
    "role": "tenant",
    "is_approved": true,
    "image": null
  }
}
```

**Key Point:**
- ✅ Authenticated request successful with JWT token

---

## Python Test Script

For automated testing, run:

```powershell
python test_mobile_signup_activation.py
```

This script will:
1. ✅ Create user via API
2. ✅ Verify login is blocked
3. ⏸️ Pause for manual web activation
4. ✅ Verify login after activation
5. ✅ Test authenticated requests

---

## Troubleshooting

### Issue 1: Signup fails with "username already exists"
**Solution:** Use a different username or delete the test user from admin panel

### Issue 2: Login still fails after activation
**Check:**
- User's `is_active` field is `True` in database
- Profile's `is_approved` field is `True`
- Correct password is being used

**Fix via Django Admin:**
```
http://127.0.0.1:8000/admin/auth/user/
```

### Issue 3: Activate button doesn't appear
**Check:**
- You're logged in as admin/staff user
- User list page is loading correctly
- User exists in the database

---

## Test Credentials

After running the test, you'll have:

- **Username:** `mobileuser1`
- **Email:** `mobileuser1@example.com`
- **Password:** `SecurePass123!`
- **Role:** Tenant

You can use these credentials to test your mobile app!

---

## API Endpoints Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/auth/signup/` | POST | None | Register new user |
| `/api/v1/auth/login/` | POST | None | Login and get tokens |
| `/api/v1/auth/profile/` | GET | JWT | Get user profile |
| `/api/v1/auth/logout/` | POST | JWT | Logout user |

---

## Flutter Integration Example

```dart
// 1. Signup
final signupResponse = await http.post(
  Uri.parse('http://127.0.0.1:8000/api/v1/auth/signup/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'flutteruser',
    'email': 'flutter@example.com',
    'password': 'SecurePass123!',
    'confirm_password': 'SecurePass123!',
    'first_name': 'Flutter',
    'last_name': 'User',
    'phone': '+254712345678',
    'role': 'tenant',
  }),
);

// 2. Login (after web activation)
final loginResponse = await http.post(
  Uri.parse('http://127.0.0.1:8000/api/v1/auth/login/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'email': 'flutter@example.com',
    'password': 'SecurePass123!',
  }),
);

final data = jsonDecode(loginResponse.body);
final accessToken = data['access'];
final refreshToken = data['refresh'];

// 3. Authenticated request
final profileResponse = await http.get(
  Uri.parse('http://127.0.0.1:8000/api/v1/auth/profile/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json',
  },
);
```

---

## Next Steps

1. ✅ Test signup flow
2. ✅ Test web activation
3. ✅ Test mobile login
4. 🔄 Integrate with Flutter app
5. 📱 Test on actual mobile device
6. 🚀 Deploy to production server
