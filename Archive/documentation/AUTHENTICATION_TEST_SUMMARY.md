# Mobile Authentication Testing - Complete Guide

## 🎯 What We're Testing

This tests the complete authentication flow between your Flutter mobile app and Django backend:

1. **Mobile App** → User signs up via API
2. **Web Admin** → Admin activates the user  
3. **Mobile App** → User logs in successfully
4. **Mobile App** → Makes authenticated requests

---

## 📋 Current Test Results

### ✅ Test User Created

**Username:** `testuser_20251006_100841`  
**Email:** `testuser_20251006_100841@example.com`  
**Password:** `TestPassword123!`  
**Status:** Pending activation (created via API)

**Response from Signup API:**
```json
{
  "success": true,
  "message": "Account created successfully. Your account is pending admin approval.",
  "user": {
    "id": 13,
    "username": "testuser_20251006_100841",
    "email": "testuser_20251006_100841@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "status": "pending_approval"
}
```

---

## 🔄 How to Complete the Test

### Step 1: View User in Web Interface ✅ DONE

1. Open browser: `http://127.0.0.1:8000/login/`
2. Login with your admin credentials
3. Go to: **User Management** → **User**
4. You should see: `testuser_20251006_100841` with **red inactive icon** 🔴

### Step 2: Activate the User ⏳ DO THIS NOW

On the user list page:
1. Find user: `testuser_20251006_100841`
2. Click the **green "Activate"** button
3. Success message should appear
4. User icon changes to **green** 🟢

### Step 3: Test Login After Activation

Run this PowerShell command:

```powershell
$loginData = @{
    email = "testuser_20251006_100841@example.com"
    password = "TestPassword123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/auth/login/" -Method POST -Body $loginData -ContentType "application/json" | ConvertTo-Json -Depth 5
```

**Expected Success Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "id": 13,
    "username": "testuser_20251006_100841",
    "email": "testuser_20251006_100841@example.com"
  }
}
```

---

## 🚀 Quick Start: New Test

For a fresh test with simpler username, run:

```powershell
.\test_mobile_flow.ps1
```

This will:
1. ✅ Create user: `testmobile1` via API
2. ✅ Verify login is blocked
3. ⏸️ Pause for you to activate on web
4. ✅ Test login after activation
5. ✅ Test authenticated requests with JWT

---

## 📱 Flutter Integration Code

Once you've verified the flow works, use this in your Flutter app:

### 1. Signup Screen

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> signupUser({
  required String username,
  required String email,
  required String password,
  required String firstName,
  required String lastName,
  required String phone,
  String role = 'tenant',
}) async {
  final url = Uri.parse('http://YOUR_IP:8000/api/v1/auth/signup/');
  
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'email': email,
      'password': password,
      'confirm_password': password,
      'first_name': firstName,
      'last_name': lastName,
      'phone': phone,
      'role': role,
    }),
  );
  
  final data = jsonDecode(response.body);
  
  if (response.statusCode == 201) {
    // Success - show message to user
    // "Account created! Wait for admin approval."
    return {'success': true, 'data': data};
  } else {
    // Error - show validation errors
    return {'success': false, 'errors': data['errors']};
  }
}
```

### 2. Login Screen

```dart
Future<Map<String, dynamic>> loginUser({
  required String email,
  required String password,
}) async {
  final url = Uri.parse('http://YOUR_IP:8000/api/v1/auth/login/');
  
  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'email': email,
      'password': password,
    }),
  );
  
  final data = jsonDecode(response.body);
  
  if (response.statusCode == 200) {
    // Success - store tokens
    final accessToken = data['access'];
    final refreshToken = data['refresh'];
    
    // Store in secure storage (flutter_secure_storage)
    await storage.write(key: 'access_token', value: accessToken);
    await storage.write(key: 'refresh_token', value: refreshToken);
    
    return {'success': true, 'user': data['user']};
  } else {
    // Error - show message
    // Common: "Account pending approval" or "Invalid credentials"
    return {'success': false, 'message': data['message']};
  }
}
```

### 3. Authenticated Request

```dart
Future<Map<String, dynamic>> getUserProfile() async {
  final accessToken = await storage.read(key: 'access_token');
  final url = Uri.parse('http://YOUR_IP:8000/api/v1/auth/profile/');
  
  final response = await http.get(
    url,
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
  );
  
  if (response.statusCode == 200) {
    return jsonDecode(response.body);
  } else if (response.statusCode == 401) {
    // Token expired - refresh or logout
    return {'error': 'unauthorized'};
  } else {
    return {'error': 'failed'};
  }
}
```

---

## 🔐 API Endpoints Reference

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/v1/auth/signup/` | POST | No | Register new user |
| `/api/v1/auth/login/` | POST | No | Login (get JWT tokens) |
| `/api/v1/auth/profile/` | GET | Yes (JWT) | Get user profile |
| `/api/v1/auth/logout/` | POST | Yes (JWT) | Logout user |
| `/api/v1/auth/refresh/` | POST | Yes (Refresh token) | Refresh access token |

---

## 🛠️ Troubleshooting

### Issue: "Account pending approval" after activation

**Solution:**
1. Go to Django admin: `http://127.0.0.1:8000/admin/`
2. Navigate to: **Authentication and Authorization** → **Users**
3. Click on the user
4. Check both:
   - ✅ **Active** (in Status section)
   - ✅ **Is approved** (in Profile section if exists)
5. Save

### Issue: Can't find user in web interface

**Solution:**
1. Check user was created: `http://127.0.0.1:8000/admin/auth/user/`
2. Or run in Django shell:
```python
python manage.py shell
from django.contrib.auth.models import User
User.objects.filter(email="testuser_20251006_100841@example.com").first()
```

### Issue: Login returns 500 error

**Check server logs:**
```powershell
# In terminal running server
# Look for error traceback
```

---

## ✅ Success Checklist

- [x] User signup via API works (201 response)
- [x] Login blocked before activation (400 response)
- [ ] User visible in web user list
- [ ] Activate button works on web
- [ ] Login succeeds after activation (200 response with tokens)
- [ ] Authenticated requests work with JWT token

---

## 📊 Test Data Summary

### Test User 1 (Already Created)
- **Username:** `testuser_20251006_100841`
- **Email:** `testuser_20251006_100841@example.com`
- **Password:** `TestPassword123!`
- **Status:** ⏳ Waiting for activation

### Test User 2 (For Fresh Test)
Run `.\test_mobile_flow.ps1` to create:
- **Username:** `testmobile1`
- **Email:** `testmobile1@example.com`
- **Password:** `MobilePass123!`

---

## 🎓 Next Steps

1. **Complete Current Test:**
   - Activate `testuser_20251006_100841` on web
   - Test login with PowerShell command above

2. **Run Fresh Test:**
   - Execute `.\test_mobile_flow.ps1`
   - Follow the interactive prompts

3. **Integrate with Flutter:**
   - Use the code examples above
   - Replace `YOUR_IP` with your actual server IP
   - Test on emulator first, then real device

4. **Production Deployment:**
   - Use HTTPS (not HTTP)
   - Store JWT tokens securely (flutter_secure_storage)
   - Implement token refresh logic
   - Add proper error handling

---

## 📞 Support

If you encounter issues:
1. Check Django server logs
2. Verify database has the user
3. Test with Swagger UI: `http://127.0.0.1:8000/swagger/`
4. Use Django admin panel for manual verification

**Server must be running:**
```powershell
python manage.py runserver
```
