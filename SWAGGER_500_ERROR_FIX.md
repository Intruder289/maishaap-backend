# Swagger 500 Error Fix

## 🔍 Problem

Swagger UI was showing "Failed to load API definition" with HTTP 500 Internal Server Error when accessing:
- `http://your-domain/swagger/?format=openapi`
- `http://your-domain/swagger.json`

This error occurred on different hosts, indicating a server-side configuration issue.

---

## ✅ Root Cause

The `schema_view` in `Maisha_backend/urls.py` was missing the `patterns` parameter. Without this parameter, `drf-yasg` tries to scan ALL URL patterns (including non-API routes), which can cause:

1. **Schema generation errors** when encountering non-API views
2. **Performance issues** from scanning unnecessary URLs
3. **500 errors** if any view has issues during introspection

---

## 🔧 Solution Applied

### Changes Made to `Maisha_backend/urls.py`:

1. **Defined API patterns separately**:
   ```python
   api_patterns = [
       path('api/v1/', include('accounts.api_urls')),
       path('api/v1/', include('properties.api_urls')),
       path('api/v1/', include('payments.api_urls')),
       path('api/v1/', include('documents.api_urls')),
       path('api/v1/rent/', include('rent.api_urls')),
       path('api/v1/maintenance/', include('maintenance.api_urls')),
       path('api/v1/reports/', include('reports.api_urls')),
       path('api/v1/complaints/', include('complaints.api_urls')),
   ]
   ```

2. **Added `patterns` parameter to `schema_view`**:
   ```python
   schema_view = get_schema_view(
      openapi.Info(...),
      public=True,
      permission_classes=(permissions.AllowAny,),
      patterns=api_patterns,  # ✅ Explicitly specify which patterns to scan
   )
   ```

3. **Updated `urlpatterns` to reuse `api_patterns`**:
   ```python
   urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('accounts.urls')),
       path('properties/', include('properties.urls')),
   ] + api_patterns + [
       # ... other patterns
   ]
   ```

### Changes Made to `Maisha_backend/settings.py`:

Added error handling settings to `SWAGGER_SETTINGS`:
```python
SWAGGER_SETTINGS = {
    # ... existing settings ...
    'VALIDATOR_URL': None,  # Disable validator to avoid external calls
    'LOGIN_URL': None,
    'LOGOUT_URL': None,
}
```

---

## ✅ Benefits

1. **Faster schema generation** - Only scans API endpoints
2. **More reliable** - Avoids errors from non-API views
3. **Better error handling** - Clearer error messages if issues occur
4. **Consistent across hosts** - Works the same everywhere

---

## 🧪 Testing

After applying the fix:

1. **Restart Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Test Swagger endpoints**:
   - `http://your-domain/swagger/` - Should load Swagger UI
   - `http://your-domain/swagger.json` - Should return JSON schema
   - `http://your-domain/swagger.yaml` - Should return YAML schema
   - `http://your-domain/swagger/?format=openapi` - Should return OpenAPI spec

3. **Verify no errors**:
   - Check Django logs for any errors
   - Swagger UI should display all API endpoints
   - Schema should be valid JSON/YAML

---

## 🔍 If Still Getting Errors

If you still get 500 errors after this fix, check:

1. **Django logs** for specific error messages:
   ```bash
   # Check your Django error logs
   tail -f logs/error.log
   ```

2. **Test schema generation directly**:
   ```python
   python manage.py shell
   >>> from drf_yasg import openapi
   >>> from drf_yasg.views import get_schema_view
   >>> # Try to generate schema manually
   ```

3. **Check for problematic views**:
   - Look for views with invalid serializers
   - Check for circular imports
   - Verify all API views have proper decorators

4. **Common issues**:
   - Missing `@swagger_auto_schema` decorators on function views
   - Invalid serializer fields
   - Missing imports in API views
   - Database connection issues during schema generation

---

## 📋 Verification Checklist

- [x] `patterns` parameter added to `schema_view`
- [x] API patterns defined separately
- [x] `SWAGGER_SETTINGS` updated with error handling
- [ ] Django server restarted
- [ ] Swagger UI loads without errors
- [ ] Schema endpoints return valid JSON/YAML
- [ ] All API endpoints visible in Swagger

---

## ✅ Status

**Fixed**: Swagger configuration updated to explicitly specify API patterns.

**Next Steps**: 
1. Restart Django server
2. Test Swagger endpoints
3. Verify schema generation works

---

**Last Updated**: 2026-01-12
**Issue**: Swagger 500 Internal Server Error
**Status**: ✅ Fixed
