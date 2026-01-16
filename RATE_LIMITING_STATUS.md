# API Rate Limiting Status

## ✅ **IMPLEMENTED** - Rate Limiting is Already Configured

Rate limiting is **fully implemented** in the Maisha Backend API using Django REST Framework's throttling system.

---

## Configuration

### Global Settings (`Maisha_backend/settings.py`)

```python
REST_FRAMEWORK = {
    # ... other settings ...
    
    # Rate limiting/throttling configuration
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',  # For anonymous users
        'rest_framework.throttling.UserRateThrottle'   # For authenticated users
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',      # Anonymous users: 100 requests per hour
        'user': '1000/hour',     # Authenticated users: 1000 requests per hour
        'auth': '10/minute',     # Authentication endpoints: 10 requests per minute
        'search': '30/minute',   # Search endpoints: 30 requests per minute
    },
}
```

---

## Rate Limits Summary

| User Type | Rate Limit | Scope |
|-----------|-----------|-------|
| **Anonymous** | 100/hour | All endpoints |
| **Authenticated** | 1000/hour | All endpoints (default) |
| **Auth Endpoints** | 10/minute | Login, signup, password reset, token refresh |
| **Search Endpoints** | 30/minute | Property search (if implemented) |

---

## Custom Throttle Classes

### 1. AuthRateThrottle (`accounts/api_views.py`)

**Rate:** `10/minute`

**Applied to:**
- ✅ `POST /api/v1/accounts/signup/` - User registration
- ✅ `POST /api/v1/accounts/login/` - User login
- ✅ `POST /api/v1/accounts/forgot-password/` - Password reset request
- ✅ `POST /api/v1/accounts/refresh-token/` - Token refresh
- ✅ `POST /api/v1/accounts/verify-token/` - Token verification

**Implementation:**
```python
class AuthRateThrottle(UserRateThrottle):
    """Custom throttle for authentication endpoints"""
    rate = '10/minute'

@throttle_classes([AuthRateThrottle])
def tenant_signup(request):
    # ...
```

---

### 2. SearchRateThrottle (`accounts/api_views.py`)

**Rate:** `30/minute`

**Status:** ⚠️ **Defined but not currently applied**

**Note:** The `SearchRateThrottle` class is defined but not yet applied to search endpoints. Consider applying it to:
- `GET /api/v1/properties/search/` - Property search endpoint

---

## How It Works

### Default Behavior

1. **All API endpoints** (`/api/v1/`) automatically use:
   - `AnonRateThrottle` for anonymous users (100/hour)
   - `UserRateThrottle` for authenticated users (1000/hour)

2. **Authentication endpoints** use stricter limits:
   - `AuthRateThrottle` (10/minute) to prevent brute force attacks

### Throttle Headers

When rate limits are exceeded, DRF returns:
- **HTTP 429 Too Many Requests**
- Headers:
  - `X-Throttle-Wait-Seconds`: Time to wait before retrying
  - `Retry-After`: Time to wait (in seconds)

### Example Response (Rate Limited)

```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

Headers:
```
HTTP/1.1 429 Too Many Requests
X-Throttle-Wait-Seconds: 3600
Retry-After: 3600
```

---

## Recommendations

### ✅ Already Implemented
- [x] Global rate limiting for all endpoints
- [x] Separate limits for anonymous vs authenticated users
- [x] Stricter limits for authentication endpoints
- [x] Custom throttle classes for specific endpoint types

### 🔄 Potential Improvements

1. **Apply SearchRateThrottle to Search Endpoints**
   ```python
   # In properties/api_views.py
   from accounts.api_views import SearchRateThrottle
   
   @throttle_classes([SearchRateThrottle])
   def property_search(request):
       # ...
   ```

2. **Add Throttle Scope for Different Endpoint Types**
   ```python
   # In settings.py
   'DEFAULT_THROTTLE_RATES': {
       'anon': '100/hour',
       'user': '1000/hour',
       'auth': '10/minute',
       'search': '30/minute',
       'upload': '20/hour',      # For file uploads
       'payment': '50/hour',     # For payment endpoints
   }
   ```

3. **Consider IP-Based Throttling for Public Endpoints**
   ```python
   from rest_framework.throttling import ScopedRateThrottle
   
   class IPRateThrottle(ScopedRateThrottle):
       scope = 'anon'
   ```

4. **Add Throttle Information to Swagger Documentation**
   - Document rate limits in endpoint descriptions
   - Include throttle information in OpenAPI schema

---

## Testing Rate Limits

### Test Anonymous Rate Limit (100/hour)

```bash
# Make 101 requests quickly
for i in {1..101}; do
    curl http://127.0.0.1:8081/api/v1/properties/
done

# 101st request should return 429
```

### Test Authentication Rate Limit (10/minute)

```bash
# Make 11 login attempts quickly
for i in {1..11}; do
    curl -X POST http://127.0.0.1:8081/api/v1/accounts/login/ \
         -H "Content-Type: application/json" \
         -d '{"email":"test@example.com","password":"wrong"}'
done

# 11th request should return 429
```

### Test Authenticated User Rate Limit (1000/hour)

```bash
# Get token first
TOKEN=$(curl -X POST http://127.0.0.1:8081/api/v1/accounts/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}' \
     | jq -r '.access')

# Make 1001 requests
for i in {1..1001}; do
    curl http://127.0.0.1:8081/api/v1/properties/ \
         -H "Authorization: Bearer $TOKEN"
done

# 1001st request should return 429
```

---

## Production Considerations

### 1. **Cache Backend**
Rate limiting uses Django's cache. Ensure you have a proper cache backend configured:

```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 2. **Distributed Systems**
If running multiple server instances, use a shared cache (Redis) to ensure rate limits are consistent across all servers.

### 3. **Monitoring**
Monitor rate limit hits:
- Track 429 responses
- Alert on unusual patterns
- Log throttle violations

### 4. **Adjust Limits Based on Usage**
- Monitor actual usage patterns
- Adjust limits based on legitimate use cases
- Consider different limits for different user tiers (free vs premium)

---

## Summary

✅ **Rate limiting is fully implemented and working**

- Global limits: 100/hour (anon), 1000/hour (auth)
- Auth endpoints: 10/minute (stricter)
- Custom throttle classes defined
- Ready for production use

**Optional Enhancement:** Apply `SearchRateThrottle` to search endpoints if needed.
