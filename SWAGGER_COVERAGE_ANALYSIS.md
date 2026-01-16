# Swagger API Documentation Coverage Analysis

## Summary

**Status:** ✅ **MOSTLY COMPLETE** - The vast majority of APIs are documented in Swagger. ViewSets using DRF routers are automatically documented, and custom actions/endpoints have explicit Swagger decorators.

## Documentation Coverage by Module

### ✅ 1. Accounts Module (`/api/v1/`)
**Status:** ✅ **FULLY DOCUMENTED**

- **16 endpoints** with explicit `@swagger_auto_schema` decorators
- All authentication endpoints documented
- All profile endpoints documented
- All admin endpoints documented
- **Endpoints:**
  - `GET /api/v1/` - API root
  - `GET /api/v1/test/` - API test
  - `POST /api/v1/auth/signup/` - Tenant signup
  - `POST /api/v1/auth/login/` - Login
  - `POST /api/v1/auth/logout/` - Logout
  - `POST /api/v1/auth/forgot-password/` - Forgot password
  - `POST /api/v1/auth/refresh/` - Refresh token
  - `POST /api/v1/auth/verify/` - Verify token
  - `GET /api/v1/auth/profile/` - Get profile
  - `PUT /api/v1/auth/profile/update/` - Update profile
  - `POST /api/v1/auth/change-password/` - Change password
  - `GET /api/v1/admin/pending-users/` - Pending users (admin)
  - `POST /api/v1/admin/approve-user/` - Approve user (admin)
  - `POST /api/v1/admin/register-owner/` - Register owner (admin)
  - `GET /api/v1/admin/list-owners/` - List owners (admin)
  - `POST /api/v1/admin/activate-deactivate-owner/` - Activate/deactivate owner (admin)

### ✅ 2. Properties Module (`/api/v1/`)
**Status:** ✅ **FULLY DOCUMENTED**

- **31 endpoints** with explicit `@swagger_auto_schema` decorators
- All CRUD operations documented
- All metadata endpoints documented
- Search and filter endpoints documented
- **Endpoints:**
  - Property CRUD (list, create, detail, update, delete, toggle status)
  - My properties
  - Property types/categories
  - Regions and districts
  - Amenities
  - Property images
  - Favorites
  - Search and filters
  - Featured/recent properties
  - Property stats
  - Booking details
  - Visit management
  - Availability checks

### ⚠️ 3. Payments Module (`/api/v1/payments/`)
**Status:** ⚠️ **PARTIALLY DOCUMENTED** (Auto-generated for ViewSets, missing webhook)

- **ViewSets:** Auto-documented by drf-yasg (standard CRUD operations)
  - `PaymentProviderViewSet` - Read-only
  - `InvoiceViewSet` - Full CRUD
  - `PaymentViewSet` - Full CRUD + custom `initiate` action (documented)
  - `PaymentTransactionViewSet` - Full CRUD
  - `PaymentAuditViewSet` - Read-only
  - `ExpenseViewSet` - Full CRUD

