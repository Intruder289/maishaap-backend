# Swagger Parameters Documentation Fix

## Problem
Some API endpoints in Swagger UI showed "No parameters" even though they accept query parameters, making it impossible to test them directly in Swagger UI.

## Root Cause
The wrapper function that converts `@swagger_auto_schema` (from `drf-yasg`) to `@extend_schema` (for `drf-spectacular`) was not reliably converting `manual_parameters` to `OpenApiParameter` objects for all endpoints, especially function-based views.

## Solution
Added `@extend_schema` decorators **directly** to all endpoints that use query parameters, ensuring parameters are properly documented in Swagger UI. The `@swagger_auto_schema` decorators were kept for backward compatibility but are now supplemented with direct `@extend_schema` decorators.

## Fixed Endpoints

### 1. `GET /api/v1/properties/` (PropertyListCreateAPIView.get)
**Query Parameters:**
- `property_type` (integer, optional) - Filter by property type ID
- `category` (string, optional) - Filter by category name
- `region` (integer, optional) - Filter by region ID
- `district` (integer, optional) - Filter by district ID
- `status` (string, optional) - Filter by status

**Fix:** Added `@extend_schema` directly to the `get()` method.

### 2. `GET /api/v1/search/` (property_search)
**Query Parameters:**
- `search` (string, optional) - Search query
- `property_type` (integer, optional) - Filter by property type ID
- `category` (string, optional) - Filter by category name
- `region` (integer, optional) - Filter by region ID
- `district` (integer, optional) - Filter by district ID
- `min_bedrooms` (integer, optional) - Minimum bedrooms
- `max_bedrooms` (integer, optional) - Maximum bedrooms
- `min_rent` (number, optional) - Minimum rent amount
- `max_rent` (number, optional) - Maximum rent amount
- `status` (string, optional) - Filter by status

**Fix:** Added `@extend_schema` directly after `@api_view` decorator.

### 3. `GET /api/v1/recent/` (recent_properties)
**Query Parameters:**
- `limit` (integer, optional) - Number of properties to return (default: 10)

**Fix:** Added `@extend_schema` directly after `@api_view` decorator.

### 4. `GET /api/v1/available-rooms/` (available_rooms_api)
**Query Parameters:**
- `property_id` (integer, **required**) - Property ID
- `check_in_date` (string, optional) - Check-in date (YYYY-MM-DD)
- `check_out_date` (string, optional) - Check-out date (YYYY-MM-DD)

**Fix:** Already had `@extend_schema` directly applied (fixed in previous session).

## Decorator Order (Critical)

For **function-based views**, the correct order is:
```python
@api_view(["GET"])
@permission_classes([AllowAny])
@extend_schema(...)  # Applied last, wraps everything
@swagger_auto_schema(...)  # Kept for backward compatibility
def my_view(request):
    ...
```

For **class-based views**, the correct order is:
```python
class MyAPIView(APIView):
    @extend_schema(...)  # Applied first to method
    @swagger_auto_schema(...)  # Kept for backward compatibility
    def get(self, request):
        ...
```

## Why This Works

1. **Direct Application**: `@extend_schema` is applied directly, bypassing the wrapper function's conversion logic which was unreliable.

2. **Proper Parameter Types**: Uses `OpenApiParameter` with correct types (`OpenApiTypes.INT`, `OpenApiTypes.STR`, `OpenApiTypes.NUMBER`) and locations (`OpenApiParameter.QUERY`).

3. **Decorator Order**: Ensures `@extend_schema` is applied at the correct point in the decorator chain so `drf-spectacular` can properly detect and document the parameters.

## Testing

After restarting the server, all fixed endpoints should now show their query parameters in Swagger UI:
1. Open Swagger UI: `http://127.0.0.1:8081/swagger/`
2. Navigate to each endpoint
3. Click "Try it out"
4. Verify all query parameters appear in the form

## Remaining Endpoints

Endpoints that **don't** use query parameters (like `featured_properties`, `property_stats`) correctly show "No parameters" as expected.

Endpoints that use **path parameters** (like `/properties/<int:pk>/`) correctly show path parameters in Swagger UI.

Endpoints that use **request body** (POST/PUT/PATCH) correctly show request body schemas in Swagger UI.

## Future Recommendations

1. **For new endpoints**: Always use `@extend_schema` directly instead of relying on the wrapper function.

2. **Migration path**: Gradually replace `@swagger_auto_schema` with `@extend_schema` for all endpoints to ensure consistency.

3. **Documentation**: Keep parameter descriptions clear and include examples where helpful.
