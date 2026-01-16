# Fix: "No Parameters" in Swagger UI

## Problem

Some API endpoints in Swagger UI show "No parameters" even though they accept query parameters.

## Root Causes

### 1. **Wrapper Function Issue**
The `swagger_auto_schema` wrapper converts `drf-yasg` decorators to `drf-spectacular`, but there might be issues with:
- Parameter conversion
- Decorator application order
- Handling of `method` parameter

### 2. **Missing Decorators**
Some endpoints don't have `@swagger_auto_schema` decorators at all:
- `featured_properties` - No decorator (but also no query params, so OK)
- Some endpoints might be missing decorators

### 3. **Decorator Order**
For `@api_view` function-based views, the decorator order matters:
```python
# ✅ Correct order
@swagger_auto_schema(...)
@api_view(["GET"])
@permission_classes([AllowAny])
def my_function(request):
    ...

# ❌ Wrong order (decorator won't apply correctly)
@api_view(["GET"])
@swagger_auto_schema(...)
@permission_classes([AllowAny])
def my_function(request):
    ...
```

## Solution

### Step 1: Fix Wrapper Function

The wrapper function needs to properly handle the decorator pattern:

```python
def swagger_auto_schema(*args, **kwargs):
    # Handle method parameter - drf-spectacular doesn't need it
    method = kwargs.pop('method', None)
    
    # Extract and convert parameters...
    # ...
    
    # Return extend_schema decorator
    return extend_schema(
        summary=kwargs.get('operation_summary', ''),
        description=kwargs.get('operation_description', ''),
        tags=kwargs.get('tags', []),
        parameters=spectacular_params if spectacular_params else None,
        responses=kwargs.get('responses', {})
    )
```

### Step 2: Verify Decorator Order

Ensure all `@api_view` endpoints have decorators in the correct order:

```python
@swagger_auto_schema(
    method='get',  # Specify HTTP method
    manual_parameters=[
        openapi.Parameter('param_name', openapi.IN_QUERY, ...),
    ],
    ...
)
@api_view(["GET"])
@permission_classes([AllowAny])
def my_endpoint(request):
    ...
```

### Step 3: Check Parameter Objects

Ensure `openapi.Parameter` objects are created correctly:

```python
openapi.Parameter(
    'property_id',           # name
    openapi.IN_QUERY,        # location
    description="...",       # description
    type=openapi.TYPE_INTEGER,  # type
    required=True            # required
)
```

## Testing

After fixing, test these endpoints in Swagger:

1. **`GET /api/v1/properties/search/`**
   - Should show: `search`, `property_type`, `category`, `region`, `district`, `min_bedrooms`, `max_bedrooms`, `min_rent`, `max_rent`, `status`

2. **`GET /api/v1/properties/`**
   - Should show: `property_type`, `category`, `region`, `district`, `status`

3. **`GET /api/v1/available-rooms/`**
   - Should show: `property_id`, `check_in_date`, `check_out_date`

4. **`GET /api/v1/properties/recent/`**
   - Should show: `limit`

## Common Issues

### Issue 1: Parameters Not Showing
**Symptom:** Endpoint shows "No parameters" in Swagger

**Causes:**
- Missing `@swagger_auto_schema` decorator
- `manual_parameters` not defined
- Wrapper function not converting parameters correctly
- Decorator order incorrect

**Fix:**
- Add `@swagger_auto_schema` with `manual_parameters`
- Ensure decorator is before `@api_view`
- Check wrapper function converts parameters correctly

### Issue 2: Parameters Show But Can't Enter Values
**Symptom:** Parameters listed but no input fields in Swagger UI

**Causes:**
- `drf-spectacular` not detecting parameters correctly
- Parameter conversion issue in wrapper

**Fix:**
- Use `@extend_schema` directly instead of wrapper
- Or fix wrapper to properly convert to `OpenApiParameter`

### Issue 3: Wrong Parameter Types
**Symptom:** Parameters show but with wrong types (all strings)

**Causes:**
- Type conversion in wrapper not working
- `openapi.TYPE_INTEGER` not being converted to `OpenApiTypes.INT`

**Fix:**
- Check type conversion logic in wrapper
- Ensure `param.type` is being read correctly

## Quick Fix Checklist

- [ ] Verify wrapper function handles `method` parameter
- [ ] Check all endpoints have `@swagger_auto_schema` decorators
- [ ] Ensure decorator order is correct (`@swagger_auto_schema` before `@api_view`)
- [ ] Verify `openapi.Parameter` objects are created correctly
- [ ] Test endpoints in Swagger UI
- [ ] Check parameter types are correct (integer, string, etc.)

## Alternative: Use `@extend_schema` Directly

If the wrapper continues to have issues, you can use `drf-spectacular`'s `@extend_schema` directly:

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@extend_schema(
    summary="Get Available Rooms",
    parameters=[
        OpenApiParameter(
            name='property_id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description='Property ID (required)',
            required=True
        ),
    ],
)
@api_view(["GET"])
def available_rooms_api(request):
    ...
```

This bypasses the wrapper entirely and ensures parameters are documented correctly.
