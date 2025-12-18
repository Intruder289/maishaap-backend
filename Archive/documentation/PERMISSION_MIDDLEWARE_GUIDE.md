# Permission Middleware Implementation Guide

## Overview

This document describes the comprehensive permission middleware system implemented for the Maisha Backend application. The system provides role-based and permission-based access control to ensure that only authorized users can access specific pages and features.

## Components

### 1. Middleware Classes

#### `RolePermissionMiddleware`
**Location:** `accounts/middleware/permissions.py`

This middleware automatically checks every request to ensure the user has the required permissions to access the requested page.

**Features:**
- ✅ Checks user authentication status
- ✅ Verifies role-based access (Admin, Manager, Property owner, Tenant)
- ✅ Validates permission-based access using Django's permission system
- ✅ Redirects unauthenticated users to login
- ✅ Shows custom 403 page for unauthorized access
- ✅ Allows unapproved users only limited access
- ✅ Bypasses checks for superusers
- ✅ Excludes static files, media, and API endpoints

**Configuration:**

```python
# Public URLs (no authentication required)
PUBLIC_URLS = [
    'login', 'register', 'logout', 'password_reset', etc.
]

# Permission-based restrictions
PERMISSION_REQUIRED_URLS = {
    'role_list': 'accounts.view_customrole',
    'property_create': 'properties.add_property',
    # ... more mappings
}

# Role-based restrictions
ROLE_REQUIRED_URLS = {
    'role_list': ['Admin', 'Manager'],
    'property_list': ['Admin', 'Manager', 'Property owner'],
    # ... more mappings
}
```

#### `ActivityLoggingMiddleware`
**Location:** `accounts/middleware/permissions.py`

Automatically logs user activities for audit and tracking purposes.

**Features:**
- ✅ Logs POST, PUT, PATCH, DELETE requests
- ✅ Creates `ActivityLog` entries for important actions
- ✅ Generates human-readable descriptions
- ✅ Excludes static files and media
- ✅ Only logs successful operations (2xx status codes)

### 2. Custom Decorators

**Location:** `accounts/decorators.py`

Additional decorators for fine-grained permission control in views.

#### `@role_required(*roles)`
Restricts view access to specific roles.

```python
from accounts.decorators import role_required

@role_required('Admin', 'Manager')
def manage_users(request):
    # Only Admin and Manager can access
    ...
```

#### `@permission_required(permission)`
Restricts view access based on Django permissions.

```python
from accounts.decorators import permission_required

@permission_required('properties.add_property')
def create_property(request):
    # Only users with add_property permission
    ...
```

#### `@approved_user_required`
Ensures only approved users can access the view.

```python
from accounts.decorators import approved_user_required

@approved_user_required
def premium_feature(request):
    # Only approved users can access
    ...
```

#### `@owner_or_admin_required`
Allows access only to resource owners or admins.

```python
from accounts.decorators import owner_or_admin_required

@owner_or_admin_required
def edit_profile(request, user_id):
    # Only the user or admins can edit profile
    ...
```

#### AJAX Decorators
For AJAX views that return JSON responses:
- `@ajax_role_required(*roles)`
- `@ajax_permission_required(permission)`

### 3. Custom 403 Page

**Location:** `accounts/templates/accounts/403.html`

Beautiful, user-friendly forbidden access page with:
- Clear error message
- Explanation of why access was denied
- Action buttons (Dashboard, Go Back)
- Contact information
- Fully responsive design
- Orange gradient theme matching the site

## Installation & Configuration

### Step 1: Enable Middleware

Add to `settings.py`:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ⭐ Custom middleware
    'accounts.middleware.permissions.RolePermissionMiddleware',
    'accounts.middleware.permissions.ActivityLoggingMiddleware',
]
```

**Important:** Place custom middleware AFTER `AuthenticationMiddleware`

### Step 2: Configure URL Permissions

Edit `accounts/middleware/permissions.py` to add your URL patterns:

```python
# Add to PERMISSION_REQUIRED_URLS
PERMISSION_REQUIRED_URLS = {
    'your_view_name': 'app_label.permission_codename',
}

# Add to ROLE_REQUIRED_URLS
ROLE_REQUIRED_URLS = {
    'your_view_name': ['Admin', 'Manager'],
}
```

### Step 3: Use in Views (Optional)

For additional protection, use decorators in views:

```python
from accounts.decorators import role_required, permission_required

@role_required('Admin')
def admin_only_view(request):
    ...

@permission_required('properties.delete_property')
def delete_property(request, pk):
    ...
```

## Access Control Flow

```
User Request
    ↓
Is Public URL? → Yes → Allow Access
    ↓ No
