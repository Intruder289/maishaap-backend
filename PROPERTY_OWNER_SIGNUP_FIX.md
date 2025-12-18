# Property Owner Signup via Mobile App API - Fix

## Issue
When property owners register via the mobile app API (`/api/v1/auth/signup/`), they were not getting the "Property Owner" role assigned correctly.

## Root Cause
The signup serializer was creating the user and profile correctly, but there were potential issues:
1. The CustomRole assignment might fail silently
2. No verification that the role was actually assigned
3. Profile role might not be set correctly if role assignment failed

## Fix Applied

### 1. Enhanced Signup Serializer (`accounts/serializers.py`)
- Added verification that UserRole was created successfully
- Added logging to track role assignment
- Added profile refresh to ensure relationships are loaded
- Better error handling for role assignment failures

### 2. Enhanced API View (`accounts/api_views.py`)
- Added verification step after user creation
- For owners, explicitly checks and assigns "Property Owner" CustomRole
- Verifies profile.role is set to 'owner'
- Creates Property Owner role if it doesn't exist
- Refreshes user and profile before returning response
- Enhanced logging for debugging

## Changes Made

### `accounts/serializers.py` - TenantSignupSerializer.create()
```python
# Before: Simple get_or_create without verification
UserRole.objects.get_or_create(user=user, role=custom_role)

# After: Verify assignment and log results
user_role, created = UserRole.objects.get_or_create(user=user, role=custom_role)
if not UserRole.objects.filter(user=user, role=custom_role).exists():
    logger.error(f"Failed to assign {role_name} role to user {user.username}")
```

### `accounts/api_views.py` - tenant_signup()
Added verification block after user creation:
```python
if role == 'owner':
    # Ensure Property Owner role is assigned
    # Verify CustomRole exists
    # Assign UserRole if missing
    # Verify profile.role is 'owner'
    # Create role if it doesn't exist
```

## Testing

### Test Signup as Property Owner:
```bash
POST /api/v1/auth/signup/
Content-Type: application/json

{
    "username": "test_owner",
    "email": "owner@example.com",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+255123456789",
    "role": "owner"
}
```

### Expected Response:
```json
{
    "success": true,
    "message": "Account created successfully. You can now login immediately.",
    "user": {
        "id": 123,
        "username": "test_owner",
        "email": "owner@example.com",
        "role": ["Property Owner"],
        ...
    },
    "tokens": {
        "access": "...",
        "refresh": "..."
    },
    "status": "approved"
}
```

### Verification Steps:
1. Check user.profile.role == 'owner'
2. Check CustomRole 'Property Owner' exists
3. Check UserRole is assigned (user.user_roles.filter(role__name='Property Owner').exists())
4. User can login immediately
5. User has Property Owner permissions

## Status

✅ **Fixed**: Property owner signup now correctly assigns:
- Profile role: 'owner'
- CustomRole: 'Property Owner'
- UserRole: Links user to Property Owner role
- Auto-approved: True
- Can login immediately

## Notes

- The fix includes both prevention (better assignment in serializer) and verification (check in API view)
- If Property Owner role doesn't exist, it will be created automatically
- All signups are auto-approved for immediate login
- Enhanced logging helps debug any future issues

