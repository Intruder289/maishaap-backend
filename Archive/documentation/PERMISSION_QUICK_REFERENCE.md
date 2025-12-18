# Permission Middleware - Quick Reference Card

## 🚀 Quick Start

### 1. Middleware is Already Enabled
The middleware is automatically protecting all pages. No action needed!

### 2. Using Decorators in Your Views

```python
from accounts.decorators import role_required, permission_required

# Protect by role
@role_required('Admin', 'Manager')
def my_admin_view(request):
    return render(request, 'template.html')

# Protect by permission
@permission_required('app.permission_codename')
def my_protected_view(request):
    return render(request, 'template.html')
```

### 3. Template Permission Checks

```django
{% if perms.properties.add_property %}
    <button>Add Property</button>
{% endif %}

{% if user.is_superuser %}
    <a href="/admin/">Admin Panel</a>
{% endif %}
```

## 📚 Common Decorators

| Decorator | Usage | When to Use |
|-----------|-------|-------------|
| `@role_required('Admin')` | Role restriction | Restrict to specific roles |
| `@permission_required('app.perm')` | Permission check | Fine-grained control |
| `@approved_user_required` | Approval check | Premium features |
| `@owner_or_admin_required` | Owner/Admin | User-owned resources |
| `@ajax_role_required('Admin')` | AJAX role | JSON endpoints |

## 🎯 Role Hierarchy

1. **Admin** - Full access to everything
2. **Manager** - Most features except role management
3. **Property Owner** - Property and tenant management
4. **Tenant** - View own data, create maintenance requests

## 🔐 Common Permissions

```python
# Properties
'properties.view_property'
'properties.add_property'
'properties.change_property'
'properties.delete_property'

# Users
'accounts.view_profile'
'accounts.change_profile'
'accounts.delete_profile'

# Roles
'accounts.view_customrole'
'accounts.add_customrole'
'accounts.change_customrole'
'accounts.delete_customrole'
```

## 🛠️ Adding New Protected Pages

### Option 1: In Middleware (Global)
Edit `accounts/middleware/permissions.py`:

```python
ROLE_REQUIRED_URLS = {
    'my_view_name': ['Admin', 'Manager'],
}
```

### Option 2: In View (Specific)
```python
@role_required('Admin', 'Manager')
def my_view(request):
    ...
```

## 📊 Check User Permissions

### In View
```python
# Check role
user_role = request.user.profile.get_primary_role()

# Check permission
has_perm = request.user.has_perm('app.permission')

# Check if admin
is_admin = user_role in ['Admin', 'Manager']
```

### In Template
```django
<!-- Check permission -->
{% if perms.app.permission %}
    <!-- Show button -->
{% endif %}

<!-- Check if superuser -->
{% if user.is_superuser %}
    <!-- Show admin link -->
{% endif %}
```

## 🎨 Custom 403 Page

When access is denied, users see a beautiful custom page at:
`accounts/templates/accounts/403.html`

Features:
- Clear error message
- Why access denied
- Dashboard and Back buttons
- Contact information

## 📝 Activity Logging

All important actions are automatically logged:

```python
from accounts.models import ActivityLog

# Get recent logs
logs = ActivityLog.objects.filter(
    user=request.user
).order_by('-timestamp')[:10]
```

## 🔍 Debug Permissions

```python
# See all user permissions
from accounts.PERMISSION_USAGE_EXAMPLES import get_user_permissions

permissions = get_user_permissions(request.user)
print(permissions)
```

## ⚠️ Common Mistakes

❌ **Don't**: Mix up role names  
✅ **Do**: Use exact role names: `'Admin'`, `'Manager'`, `'Property owner'`, `'Tenant'`

❌ **Don't**: Forget permission format  
✅ **Do**: Always use: `'app_label.permission_codename'`

❌ **Don't**: Stack too many decorators  
✅ **Do**: Use middleware for broad policies, decorators for specific views

## 🧪 Testing

```bash
# Test as different users
1. Login as Tenant → Try accessing admin page → Should show 403
2. Login as Manager → Try accessing role management → Should succeed
3. Login as Admin → Access everything → Should succeed
4. Logout → Try accessing dashboard → Should redirect to login
```

## 🆘 Troubleshooting

### Middleware not working?
1. Check `settings.py` MIDDLEWARE list
2. Restart Django server
3. Check middleware is after `AuthenticationMiddleware`

### 403 page not showing?
1. Verify template exists: `accounts/templates/accounts/403.html`
2. Clear browser cache
3. Check template settings

### Activity logs missing?
1. Run migrations: `python manage.py migrate`
2. Check middleware enabled
3. Verify POST/PUT/DELETE requests

## 📚 Full Documentation

- **Comprehensive Guide**: `PERMISSION_MIDDLEWARE_GUIDE.md`
- **Usage Examples**: `accounts/PERMISSION_USAGE_EXAMPLES.py`
- **Summary**: `PERMISSION_MIDDLEWARE_SUMMARY.md`
- **This Card**: `PERMISSION_QUICK_REFERENCE.md`

## 🎓 Remember

1. **Middleware** = Global protection (all pages)
2. **Decorators** = View-specific protection (one view)
3. **Templates** = UI visibility (show/hide buttons)
4. **Both** = Best practice (defense in depth)

## 🚀 Ready to Use!

The middleware is **ACTIVE** and protecting your application now!

Just add decorators to sensitive views for extra protection.

---

**Need Help?** Check the full documentation files or review the code comments.
