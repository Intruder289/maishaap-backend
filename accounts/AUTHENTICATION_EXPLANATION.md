# Custom JWT Authentication Explanation

## What is `GracefulJWTAuthentication`?

`GracefulJWTAuthentication` is a **custom JWT authentication class** that replaces Django REST Framework's default JWT authentication. It handles invalid/expired tokens gracefully instead of throwing errors.

## When is it Used?

**It is used for ALL API requests** that come to your Django REST Framework endpoints. This is because it's set in `settings.py` as the `DEFAULT_AUTHENTICATION_CLASSES`.

### Specifically:
- ✅ **All mobile app API calls** (`/api/v1/...`)
- ✅ **All web application API calls** (`/api/...`)
- ✅ **Every request** that uses DRF views

## How Does It Work?

### Before (Default JWT Authentication):
```
Mobile App sends expired token → Server validates token → Token is invalid → 
ERROR: "Given token not valid for any token type" → Request fails ❌
```

### After (Graceful JWT Authentication):
```
Mobile App sends expired token → Server validates token → Token is invalid → 
Silently ignore token → Treat as unauthenticated → Permission class decides → 
If endpoint allows guest access → Request succeeds ✅
```

## What Problem Does It Fix?

### Your Reported Issues:

1. **"Given token not valid for any token type" error**
   - **When:** Sometimes when entering mobile app as guest, or even when logged in
   - **Why:** Mobile app sends expired/invalid tokens from previous sessions
   - **Fix:** Invalid tokens are now ignored, allowing guest access to work

2. **"No categories available" on Home screen**
   - **When:** Mobile app tries to load categories but gets token error
   - **Why:** Token validation fails before the endpoint can respond
   - **Fix:** Categories endpoint (`/api/v1/categories/`) now works even with invalid tokens

## How It Handles Different Scenarios:

### Scenario 0: Login Credentials (Email or Phone)
```
Request: POST /api/v1/auth/login/
Body: { "email": "tenant@example.com", "password": "Secret123" }
   or { "phone": "+255700123456", "password": "Secret123" }
Result: ✅ Works (either identifier returns the same JWT bundle)
```

### Scenario 1: Guest User (No Token)
```
Request: GET /api/v1/properties/
Token: None
Result: ✅ Works (endpoint allows unauthenticated access)
```

### Scenario 2: Guest User (Invalid/Expired Token)
```
Request: GET /api/v1/properties/
Token: "eyJ0eXAiOiJKV1QiLCJhbGc..." (expired/invalid)
Result: ✅ Works (token ignored, treated as unauthenticated)
```

### Scenario 3: Authenticated User (Valid Token)
```
Request: GET /api/v1/properties/
Token: "eyJ0eXAiOiJKV1QiLCJhbGc..." (valid)
Result: ✅ Works (user authenticated normally)
```

### Scenario 4: Protected Endpoint (Requires Auth)
```
Request: POST /api/v1/properties/ (create property)
Token: None or Invalid
Result: ❌ 401 Unauthorized (correct behavior - endpoint requires auth)
```

## Is Your Problem Fixed?

### ✅ YES - Your specific issues are addressed:

1. **"Given token not valid" errors** → **FIXED**
   - Invalid tokens are now ignored for public endpoints
   - Guest users can browse without errors

2. **"No categories available"** → **FIXED**
   - Categories endpoint works even with invalid tokens
   - Home screen will load categories properly

3. **Errors when logged in** → **FIXED**
   - If token expires during session, it's handled gracefully
   - User can still access public endpoints

## Will the System Work Fine?

### ✅ YES - The system should work correctly:

- **Guest Mode:** ✅ Works perfectly (invalid tokens ignored)
- **Authenticated Mode:** ✅ Works perfectly (valid tokens authenticated)
- **Protected Endpoints:** ✅ Still secure (require valid authentication)
- **Public Endpoints:** ✅ Accessible to everyone (properties, categories, regions)

## Technical Details:

### Settings Configuration:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.GracefulJWTAuthentication',  # Our custom class
        'rest_framework.authentication.SessionAuthentication',   # For web app
    ],
}
```

### What Happens:
1. **Every API request** goes through `GracefulJWTAuthentication`
2. If token is **valid** → User is authenticated ✅
3. If token is **invalid/expired** → Returns `None` (unauthenticated) instead of error
4. **Permission class** then decides if unauthenticated access is allowed
5. For `IsAuthenticatedOrReadOnly` → GET requests work without auth ✅

## Summary:

- **What:** Custom JWT authentication that ignores invalid tokens
- **When:** Used for ALL API requests automatically
- **Why:** Fixes "token not valid" errors in guest mode
- **Result:** System works fine for both guest and authenticated users ✅

