# Manager Register Property Owner via Mobile App - Fix

## Issue
When managers register property owners via the mobile app API (`/api/v1/admin/register-owner/`), the "Property Owner" role was not being assigned correctly because the serializer wasn't receiving `"role": "owner"` in the request data.

## Root Cause
The `admin_register_owner` endpoint was:
1. Using `TenantSignupSerializer` without explicitly setting `role='owner'` in the request data
2. The serializer defaults to `role='tenant'` if not provided
3. Even though the profile.role was set to 'owner' afterwards, the CustomRole assignment might have been for 'Tenant' instead of 'Property Owner'

## Fix Applied

### Enhanced `admin_register_owner` Endpoint (`accounts/api_views.py`)

**Key Changes:**
1. **Force owner role in request data**: Added `request_data['role'] = 'owner'` before passing to serializer
2. **Verification**: Added checks to ensure Property Owner CustomRole is assigned
3. **Error handling**: Added fallback if role assignment fails
4. **Better logging**: Enhanced logging to track role assignment
5. **Data refresh**: Refresh user and profile before returning response

## Changes Made

### Before:
```python
# Use the signup serializer but auto-approve
serializer = TenantSignupSerializer(data=request.data)  # ❌ No role specified
```

### After:
```python
# Ensure role is set to 'owner' in request data for serializer
request_data = request.data.copy()
request_data['role'] = 'owner'  # ✅ Force owner role

# Use the signup serializer but auto-approve
serializer = TenantSignupSerializer(data=request_data)
```

### Additional Improvements:
- Verify Property Owner role assignment
- Create role if it doesn't exist
- Retry role assignment if it fails
- Refresh user data before response
- Enhanced logging with role assignment status

## Testing

### Test Manager Registering Owner:
```bash
POST /api/v1/admin/register-owner/
Authorization: Bearer <manager_token>
Content-Type: application/json

{
    "username": "hotel_owner_1",
    "email": "owner1@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+255123456789"
    // Note: "role" is NOT needed - it's automatically set to "owner"
}
```

### Expected Response:
```json
{
    "success": true,
    "message": "Owner account created and activated successfully for hotel_owner_1",
    "user": {
        "id": 123,
        "username": "hotel_owner_1",
        "email": "owner1@example.com",
        "role": ["Property Owner"],  // ✅ Should show Property Owner
        ...
    }
}
```

### Verification Steps:
1. ✅ User created with profile.role = 'owner'
2. ✅ CustomRole 'Property Owner' exists and is assigned
3. ✅ UserRole links user to Property Owner role
4. ✅ User is auto-approved
5. ✅ User can login immediately
6. ✅ User has Property Owner permissions

## Status

✅ **Fixed**: Manager/Admin registering owners now correctly:
- Forces `role='owner'` in serializer
- Assigns Property Owner CustomRole
- Verifies role assignment
- Auto-approves owner account
- Tracks who registered the owner

## Comparison

### Regular Signup (`/api/v1/auth/signup/`):
- User provides `"role": "owner"` in request
- Verification added to ensure role assignment

### Manager Register Owner (`/api/v1/admin/register-owner/`):
- Manager doesn't need to provide role (automatically set to 'owner')
- Requires authentication (Manager or Admin)
- Tracks who registered the owner
- Auto-approved and activated

## Notes

- The fix ensures the serializer receives `role='owner'` from the start
- This prevents the serializer from defaulting to 'tenant'
- Both endpoints now properly assign Property Owner role
- Enhanced logging helps debug any future issues
- Role assignment is verified and retried if it fails

