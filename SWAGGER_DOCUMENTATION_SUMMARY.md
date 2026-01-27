# Swagger Documentation Summary

## Overview

All API endpoints have been fully documented in Swagger/OpenAPI. This document provides a comprehensive summary of all documented endpoints.

---

## Lease APIs

### 1. **Create Lease** ✅
**Endpoint:** `POST /api/v1/leases/`

**Documentation:**
- ✅ Request body schema documented (`LeaseCreateSerializer`)
- ✅ Response schema documented (`LeaseSerializer`)
- ✅ **Important:** Response includes `id` field (lease ID)
- ✅ Response includes `payment_status` field
- ✅ Documents that non-staff users get 'active' status automatically

**Swagger Tags:** `['Leases']`

---

### 2. **List Leases** ✅
**Endpoint:** `GET /api/v1/leases/`

**Documentation:**
- ✅ Response schema documented (`LeaseSerializer`)
- ✅ **Important:** Response includes `payment_status` field
- ✅ Documents filtering parameters (status, property_ref, tenant, search, ordering)
- ✅ Documents user role-based filtering
- ✅ Explains payment_status calculation

**Swagger Tags:** `['Leases']`

**Query Parameters Documented:**
- `status` - Filter by lease status
- `property_ref` - Filter by property ID
- `tenant` - Filter by tenant user ID
- `search` - Search by property name, tenant username/email
- `ordering` - Order results by field

---

### 3. **Retrieve Lease** ✅
**Endpoint:** `GET /api/v1/leases/{id}/`

**Documentation:**
- ✅ Response schema documented (`LeaseSerializer`)
- ✅ **Important:** Response includes `payment_status` field
- ✅ Documents payment_status calculation logic
- ✅ Explains payment_status values ('paid', 'partial', 'unpaid')

**Swagger Tags:** `['Leases']`

---

## Rent Payment APIs

### 4. **Create Rent Payment** ✅
**Endpoint:** `POST /api/v1/rent/payments/`

**Documentation:**
- ✅ Request body schema documented (`RentPaymentCreateSerializer`)
- ✅ Response schema documented (`RentPaymentSerializer`)
- ✅ **Documents TWO payment flows:**
  - **Option 1:** Payment with Invoice (Structured)
  - **Option 2:** Payment without Invoice (Flexible)
- ✅ Documents that either `rent_invoice` OR `lease` must be provided
- ✅ Documents invoice auto-creation for lease-only payments
- ✅ Documents validation rules for both flows
- ✅ Documents response differences for each flow

**Swagger Tags:** `['Rent']`

**Request Body Fields Documented:**
- `rent_invoice` - Optional: Invoice ID
- `lease` - Optional: Lease ID (required if rent_invoice not provided)
- `amount` - Required: Payment amount
- `payment_method` - Required: cash, mobile_money, online
- `mobile_money_provider` - Required for mobile_money: AIRTEL, TIGO, MPESA, HALOPESA
- `reference_number` - Optional
- `notes` - Optional

---

### 5. **List Rent Payments** ✅
**Endpoint:** `GET /api/v1/rent/payments/`

**Documentation:**
- ✅ Response schema documented (`RentPaymentSerializer`)
- ✅ Documents that it returns both invoice-based and lease-only payments
- ✅ Documents filtering parameters
- ✅ Documents user role-based filtering

**Swagger Tags:** `['Rent']`

**Query Parameters Documented:**
- `tenant_id` - Filter by tenant (admin/staff only)
- `invoice_id` - Filter by rent invoice
- `lease_id` - Filter by lease
- `payment_method` - Filter by payment method

---

### 6. **Retrieve Rent Payment** ✅
**Endpoint:** `GET /api/v1/rent/payments/{id}/`

**Documentation:**
- ✅ Response schema documented (`RentPaymentSerializer`)
- ✅ Documents that it works for both invoice-based and lease-only payments
- ✅ Documents response includes invoice or lease information

**Swagger Tags:** `['Rent']`

---

### 7. **Initiate Gateway Payment** ✅
**Endpoint:** `POST /api/v1/rent/payments/{id}/initiate-gateway/`

**Documentation:**
- ✅ Request body schema documented (mobile_money_provider)
- ✅ Response schema documented
- ✅ **Important:** Documents that it works WITHOUT invoices
- ✅ Documents that invoice will be auto-created when payment completes
- ✅ Documents mobile money provider options
- ✅ Documents error responses

**Swagger Tags:** `['Rent']`

**Request Body Fields Documented:**
- `mobile_money_provider` - Optional if already set on payment: AIRTEL, TIGO, MPESA, HALOPESA