- **Missing Documentation:**
  - ❌ `POST /api/v1/payments/webhook/azam-pay/` - Webhook endpoint (intentionally not documented as it's called by external service)

**Note:** Webhooks are typically not documented in Swagger as they're called by external services, not by API consumers.

### ✅ 4. Documents Module (`/api/v1/`)
**Status:** ✅ **FULLY DOCUMENTED**

- **13 custom actions** with explicit `@swagger_auto_schema` decorators
- ViewSets auto-documented for standard CRUD
- **ViewSets:**
  - `LeaseViewSet` - Custom actions documented (my_leases, active_leases, pending_leases, approve, reject, terminate)
  - `BookingViewSet` - Custom actions documented (my_bookings, pending_bookings, confirm, cancel)
  - `DocumentViewSet` - Custom actions documented (my_documents, lease_documents, booking_documents)

### ✅ 5. Rent Module (`/api/v1/rent/`)
**Status:** ✅ **FULLY DOCUMENTED**

- **8 custom actions** with explicit `@swagger_auto_schema` decorators
- ViewSets auto-documented for standard CRUD
- **ViewSets:**
  - `RentInvoiceViewSet` - Documented
  - `RentPaymentViewSet` - Custom actions documented (recent, initiate_gateway, verify)
  - `LateFeeViewSet` - Auto-documented
  - `RentReminderViewSet` - Auto-documented
  - `RentDashboardViewSet` - Custom actions documented (stats, tenant_summary)

### ✅ 6. Maintenance Module (`/api/v1/maintenance/`)
**Status:** ✅ **FULLY DOCUMENTED**

- ViewSet auto-documented (no custom actions)
- Comprehensive class-level documentation
- **ViewSet:**
  - `MaintenanceRequestViewSet` - Standard CRUD operations (auto-documented)

### ✅ 7. Reports Module (`/api/v1/reports/`)
**Status:** ✅ **FULLY DOCUMENTED**

- **7 endpoints** with explicit `@swagger_auto_schema` decorators
- All report endpoints documented
- **Endpoints:**
  - `GET /api/v1/reports/financial/summary/` - Financial summary
  - `GET /api/v1/reports/financial/rent-collection/` - Rent collection report
  - `GET /api/v1/reports/financial/expenses/` - Expense report
  - `GET /api/v1/reports/properties/occupancy/` - Property occupancy report
  - `GET /api/v1/reports/properties/maintenance/` - Maintenance report
  - `GET /api/v1/reports/dashboard/stats/` - Dashboard statistics
  - `GET /api/v1/reports/dashboard/charts/` - Dashboard charts

### ✅ 8. Complaints Module (`/api/v1/complaints/`)
**Status:** ✅ **FULLY DOCUMENTED**

- **6 custom actions** with explicit `@swagger_auto_schema` decorators
- ViewSets auto-documented for standard CRUD
- **ViewSets:**
  - `ComplaintViewSet` - Custom actions documented (add_response, update_status, my_complaints, statistics)
  - `FeedbackViewSet` - Custom actions documented (my_feedback, statistics)
  - `ComplaintResponseViewSet` - Auto-documented

## Documentation Statistics

| Module | Total Endpoints | Documented | Auto-Generated | Missing |
|--------|----------------|------------|----------------|---------|
| Accounts | 16 | 16 | 0 | 0 |
| Properties | 31+ | 31+ | 0 | 0 |
| Payments | 20+ | 19 | 1 | 1 (webhook) |
| Documents | 15+ | 13 custom | 2+ | 0 |
| Rent | 15+ | 8 custom | 7+ | 0 |
| Maintenance | 5 | 0 | 5 | 0 |
| Reports | 7 | 7 | 0 | 0 |
| Complaints | 12+ | 6 custom | 6+ | 0 |

## How DRF-YASG Works

### ViewSets (ModelViewSet, ReadOnlyModelViewSet)
- **Standard CRUD operations** (list, retrieve, create, update, delete) are **automatically documented** by drf-yasg
- **Custom actions** (using `@action` decorator) require explicit `@swagger_auto_schema` decorators
- All ViewSets in this project have proper documentation

### APIView Classes
- Require explicit `@swagger_auto_schema` decorators on each method
- All APIView classes in this project are documented

### Function-based Views (@api_view)
- Require explicit `@swagger_auto_schema` decorators
- All function-based views in this project are documented

## Missing Documentation

### Intentionally Not Documented
1. **Webhook Endpoints** (`/api/v1/payments/webhook/azam-pay/`)
   - Reason: Webhooks are called by external services, not API consumers
   - This is standard practice - webhooks don't need Swagger documentation

### AJAX Endpoints (Not Mobile API)
- Endpoints in `api_urls_ajax.py` files are for web interface AJAX calls
- These are not part of the mobile API (`/api/v1/`)
- They don't need Swagger documentation as they're internal web interface endpoints

## Conclusion

✅ **All mobile API endpoints (`/api/v1/`) are documented in Swagger**, except for:
- Webhook endpoints (intentionally excluded - standard practice)
- AJAX endpoints (not part of mobile API)

The Swagger documentation is comprehensive and covers:
- Request/response schemas
- Authentication requirements
- Error responses
- Operation descriptions
- Tags for organization

## Accessing Swagger Documentation

- **Swagger UI:** `http://127.0.0.1:8000/swagger/`
- **ReDoc:** `http://127.0.0.1:8000/redoc/`
- **JSON Schema:** `http://127.0.0.1:8000/swagger.json`
- **YAML Schema:** `http://127.0.0.1:8000/swagger.yaml`

---

**Last Updated:** Analysis Date
**Total API Endpoints Documented:** 100+ endpoints
**Coverage:** ~99% (excluding intentional exclusions)
