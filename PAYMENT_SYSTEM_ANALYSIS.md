# Payment System Analysis & Refactoring Plan

## Current State Analysis

### 1. Multiple Payment Models (CONFUSION!)

#### A. `properties.models.Payment` (Booking Payments)
- **Location**: `properties/models.py` line 718
- **Purpose**: Payments for hotel/lodge/venue/house bookings
- **Relationships**: 
  - ForeignKey to `Booking` (via `booking_payments`)
- **Fields**: amount, payment_method, payment_type, transaction_reference, payment_date
- **Used by**: `create_payment` view in `properties/views.py`

#### B. `payments.models.Payment` (Unified Payment)
- **Location**: `payments/models.py` line 52
- **Purpose**: Unified payment model for all payment types
- **Relationships**: 
  - Can link to `Invoice`, `RentInvoice`, `Booking`, or `Lease`
  - ForeignKey to `PaymentProvider` (for gateway integration)
- **Fields**: Similar but includes gateway fields (transaction_id, processor_response)
- **Used by**: Visit payments, potentially AZAMpay integration

#### C. `rent.models.RentPayment` (Rent Payments)
- **Location**: `rent/models.py` line 89
- **Purpose**: Monthly rent payments for house leases
- **Relationships**: 
  - ForeignKey to `RentInvoice` and `Lease`
- **Fields**: Similar structure
- **Used by**: Rent payment views

### 2. Pricing Calculation Issues

#### Booking Model Problems:
```python
# CURRENT (WRONG for hotels/lodges/venues):
@property
def calculated_total_amount(self):
    """Calculate total amount based on monthly rate × number of months"""
    return self.monthly_rate * self.duration_months

@property
def monthly_rate(self):
    """Get the monthly rate for this property"""
    return self.property_obj.rent_amount  # This is wrong!
```

**Issues**:
1. **Hotels/Lodges/Venues**: Should use `daily_rate × duration_days`, NOT monthly rate × months
2. **Houses**: Can use monthly rate × months (correct)
3. **Property has `rent_period` field** (month/day/week/year) but Booking model ignores it!

#### Property Model:
- Has `rent_amount` field (the base rate)
- Has `rent_period` field (month/day/week/year) - **NOT USED BY BOOKING MODEL!**
- Migration `0010_property_rent_period.py` sets hotels/lodges/venues to 'day', houses to 'month'

### 3. Invoice System Confusion

#### A. `payments.models.Invoice`
- Generic invoice model
- Has `booking_id` field (BigInteger, not ForeignKey!)
- Status: Seems unused for bookings

#### B. `rent.models.RentInvoice`
- Used for monthly rent invoices
- Properly linked to Lease
- Has payment tracking

#### C. Booking Invoices
- **NO automatic invoice generation for bookings**
- Bookings go directly to payment without invoice step

### 4. Property Type Payment Requirements

| Property Type | Pricing Model | Invoice Needed? | Payment Model Used |
|--------------|---------------|-----------------|-------------------|
| **House** | Monthly rent × months | Yes (via RentInvoice) | `rent.models.RentPayment` |
| **Hotel** | Daily rate × nights | Maybe? (Currently NO) | `properties.models.Payment` |
| **Lodge** | Daily rate × nights | Maybe? (Currently NO) | `properties.models.Payment` |
| **Venue** | Rate per event | Maybe? (Currently NO) | `properties.models.Payment` |

## Problems Identified

1. **❌ Booking pricing calculation is WRONG** for hotels/lodges/venues (uses monthly instead of daily)
2. **❌ Multiple payment models** causing confusion
3. **❌ No clear invoice flow** for bookings (hotel/lodge/venue)
4. **❌ Property `rent_period` field ignored** by Booking model
5. **❌ AZAMpay integration unclear** - which payment model to use?

## Proposed Solution

### Phase 1: Fix Booking Pricing Calculation

