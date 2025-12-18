# Permission Middleware Fix - URL Namespace Issue

## Problem

After implementing the permission middleware, the application threw this error:

```
NoReverseMatch at /
Reverse for 'login' not found. 'login' is not a valid view function or pattern name.
```

## Root Cause

The accounts app uses a URL namespace (`app_name = 'accounts'` in `accounts/urls.py`), which means all URL names in that app must be referenced with the namespace prefix.

**Incorrect:** `reverse('login')`  
**Correct:** `reverse('accounts:login')`

## Files Fixed

### 1. accounts/middleware/permissions.py

**Line 248 - Login redirect:**
```python
# Before
return redirect(f"{reverse('login')}?next={request.path}")

# After
return redirect(f"{reverse('accounts:login')}?next={request.path}")
```

**Line 256 - Dashboard redirect:**
```python
# Before
return redirect('dashboard')

# After
return redirect('accounts:dashboard')
```

### 2. accounts/decorators.py

**Multiple locations - All login redirects:**
```python
# Before (4 instances)
return redirect(f"{reverse('login')}?next={request.path}")

# After
return redirect(f"{reverse('accounts:login')}?next={request.path}")
```

**Multiple locations - All dashboard redirects:**
```python
# Before (1 instance)
return redirect('dashboard')

# After
return redirect('accounts:dashboard')
```

### 3. accounts/templates/accounts/403.html

**Line 228 - Dashboard link:**
```django
<!-- Before -->
<a href="{% url 'dashboard' %}" class="btn-primary-action">

<!-- After -->
<a href="{% url 'accounts:dashboard' %}" class="btn-primary-action">
```

## Why This Happened

When a Django app defines `app_name`, it creates a URL namespace. This is a best practice for:
- Avoiding URL name conflicts between apps
- Making URL organization clearer
- Allowing multiple instances of the same app

## URL Namespace Reference

### In accounts/urls.py:
```python
app_name = 'accounts'  # This creates the namespace

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Full name: 'accounts:login'
    path('', views.dashboard, name='dashboard'),      # Full name: 'accounts:dashboard'
    # ...
]
```

### Usage in Code:
```python
# Python views
from django.urls import reverse
reverse('accounts:login')      # ✅ Correct
reverse('accounts:dashboard')  # ✅ Correct
reverse('login')               # ❌ Wrong - NoReverseMatch error

# Django templates
{% url 'accounts:login' %}      {# ✅ Correct #}
{% url 'accounts:dashboard' %}  {# ✅ Correct #}
{% url 'login' %}               {# ❌ Wrong #}
```

## All Accounts App URLs

Here are all the main URLs in the accounts app and their full names:

| URL Pattern | View Name | Full URL Name |
|-------------|-----------|---------------|
| `/login/` | login | `accounts:login` |
| `/logout/` | logout | `accounts:logout` |
| `/` | dashboard | `accounts:dashboard` |
| `/profile/` | profile | `accounts:profile` |
| `/users/` | user_list | `accounts:user_list` |
| `/roles/` | role_list | `accounts:role_list` |
| `/system-logs/` | system_logs | `accounts:system_logs` |

## Testing

After the fix:

1. ✅ Server starts without errors
2. ✅ Accessing `/` (dashboard) works
3. ✅ Middleware redirects work properly
4. ✅ 403 page links work correctly
5. ✅ Decorator redirects function as expected

## Prevention

To avoid this issue in the future:

1. **Always use namespaced URLs** when an app has `app_name` defined
2. **Check URL configuration** when adding new redirect logic
3. **Test middleware changes** by visiting protected pages
4. **Use IDE autocomplete** for URL names (shows namespace)

## Quick Reference

### Middleware & Decorators
When redirecting in middleware or decorators for the accounts app:
```python
# Login redirect
redirect(f"{reverse('accounts:login')}?next={request.path}")

# Dashboard redirect  
redirect('accounts:dashboard')
```

### Templates
When linking in templates:
```django
<a href="{% url 'accounts:login' %}">Login</a>
<a href="{% url 'accounts:dashboard' %}">Dashboard</a>
<a href="{% url 'accounts:profile' %}">Profile</a>
```

### Checking Active URL
```django
{% if request.resolver_match.url_name == 'dashboard' %}
    {# This works because url_name is just the name without namespace #}
{% endif %}
```

## Status

✅ **FIXED** - All URL references updated to use proper namespaces  
✅ **TESTED** - Server runs successfully  
✅ **VERIFIED** - Redirects work as expected

---

**Date Fixed:** October 15, 2025  
**Issue:** NoReverseMatch error for 'login'  
**Solution:** Updated all URL references to use 'accounts:' namespace prefix
