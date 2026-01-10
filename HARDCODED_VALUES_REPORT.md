# Hardcoded Values Report

## Summary
This report identifies all hardcoded values in the system that should be calculated from database data or made dynamic.

---

## 🔴 Critical Hardcoded Values (Must Fix)

### 1. Documents Module - Lease List (`documents/templates/documents/lease_list.html`)

**Location:** Lines 49, 67, 103

**Hardcoded Values:**
- `+12% this month` - Total Leases percentage change
- `+8% this month` - Active Leases percentage change  
- `+15% this month` - Monthly Revenue percentage change
- `3` - Expiring Soon count (line 83)
- `TZS 24.8K` - Monthly Revenue amount (line 101)

**Should Be:**
- Calculate month-over-month percentage changes from database
- Calculate actual expiring leases count
- Calculate actual monthly revenue from payments

**View:** `documents/views.py` - `lease_list()` function

---

### 2. Payments Module - Invoice List (`payments/templates/payments/invoice_list.html`)

**Location:** Lines 29, 53

**Hardcoded Values:**
- `+18% this month` - Total Invoices percentage change
- `85% payment rate` - Paid Invoices payment rate

**Should Be:**
- Calculate month-over-month percentage change for invoices
- Calculate actual payment rate: `(paid_invoices / total_invoices) * 100`

**View:** `payments/views.py` - `invoice_list()` function

---

### 3. Payments Module - Payment Methods (`payments/templates/payments/payment_methods.html`)

**Location:** Lines 98, 101

**Hardcoded Values:**
- `98.5%` - Success Rate percentage
- `Excellent` - Success Rate status text

**Should Be:**
- Calculate actual success rate from payment transactions
- Dynamic status text based on success rate value

**View:** `payments/views.py` - `payment_methods()` function

---

### 4. Payments Module - Payment List (`payments/templates/payments/payment_list.html`)

**Location:** Line 332

**Hardcoded Values:**
- `Excellent` - Success Rate status text (always shows "Excellent" regardless of actual rate)

**Should Be:**
- Dynamic status text based on success rate:
  - Excellent: >= 90%
  - Good: 70-89%
  - Fair: 50-69%
  - Poor: < 50%

**Status:** ✅ Percentage is calculated, but status text is hardcoded

---

### 5. Properties Module - Lodge Dashboard (`properties/templates/properties/lodge_dashboard.html`)

**Location:** Lines 330, 339, 348

**Hardcoded Values:**
- `12` - Available rooms count
- `4` - Occupied rooms count
- `0` - Maintenance rooms count

**Should Be:**
- Calculate from actual Room model data
- Filter by property and room status

**View:** `properties/views.py` - `lodge_dashboard()` function

---

## 🟡 Medium Priority Hardcoded Values

### 6. Documents Module - Lease List (`documents/templates/documents/lease_list.html`)

**Location:** Line 85

**Hardcoded Values:**
- `Requires attention` - Expiring Soon status text

**Should Be:**
- Dynamic text based on actual count:
  - If count > 0: "X leases expiring soon"
  - If count = 0: "No expiring leases"

---

## ✅ Already Fixed

### Payments Module - Payment List (`payments/templates/payments/payment_list.html`)
- ✅ `+12.5%` - **FIXED** - Now calculates `payments_change_percent`
- ✅ `+8.2%` - **FIXED** - Now calculates `revenue_change_percent`
- ⚠️ `Excellent` - **PARTIALLY FIXED** - Percentage calculated, but text still hardcoded

---

## 📋 Complete List of Hardcoded Values by File

### `documents/templates/documents/lease_list.html`
1. Line 49: `+12% this month` (Total Leases change)
2. Line 67: `+8% this month` (Active Leases change)
3. Line 83: `3` (Expiring Soon count)
4. Line 85: `Requires attention` (Expiring Soon text)
5. Line 101: `TZS 24.8K` (Monthly Revenue amount)
6. Line 103: `+15% this month` (Monthly Revenue change)

### `payments/templates/payments/invoice_list.html`
1. Line 29: `+18% this month` (Total Invoices change)
2. Line 53: `85% payment rate` (Paid Invoices rate)

### `payments/templates/payments/payment_methods.html`
1. Line 98: `98.5%` (Success Rate percentage)
2. Line 101: `Excellent` (Success Rate status)

### `payments/templates/payments/payment_list.html`
1. Line 332: `Excellent` (Success Rate status text - should be dynamic)

### `properties/templates/properties/lodge_dashboard.html`
1. Line 330: `12` (Available rooms)
2. Line 339: `4` (Occupied rooms)
3. Line 348: `0` (Maintenance rooms)

---

## 🔧 Recommended Fixes

### Priority 1: Critical Statistics
1. **Lease List Statistics** - Calculate all percentages and counts from database
2. **Invoice List Statistics** - Calculate percentage changes and payment rate
3. **Payment Methods Success Rate** - Calculate from actual transactions
4. **Lodge Dashboard Room Counts** - Calculate from Room model

### Priority 2: Status Text
1. **Success Rate Status** - Make dynamic based on percentage value
2. **Expiring Leases Text** - Make dynamic based on count

---

## 📝 Files That Need Updates

### Views (Python)
1. `documents/views.py` - `lease_list()` function
2. `payments/views.py` - `invoice_list()` function
3. `payments/views.py` - `payment_methods()` function
4. `properties/views.py` - `lodge_dashboard()` function

### Templates (HTML)
1. `documents/templates/documents/lease_list.html`
2. `payments/templates/payments/invoice_list.html`
3. `payments/templates/payments/payment_methods.html`
4. `payments/templates/payments/payment_list.html` (status text only)
5. `properties/templates/properties/lodge_dashboard.html`

---

## 🎯 Implementation Strategy

1. **Calculate Statistics in Views**
   - Add month-over-month percentage calculations
   - Calculate actual counts from database
   - Calculate actual revenue from payments

2. **Pass to Templates**
   - Add calculated values to context
   - Use template variables instead of hardcoded values

3. **Dynamic Status Text**
   - Create helper functions or template filters
   - Determine status based on calculated values

---

**Total Hardcoded Values Found:** 13 instances across 5 files
**Priority:** High - These affect data accuracy and user trust