**Response Fields Documented:**
- `success` - Boolean
- `payment_id` - Integer
- `transaction_id` - Integer
- `payment_link` - String (URL to redirect user)
- `transaction_reference` - String
- `message` - String

---

### 8. **Get Recent Rent Payments** ✅
**Endpoint:** `GET /api/v1/rent/payments/recent/`

**Documentation:**
- ✅ Response schema documented (`RentPaymentSerializer`)
- ✅ Documents query parameter `limit` (default: 10)
- ✅ Documents that it returns both invoice-based and lease-only payments

**Swagger Tags:** `['Rent']`

**Query Parameters Documented:**
- `limit` - Number of recent payments to return (default: 10)

---

## User Account APIs

### 9. **Delete User Account** ✅
**Endpoint:** `DELETE/POST /api/v1/accounts/auth/delete-account/`

**Documentation:**
- ✅ Request method documented (DELETE or POST)
- ✅ Response schema documented
- ✅ Documents Play Store compliance requirement
- ✅ Documents that users can only delete their own account
- ✅ Documents that action is permanent
- ✅ Documents authentication requirement

**Swagger Tags:** `['User Account']`

**Response Fields Documented:**
- `success` - Boolean
- `message` - String

---

## Serializer Documentation

### RentPaymentCreateSerializer ✅
**Location:** `rent/serializers.py`

**Fields Documented:**
- `rent_invoice` - Optional: Invoice ID (help_text provided)
- `lease` - Optional: Lease ID (help_text provided)
- `amount` - Required: Payment amount
- `payment_method` - Required: Payment method
- `mobile_money_provider` - Required for mobile_money
- `reference_number` - Optional
- `notes` - Optional

**Docstring:**
- ✅ Explains two payment options
- ✅ Documents that either rent_invoice OR lease must be provided
- ✅ Documents invoice auto-creation behavior

---

### LeaseSerializer ✅
**Location:** `documents/serializers.py`

**Fields Documented:**
- ✅ All fields including `payment_status`
- ✅ `payment_status` is a `SerializerMethodField` (calculated)
- ✅ Docstring explains payment_status calculation

---

## Summary Checklist

### Lease Endpoints:
- [x] Create Lease - Documented with ID and payment_status in response
- [x] List Leases - Documented with payment_status field
- [x] Retrieve Lease - Documented with payment_status field

### Payment Endpoints:
- [x] Create Payment - Documented with both payment flows
- [x] List Payments - Documented with filtering options
- [x] Retrieve Payment - Documented
- [x] Initiate Gateway - Documented (works without invoice)
- [x] Recent Payments - Documented

### User Account Endpoints:
- [x] Delete Account - Documented (Play Store compliance)

### Serializers:
- [x] RentPaymentCreateSerializer - Fully documented
- [x] LeaseSerializer - payment_status field documented
- [x] RentPaymentSerializer - All fields documented

---

## Key Documentation Highlights

### 1. **Hybrid Payment System**
- ✅ Both payment flows (invoice-based and lease-only) fully documented
- ✅ Clear explanation of when to use each flow
- ✅ Documents invoice auto-creation behavior

### 2. **Payment Status**
- ✅ `payment_status` field documented on LeaseSerializer
- ✅ Explains calculation logic
- ✅ Documents possible values ('paid', 'partial', 'unpaid')

### 3. **Gateway Payments**
- ✅ Documents that gateway payments work without invoices
- ✅ Documents invoice auto-creation on completion
- ✅ Clear error messages documented

### 4. **Lease ID in Response**
- ✅ Create lease endpoint documented to return ID
- ✅ Response schema includes all fields including ID

### 5. **User Account Deletion**
- ✅ Play Store compliance documented
- ✅ Security and permissions documented
- ✅ Response format documented

---

## Swagger UI Access

All endpoints are available in Swagger UI at:
- `/api/schema/swagger-ui/` (if using drf-yasg)
- `/api/schema/redoc/` (if using drf-spectacular)

---

## Notes

1. **Auto-Discovery:** drf-spectacular automatically discovers ViewSet endpoints, but explicit documentation ensures clarity
2. **Backward Compatibility:** Both `@extend_schema` (drf-spectacular) and `@swagger_auto_schema` (drf-yasg) decorators are used
3. **Response Schemas:** All responses use proper serializer schemas for accurate documentation
4. **Error Responses:** All error scenarios are documented (400, 401, 403, 404)

---

## Conclusion

✅ **All endpoints are fully documented in Swagger**
✅ **All new features are documented**
✅ **Both payment flows are clearly explained**
✅ **Payment status field is documented**
✅ **User deletion endpoint is documented**

The API documentation is complete and ready for mobile app integration! 🎉