Is Authenticated? → No → Redirect to Login
    ↓ Yes
Is Superuser? → Yes → Allow Access
    ↓ No
Is Approved? → No → Limit to Dashboard/Logout
    ↓ Yes
Check Role Requirements → Fail → Show 403 Page
    ↓ Pass
Check Permission Requirements → Fail → Show 403 Page
    ↓ Pass
Allow Access
```

## Permission Matrix

### By Role

| Page/Feature | Admin | Manager | Property Owner | Tenant |
|-------------|-------|---------|----------------|--------|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Role Management | ✅ | ✅ | ❌ | ❌ |
| User Management | ✅ | ✅ | ❌ | ❌ |
| System Logs | ✅ | ✅ | ❌ | ❌ |
| Property List | ✅ | ✅ | ✅ | ❌ |
| Property Create | ✅ | ✅ | ✅ | ❌ |
| Maintenance Requests | ✅ | ✅ | ✅ | ✅ |
| Payments | ✅ | ✅ | ✅ | ✅ |
| Reports | ✅ | ✅ | ✅ | ❌ |

### By Permission

Common Django permissions used:
- `view_model` - View list/details
- `add_model` - Create new items
- `change_model` - Edit existing items
- `delete_model` - Delete items

Example for Properties:
- `properties.view_property`
- `properties.add_property`
- `properties.change_property`
- `properties.delete_property`

## Customization

### Adding New Protected URLs

1. **Add to Middleware:**
```python
# In accounts/middleware/permissions.py
ROLE_REQUIRED_URLS = {
    'new_view_name': ['Admin', 'Manager'],
}
```

2. **Or use decorator in view:**
```python
@role_required('Admin', 'Manager')
def new_view(request):
    ...
```

### Creating Custom Roles

```python
from accounts.models import CustomRole
from django.contrib.auth.models import Permission

# Create role
role = CustomRole.objects.create(
    name='Custom Role',
    description='Special access role'
)

# Add permissions
permission = Permission.objects.get(codename='add_property')
role.permissions.add(permission)
```

### Assigning Roles to Users

```python
from accounts.models import UserRole

UserRole.objects.create(
    user=user,
    role=role,
    assigned_by=admin_user
)
```

## Testing

### Test Permission Middleware

```python
# Try accessing protected page without login
# Should redirect to login

# Login as Tenant
# Try accessing admin page
# Should show 403 page

# Login as Admin
# Try accessing admin page
# Should succeed
```

### Check Activity Logs

```python
from accounts.models import ActivityLog

# View recent activities
logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
```

## Troubleshooting

### Issue: Users can access restricted pages

**Solution:** Check middleware order in `settings.py`. `RolePermissionMiddleware` must come after `AuthenticationMiddleware`.

### Issue: 403 page not showing

**Solution:** Ensure `accounts/templates/accounts/403.html` exists and template path is correct.

### Issue: Superuser can't access pages

**Solution:** Check for errors in middleware. Superusers should bypass all checks.

### Issue: Activity logs not being created

**Solution:** Verify `ActivityLoggingMiddleware` is enabled and comes after authentication middleware.

## Security Best Practices

1. ✅ **Use HTTPS** in production
2. ✅ **Keep SECRET_KEY secure**
3. ✅ **Regularly review permissions**
4. ✅ **Monitor activity logs** for suspicious behavior
5. ✅ **Use strong password requirements**
6. ✅ **Implement account lockout** after failed login attempts
7. ✅ **Regularly audit user roles** and permissions
8. ✅ **Remove unused permissions** promptly

## API Endpoints

Note: API endpoints (`/api/*`) are excluded from middleware checks. They use DRF permission classes instead:

```python
# In API views
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminOrManager

class MyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrManager]
```

## Logging

Activity logs are stored in the `ActivityLog` model and include:
- User who performed action
- Action type (create, update, delete, etc.)
- Description
- Content type (Property, Payment, etc.)
- Timestamp
- Priority level
- Metadata (JSON field for additional data)

Access logs via:
- Admin interface
- System Logs page (Admin/Manager only)
- API endpoint: `/api/activity-logs/`

## Future Enhancements

Potential improvements:
- [ ] IP-based restrictions
- [ ] Time-based access controls
- [ ] Two-factor authentication
- [ ] Session management (concurrent login limits)
- [ ] Advanced audit trails with change history
- [ ] Email notifications for permission changes
- [ ] Temporary permission grants
- [ ] Permission inheritance system

## Support

For questions or issues:
- Check Django documentation: https://docs.djangoproject.com/en/5.2/topics/auth/
- Review code comments in `accounts/middleware/permissions.py`
- Contact development team

---

**Last Updated:** October 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
