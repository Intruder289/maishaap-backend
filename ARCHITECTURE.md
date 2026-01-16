# Maisha Backend Architecture

## Enterprise-Grade Architecture (Best Practice)

This project follows a clean separation of concerns with three distinct layers:

### Layer 1: Web Views (HTML, Templates, AJAX)
**Purpose:** Server-rendered HTML pages and AJAX endpoints for web interface

**Location:**
- Django views: `*/views.py` (e.g., `properties/views.py`, `accounts/views.py`)
- Templates: `*/templates/`
- AJAX endpoints: `*/api_urls_ajax.py` → `/api/` (e.g., `/api/properties/...`)

**Characteristics:**
- Uses Django's template system
- Returns HTML responses
- AJAX endpoints return JSON but are NOT documented in Swagger
- Session-based authentication
- Not included in API documentation

**Example URLs:**
- `/properties/hotel/bookings/` - HTML page
- `/api/properties/available-rooms/` - AJAX endpoint (not in Swagger)

---

### Layer 2: API Layer (DRF-only)
**Purpose:** RESTful API endpoints for mobile applications (Flutter)

**Location:**
- DRF views: `*/api_views.py` (e.g., `properties/api_views.py`)
- API URLs: `*/api_urls.py` → `/api/v1/` (e.g., `/api/v1/properties/...`)

**Characteristics:**
- Uses Django REST Framework (DRF)
- Returns JSON responses
- JWT token authentication
- **Documented in Swagger**
- Follows RESTful conventions
- Versioned (`/api/v1/`)

**Example URLs:**
- `/api/v1/properties/` - List properties (in Swagger)
- `/api/v1/available-rooms/` - Get available rooms (in Swagger)

---

### Layer 3: Swagger Documentation
**Purpose:** API documentation for mobile app developers

**Location:**
- Schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/` or `/swagger/`
- ReDoc: `/api/schema/redoc/` or `/redoc/`

**Characteristics:**
- **ONLY documents DRF API endpoints** (`/api/v1/`)
- Excludes AJAX endpoints (`/api/`)
- Excludes web views (HTML pages)
- Auto-generated from DRF views/viewsets
- Uses `drf-spectacular` for OpenAPI 3.0 schema

**Configuration:**
- `SPECTACULAR_SETTINGS` in `settings.py`
- `api_patterns` in `urls.py` - defines which URLs to scan
- Schema view uses `patterns=api_patterns` to limit scope

---

## File Structure

```
Maisha_backend/
├── accounts/
│   ├── views.py              # Web views (HTML)
│   ├── api_views.py          # DRF API views (Swagger)
│   ├── api_urls.py           # API URLs (/api/v1/)
│   ├── api_urls_ajax.py      # AJAX URLs (/api/)
│   └── urls.py               # Web view URLs
├── properties/
│   ├── views.py              # Web views (HTML)
│   ├── api_views.py          # DRF API views (Swagger)
│   ├── api_urls.py           # API URLs (/api/v1/)
│   ├── api_urls_ajax.py      # AJAX URLs (/api/)
│   └── urls.py               # Web view URLs
└── Maisha_backend/
    ├── urls.py               # Root URLconf
    └── settings.py           # SPECTACULAR_SETTINGS
```

---

## URL Patterns

### API Layer (Swagger Documented)
```python
# In Maisha_backend/urls.py
api_patterns = [
    path('api/v1/', include('accounts.api_urls')),      # ✅ In Swagger
    path('api/v1/', include('properties.api_urls')),    # ✅ In Swagger
    path('api/v1/', include('payments.api_urls')),     # ✅ In Swagger
    # ... etc
]
```

### AJAX Endpoints (NOT in Swagger)
```python
# In Maisha_backend/urls.py
path('api/', include('properties.api_urls_ajax')),  # ❌ NOT in Swagger
```

### Web Views (NOT in Swagger)
```python
# In Maisha_backend/urls.py
path('properties/', include('properties.urls')),    # ❌ NOT in Swagger
path('payments/', include('payments.urls')),        # ❌ NOT in Swagger
```

---

## Best Practices

1. **Separation of Concerns**
   - Web views handle HTML rendering
   - API layer handles JSON responses
   - Swagger documents only the API layer

2. **Versioning**
   - API endpoints are versioned (`/api/v1/`)
   - Future versions: `/api/v2/`, `/api/v3/`, etc.

3. **Authentication**
   - Web views: Session-based
   - API layer: JWT tokens
   - Swagger: Bearer token authentication

4. **Documentation**
   - Use `@extend_schema` or `@swagger_auto_schema` for API endpoints
   - Keep descriptions clear and detailed
   - Include request/response examples

5. **Testing**
   - Test API endpoints via Swagger UI
   - Test web views via browser
   - Test AJAX endpoints via web interface

---

## Adding New Endpoints

### Adding a DRF API Endpoint (Swagger Documented)
1. Add view to `*/api_views.py` using DRF (`APIView`, `ViewSet`, `@api_view`)
2. Add URL to `*/api_urls.py` under `/api/v1/`
3. Add `@extend_schema` decorator for documentation
4. Endpoint will appear in Swagger automatically

### Adding an AJAX Endpoint (NOT Swagger Documented)
1. Add view to `*/views.py` or `*/api_views_ajax.py`
2. Add URL to `*/api_urls_ajax.py` under `/api/`
3. Endpoint will NOT appear in Swagger

### Adding a Web View (NOT Swagger Documented)
1. Add view to `*/views.py` (returns HTML)
2. Add URL to `*/urls.py`
3. Create template in `*/templates/`
4. View will NOT appear in Swagger

---

## Swagger Configuration

Swagger is configured to ONLY scan `api_patterns`:

```python
# In Maisha_backend/urls.py
path('api/schema/', SpectacularAPIView.as_view(patterns=api_patterns), name='schema'),
```

This ensures:
- ✅ Only `/api/v1/` endpoints appear in Swagger
- ❌ AJAX endpoints (`/api/`) are excluded
- ❌ Web views are excluded

---

## Summary

| Layer | URL Prefix | Framework | Swagger | Purpose |
|-------|-----------|-----------|---------|---------|
| Web Views | `/properties/`, `/payments/`, etc. | Django | ❌ | HTML pages |
| AJAX Endpoints | `/api/` | Django | ❌ | Web interface AJAX |
| API Layer | `/api/v1/` | DRF | ✅ | Mobile app API |
| Swagger | `/swagger/`, `/api/schema/` | drf-spectacular | - | API documentation |
