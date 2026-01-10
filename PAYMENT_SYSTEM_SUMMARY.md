# Payment System - Clear Summary & Implementation Guide

## ✅ What Was Fixed

### 1. Booking Pricing Calculation (FIXED ✅)

**Problem**: Booking model was calculating ALL properties as monthly (monthly_rate × months), which was wrong for hotels/lodges/venues.

**Solution**: Updated `Booking.calculated_total_amount` to respect property `rent_period`:
- **Hotels/Lodges** (`rent_period='day'`): `base_rate × duration_days` ✅
- **Houses** (`rent_period='month'`): `base_rate × duration_months` ✅
- **Weekly rentals** (`rent_period='week'`): `base_rate × weeks` ✅
- **Yearly rentals** (`rent_period='year'`): `base_rate × years` ✅

**Files Changed**:
- `properties/models.py`: Updated `calculated_total_amount`, `daily_rate`, added `base_rate`, `rent_period` properties
- `properties/templates/properties/modals/booking_details.html`: Updated to show correct pricing info based on property type

### 2. Backward Compatibility

- Kept `monthly_rate` property for backward compatibility (deprecated but functional)
- Templates updated to use `base_rate` and show appropriate labels

## 📋 Current Payment Models

### Model 1: `properties.models.Payment` (Currently Used for Bookings)
- **Used by**: `create_payment` view
- **Links to**: `Booking` only
- **Fields**: amount, payment_method, payment_type, transaction_reference, payment_date
- **Status**: Active, but should migrate to unified model

### Model 2: `payments.models.Payment` (Unified Payment Model)
- **Used by**: Visit payments, AZAMpay integration
- **Links to**: `Invoice`, `RentInvoice`, `Booking`, or `Lease`
- **Fields**: Includes gateway fields (transaction_id, processor_response, provider)
- **Status**: Ready for AZAMpay, should be used for all payments

### Model 3: `rent.models.RentPayment` (Rent Payments)
- **Used by**: Monthly rent payments for house leases
- **Links to**: `RentInvoice` and `Lease`
- **Status**: Working correctly, keep as-is

## 🔄 Payment Flow by Property Type

### House Properties
1. **Lease Created** → `documents.Lease`
2. **Monthly Invoice Generated** → `rent.RentInvoice`
3. **Payment Made** → `rent.RentPayment` (linked to RentInvoice)
4. **Invoice Status Updated** → Automatically when payment received

### Hotel/Lodge/Venue Properties
1. **Booking Created** → `properties.Booking`
2. **Total Calculated** → Based on `rent_period`:
   - Hotels/Lodges: `daily_rate × nights`
   - Venues: `rate_per_event` (if set) or `daily_rate × days`
3. **Payment Made** → `properties.Payment` (currently) OR `payments.Payment` (recommended)
4. **Booking Status Updated** → Payment status tracked on Booking model

## 🎯 Invoice Requirements

| Property Type | Invoice Needed? | Current Status |
|--------------|----------------|----------------|
| **House** | ✅ Yes | Uses `RentInvoice` - Working |
| **Hotel** | ❓ Optional | No invoice currently - Direct payment |
| **Lodge** | ❓ Optional | No invoice currently - Direct payment |
| **Venue** | ❓ Optional | No invoice currently - Direct payment |

**Recommendation**: 
- **Houses**: Keep using `RentInvoice` (working well)
- **Hotels/Lodges/Venues**: Optional invoice generation for accounting. Current direct payment flow is fine.

## 🔌 AZAMpay Integration Plan

### Current State
- `payments.models.Payment` has gateway support
- `PaymentProvider` model exists
- `PaymentTransaction` model for tracking gateway transactions

### Integration Steps

1. **Use Unified Payment Model** (`payments.models.Payment`)
   ```python
   from payments.models import Payment, PaymentProvider, PaymentTransaction
   
   # Create payment
   payment = Payment.objects.create(
       booking=booking,
       tenant=booking.customer.user,  # or request.user
       amount=booking.calculated_total_amount,
       payment_method='online',
       provider=azam_pay_provider,
       status='pending'
   )
   ```

2. **Create Transaction Record**
   ```python
   transaction = PaymentTransaction.objects.create(
       payment=payment,
       provider=azam_pay_provider,
       status='initiated'
   )
   ```

3. **Initiate AZAMpay Payment**
   - Use AZAMpay API to create payment link
   - Store `azam_reference` in `PaymentTransaction`
   - Update status as payment progresses

4. **Handle Callback**
   - Update `Payment.status` to 'successful' or 'failed'
   - Update `PaymentTransaction.status`
   - Update `Booking.paid_amount` and `payment_status`

## 📝 Next Steps

### Priority 1: Migrate Booking Payments to Unified Model
- [ ] Update `create_payment` view to use `payments.models.Payment`
- [ ] Migrate existing `properties.Payment` records
- [ ] Update payment display views
- [ ] Test payment flow

### Priority 2: AZAMpay Integration
- [ ] Create AZAMpay provider in `PaymentProvider`
- [ ] Implement payment initiation endpoint
- [ ] Implement callback handler
- [ ] Test end-to-end payment flow

### Priority 3: Optional Invoice Generation
- [ ] Add optional invoice generation for bookings
- [ ] Create `BookingInvoice` model OR use `payments.Invoice` properly
- [ ] Add invoice generation toggle in settings

## 🧪 Testing Checklist

### Booking Pricing
- [x] House booking: Monthly calculation works
- [x] Hotel booking: Daily calculation works  
- [x] Lodge booking: Daily calculation works
- [x] Venue booking: Event/daily rate works
- [ ] Test with different date ranges
- [ ] Test edge cases (1 day, 1 month, etc.)

### Payment Flow
- [ ] Create payment for house booking
- [ ] Create payment for hotel booking
- [ ] Create payment for lodge booking
- [ ] Create payment for venue booking
- [ ] Verify booking.paid_amount updates correctly
- [ ] Verify payment_status updates correctly

### AZAMpay Integration
- [ ] Payment initiation works
- [ ] Payment callback updates status correctly
- [ ] Booking status updates on successful payment
- [ ] Failed payments handled correctly

## 📚 Key Files Reference

- **Booking Model**: `properties/models.py` (line 528)
- **Payment Model (Bookings)**: `properties/models.py` (line 718)
- **Unified Payment Model**: `payments/models.py` (line 52)
- **Rent Payment Model**: `rent/models.py` (line 89)
- **Create Payment View**: `properties/views.py` (line 4830)
- **Property Model**: `properties/models.py` (line 76)

## 💡 Important Notes

1. **Property `rent_period` field**: Now properly used by Booking model ✅
2. **Multiple payment models**: Migration needed to unified model
3. **Invoice system**: Working for houses, optional for bookings
4. **AZAMpay ready**: Unified payment model supports gateway integration