**Fix the Booking model to respect property `rent_period`:**

```python
@property
def base_rate(self):
    """Get the base rate from property"""
    return self.property_obj.rent_amount

@property
def rent_period(self):
    """Get rent period from property"""
    return self.property_obj.rent_period

@property
def calculated_total_amount(self):
    """Calculate total amount based on property rent_period"""
    if self.rent_period == 'day':
        # Hotels, Lodges: daily_rate × nights
        return self.base_rate * self.duration_days
    elif self.rent_period == 'month':
        # Houses: monthly_rate × months
        return self.base_rate * self.duration_months
    elif self.rent_period == 'week':
        # Weekly rentals
        weeks = max(1, self.duration_days // 7)
        return self.base_rate * weeks
    elif self.rent_period == 'year':
        # Yearly rentals
        years = max(1, self.duration_months // 12)
        return self.base_rate * years
    else:
        # Fallback to daily
        return self.base_rate * self.duration_days

@property
def daily_rate(self):
    """Calculate daily rate (for display purposes)"""
    if self.duration_days > 0:
        return self.calculated_total_amount / self.duration_days
    return self.base_rate if self.rent_period == 'day' else (self.base_rate / 30)
```

### Phase 2: Unify Payment Models

**Decision: Use `payments.models.Payment` as the unified model**

**Migration Strategy**:
1. Keep `properties.models.Payment` temporarily for backward compatibility
2. Update `create_payment` view to create `payments.models.Payment` instead
3. Add migration to copy existing `properties.models.Payment` records to unified model
4. Eventually deprecate `properties.models.Payment`

**Benefits**:
- Single payment model for all types
- Built-in gateway integration support (AZAMpay ready)
- Consistent payment tracking
- Better for reporting

### Phase 3: Invoice System for Bookings

**Decision: Generate invoices for bookings (optional, configurable)**

**Approach**:
- Create `BookingInvoice` model OR use `payments.models.Invoice` properly
- Generate invoice when booking is confirmed
- Link payments to invoice
- Allow direct payment without invoice (current flow)

**Recommendation**: Keep current flow (direct payment) but add optional invoice generation for accounting purposes.

### Phase 4: AZAMpay Integration

**Use `payments.models.Payment` with `PaymentProvider` and `PaymentTransaction`:**

```python
# Create unified payment
payment = Payment.objects.create(
    booking=booking,
    tenant=request.user,  # or booking.customer.user
    amount=booking.calculated_total_amount,
    payment_method='online',
    provider=azam_pay_provider,
    status='pending'
)

# Create transaction record
transaction = PaymentTransaction.objects.create(
    payment=payment,
    provider=azam_pay_provider,
    status='initiated'
)

# Initiate AZAMpay payment
# ... AZAMpay API call ...
```

## Implementation Plan

### Step 1: Fix Booking Pricing ✅ (Priority 1)
- [x] Update `calculated_total_amount` to use `rent_period`
- [x] Update `daily_rate` property
- [ ] Test with different property types

### Step 2: Update Payment Creation ✅ (Priority 1)
- [ ] Modify `create_payment` view to use `payments.models.Payment`
- [ ] Keep backward compatibility
- [ ] Update payment display views

### Step 3: Clarify Invoice Flow (Priority 2)
- [ ] Document when invoices are needed
- [ ] Add optional invoice generation for bookings
- [ ] Update templates/views

### Step 4: AZAMpay Integration (Priority 1)
- [ ] Create payment using unified model
- [ ] Integrate with AZAMpay gateway
- [ ] Test payment flow

## Testing Checklist

- [ ] House booking: Monthly calculation works
- [ ] Hotel booking: Daily calculation works
- [ ] Lodge booking: Daily calculation works
- [ ] Venue booking: Event rate works
- [ ] Payment creation works for all types
- [ ] Payment tracking updates booking correctly
- [ ] AZAMpay integration works end-to-end
