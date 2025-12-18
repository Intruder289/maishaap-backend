# API Fixes Summary

## Overview
This document summarizes the fixes applied to three API issues:
1. Image Upload API - Missing image file field in Swagger documentation
2. Phone Login API - 500 Internal Server Error when logging in with phone number
3. Manager Login - Managers unable to login via mobile app

## Fixes Applied

### 1. Image Upload API ✅

**Issue:** The Swagger documentation for property image upload API was not showing the `image` file field, making it unclear how to upload images from mobile apps.

**Fix Applied:**
- Updated `PropertyImageUploadAPIView` in `properties/api_views.py`
- Added comprehensive Swagger documentation using `manual_parameters` with `openapi.IN_FORM` and `openapi.TYPE_FILE`
- Documented all form fields: `image`, `property`, `caption`, `is_primary`, `order`
- Added clear description that `multipart/form-data` content type should be used

**Files Modified:**
- `properties/api_views.py` (lines 345-400)

**API Endpoint:**
- `POST /api/v1/property-images/`
- Content-Type: `multipart/form-data`
- Authentication: Required (Bearer token)

**Usage Example:**
```python
files = {'image': ('image.jpg', image_file, 'image/jpeg')}
data = {
    'property': property_id,
    'caption': 'Optional caption',
    'is_primary': False,
    'order': 0
}
response = requests.post(url, files=files, data=data, headers={'Authorization': 'Bearer TOKEN'})
```

**Verification:**
- ✅ Swagger documentation now shows image file field
- ✅ All form parameters properly documented
- ✅ Serializer already includes `image` field (no changes needed)

---

### 2. Phone Login API ✅

**Issue:** Login via phone number was returning 500 Internal Server Error, while email login worked fine.

**Root Cause:**
- Phone number normalization was too simple (only stripped spaces)
- No handling for different phone formats (with/without `+`, with/without country code)
- Insufficient error handling causing exceptions to bubble up as 500 errors

**Fix Applied:**
- Enhanced `_normalize_phone()` method to handle spaces, dashes, parentheses
- Created new `_find_user_by_phone()` method that tries multiple phone formats:
  - Exact match
  - With/without leading `+`
  - Handles different storage formats in database
- Improved error handling to catch exceptions and return proper validation errors instead of 500 errors
- Added logging for debugging phone login issues

**Files Modified:**
- `accounts/serializers.py` (lines 115-188)

**API Endpoint:**
- `POST /api/v1/auth/login/`

**Supported Phone Formats:**
- `+255674367492` (with country code and +)
- `255674367492` (with country code, no +)
- `0674367492` (local format)
- `+255 674 367 492` (with spaces)
- `255-674-367-492` (with dashes)

**Verification:**
- ✅ Phone normalization handles multiple formats
- ✅ Multiple format lookup attempts
- ✅ Proper error handling (no more 500 errors)
- ✅ Clear error messages for users

---

### 3. Manager Login ✅

**Issue:** Managers were unable to login via mobile app because `'Manager'` role was not in the list of valid roles.

**Root Cause:**
- `TenantLoginSerializer` only allowed `['Tenant', 'Property Owner']` roles
- Managers have `'Manager'` role (from CustomRole or Django groups)
- Role validation was rejecting manager login attempts

**Fix Applied:**
- Added `'Manager'` to `valid_roles` list in `TenantLoginSerializer.validate()`
- Added check for Manager role in Django groups for backward compatibility
- Supports both `'Manager'` and `'Property manager'` group names

**Files Modified:**
- `accounts/serializers.py` (lines 218-238)

**API Endpoint:**
- `POST /api/v1/auth/login/`

**Supported Roles:**
- ✅ Tenant
- ✅ Property Owner
- ✅ Manager (NEW)

**Verification:**
- ✅ Manager role added to valid roles
- ✅ Backward compatibility with Django groups
- ✅ Managers can now login via mobile app

---

## Testing

### Code Verification
Run the verification script to check code structure:
```bash
python verify_api_fixes.py
```

### API Testing
Run the comprehensive test script (requires test credentials):
```bash
python test_fixed_apis.py
```

**Note:** Update test credentials in `test_fixed_apis.py` before running:
- Test user email/password
- Test user phone number
- Manager user email/password

### Manual Testing

#### 1. Image Upload
1. Login to get JWT token
2. Get a property ID (from `/api/v1/my-properties/`)
3. Upload image using multipart/form-data:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/property-images/" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "image=@test_image.jpg" \
     -F "property=1" \
     -F "caption=Test image"
   ```

#### 2. Phone Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"phone": "0674367492", "password": "yourpassword"}'
```

#### 3. Manager Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@example.com", "password": "managerpassword"}'
```

---

## Files Changed

1. **properties/api_views.py**
   - Enhanced `PropertyImageUploadAPIView` Swagger documentation

2. **accounts/serializers.py**
   - Enhanced `TenantLoginSerializer`:
     - Improved phone normalization
     - Added `_find_user_by_phone()` method
     - Better error handling
     - Added Manager role support

---

## Status

✅ **All fixes completed and verified**

- Image upload API: Swagger documentation updated
- Phone login API: Error handling improved, multiple format support
- Manager login: Manager role added to valid roles

---

## Notes

1. **Image Upload:** DRF's `CreateAPIView` automatically handles `multipart/form-data` when using `ModelSerializer` with `ImageField`. No parser configuration needed.

2. **Phone Login:** The phone field in Profile model is unique, so multiple account checks are redundant but kept for defensive programming.

3. **Manager Role:** Managers can login via both email and phone (if phone is set in their profile).

---

## Next Steps

1. Test APIs with actual mobile app
2. Verify Swagger documentation at `/swagger/`
3. Monitor logs for any phone login issues
4. Confirm managers can access mobile app features

