# Swagger Static Files 404 Error - Fix

## 🔍 Problem

Swagger UI shows blank page because static files (CSS/JS) return 404:
- `/static/drf-yasg/style.css` → 404
- `/static/drf-yasg/swagger-ui-dist/swagger-ui-bundle.js` → 404
- All drf-yasg static files → 404

## ✅ Solution Applied

Updated `Maisha_backend/urls.py` to serve static files from `STATIC_ROOT`:

```python
if settings.DEBUG:
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files in development (including drf-yasg static files)
    # Serve from STATIC_ROOT where collectstatic puts all static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

## 🔧 Steps to Fix

1. **Static files are already collected** ✅
   - Files exist in `staticfiles/drf-yasg/`
   - Verified: `staticfiles/drf-yasg/style.css` exists

2. **URL configuration updated** ✅
   - Changed from `staticfiles_urlpatterns()` to explicit `static()` helper
   - Now serves from `STATIC_ROOT` directory

3. **Restart Django server** ⚠️ **REQUIRED**
   ```bash
   # Stop server (CTRL+C or CTRL+BREAK)
   # Then restart:
   python manage.py runserver 8081
   ```

## ✅ After Restart

You should see in logs:
```
[XX/Jan/2026 XX:XX:XX] "GET /static/drf-yasg/style.css HTTP/1.1" 200 ...
[XX/Jan/2026 XX:XX:XX] "GET /static/drf-yasg/swagger-ui-dist/swagger-ui-bundle.js HTTP/1.1" 200 ...
```

Instead of 404 errors.

## 🧪 Verification

After restarting:
1. Visit: `http://127.0.0.1:8081/swagger/`
2. Check browser console (F12) - should show no 404 errors
3. Swagger UI should load with full styling

---

**Status**: ✅ Configuration Fixed
**Action Required**: Restart Django server
