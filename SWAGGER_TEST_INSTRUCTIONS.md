# Testing Swagger Parameters Display

## ✅ Code Verification Complete

All endpoints have been fixed with proper `@extend_schema` decorators:

1. **`GET /api/v1/available-rooms/`** - 3 parameters ✅
2. **`GET /api/v1/search/`** - 9 parameters ✅  
3. **`GET /api/v1/recent/`** - 1 parameter ✅
4. **`GET /api/v1/properties/`** - 5 parameters ✅

## 🧪 Manual Testing Steps

### Step 1: Restart Django Server
```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

### Step 2: Open Swagger UI
Navigate to: `http://127.0.0.1:8081/swagger/`

### Step 3: Test Each Endpoint

#### Test 1: `GET /api/v1/available-rooms/`
1. Find the endpoint in Swagger UI
2. **Expected:** Should show 3 query parameters:
   - `property_id` (required, integer)
   - `check_in_date` (optional, string)
   - `check_out_date` (optional, string)
3. Click **"Try it out"**
4. **Expected:** Input fields should appear for all 3 parameters
5. **Test:** Enter `property_id=1` and click "Execute"
6. **Expected:** Should return a response (not an error about missing parameters)

#### Test 2: `GET /api/v1/search/`
1. Find the endpoint in Swagger UI
2. **Expected:** Should show 9 query parameters:
   - `search`, `property_type`, `category`, `region`, `district`
   - `min_bedrooms`, `max_bedrooms`, `min_rent`, `max_rent`, `status`
3. Click **"Try it out"**
4. **Expected:** Input fields should appear for all 9 parameters
5. **Test:** Enter `search=hotel` and click "Execute"
6. **Expected:** Should return filtered results

#### Test 3: `GET /api/v1/recent/`
1. Find the endpoint in Swagger UI
2. **Expected:** Should show 1 query parameter:
   - `limit` (optional, integer)
3. Click **"Try it out"**
4. **Expected:** Input field should appear for `limit`
5. **Test:** Enter `limit=5` and click "Execute"
6. **Expected:** Should return 5 recent properties

#### Test 4: `GET /api/v1/properties/`
1. Find the endpoint in Swagger UI
2. **Expected:** Should show 5 query parameters:
   - `property_type`, `category`, `region`, `district`, `status`
3. Click **"Try it out"**
4. **Expected:** Input fields should appear for all 5 parameters
5. **Test:** Enter `category=hotel` and click "Execute"
6. **Expected:** Should return filtered hotel properties

## ✅ Success Criteria

For each endpoint, you should see:
- ✅ Parameters listed (not "No parameters")
- ✅ Correct parameter types (integer, string, number)
- ✅ Required/optional status shown correctly
- ✅ Input fields appear when clicking "Try it out"
- ✅ Can successfully execute requests with parameters

## ❌ If Parameters Still Don't Show

If you still see "No parameters":

1. **Check server logs** for any errors
2. **Clear browser cache** and hard refresh (Ctrl+F5)
3. **Verify drf-spectacular is installed:**
   ```bash
   pip list | grep drf-spectacular
   ```
4. **Check settings.py** has:
   ```python
   INSTALLED_APPS = [
       ...
       'drf_spectacular',
   ]
   
   REST_FRAMEWORK = {
       'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
   }
   ```
5. **Regenerate schema:**
   ```bash
   python manage.py spectacular --color --file schema.yml
   ```

## 📝 Expected Swagger UI Appearance

When you click on an endpoint, you should see:

```
GET /api/v1/available-rooms/

Get Available Rooms

Query Parameters:
┌─────────────────┬──────────┬─────────┬─────────────────────────────┐
│ Name            │ Type     │ Required│ Description                 │
├─────────────────┼──────────┼─────────┼─────────────────────────────┤
│ property_id     │ integer  │ Yes     │ Property ID (required)      │
│ check_in_date   │ string   │ No      │ Check-in date (YYYY-MM-DD)  │
│ check_out_date  │ string   │ No      │ Check-out date (YYYY-MM-DD)│
└─────────────────┴──────────┴─────────┴─────────────────────────────┘

[Try it out] button
```

## 🎯 Quick Verification Checklist

- [ ] Server restarted after code changes
- [ ] Swagger UI loads without errors
- [ ] Endpoints are visible in Swagger UI
- [ ] Parameters show (not "No parameters")
- [ ] "Try it out" button works
- [ ] Input fields appear for all parameters
- [ ] Can execute requests successfully

---

**Status:** Code is ready. Please test in Swagger UI and report results.
