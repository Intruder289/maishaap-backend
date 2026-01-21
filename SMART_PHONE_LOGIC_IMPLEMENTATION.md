# Smart Phone Logic Implementation (Option 2)

## Overview
Implemented smart phone number selection for payments based on user role.

## Logic

### Admin/Staff Users
- **When**: Admin or staff member creates a payment for a booking
- **Phone Used**: Customer's phone number (from `booking.customer.phone`)
- **Result**: Customer receives the payment prompt on their phone
- **Why**: Admin is creating payment on behalf of customer, so customer should receive the prompt

### Regular Customer Users
- **When**: Customer creates their own payment
- **Phone Used**: Customer's own profile phone (`user.profile.phone`)
- **Result**: Customer receives payment prompt on their own phone
- **Why**: Customer is making their own payment, so they should receive the prompt

## Implementation Details

### 1. Payment Creation (`properties/views.py`)
- Tenant is always set to `request.user` (logged-in user)
- Phone number selection happens in gateway service

### 2. Gateway Service (`payments/gateway_service.py`)
- Checks if `payment.tenant.is_staff` or `payment.tenant.is_superuser`
- If admin/staff AND booking exists:
  - Uses `payment.booking.customer.phone`
- Otherwise:
  - Uses `payment.tenant.profile.phone`

### 3. Error Messages
- **Admin/Staff**: "Customer does not have a phone number. Please add a phone number to the customer profile."
- **Customer**: "Please add a phone number to your profile (User: <username>)."

## Code Location

### Gateway Service Logic
**File**: `payments/gateway_service.py`  
**Lines**: ~413-450

```python
# Check if logged-in user is admin/staff
is_admin_or_staff = payment.tenant.is_staff or payment.tenant.is_superuser

if is_admin_or_staff and payment.booking:
    # Admin/Staff: Use customer phone
    phone_number = payment.booking.customer.phone
else:
    # Customer: Use their own profile phone
    user_profile = getattr(payment.tenant, 'profile', None)
    phone_number = user_profile.phone if user_profile and user_profile.phone else None
```

## Testing

Run the test script to verify:
```bash
python test_smart_phone_logic.py
```

## Benefits

1. **Correct Behavior**: Customer always receives payment prompt (whether admin or self-initiated)
2. **Better UX**: No confusion about who receives the payment prompt
3. **Flexible**: Handles both admin-created and customer-created payments correctly
4. **Clear Errors**: Role-specific error messages help users understand what's wrong

## Scenarios

### Scenario 1: Admin Creates Payment
- Admin logs in → Creates payment for booking
- **Phone Used**: Customer's phone (`booking.customer.phone`)
- **Result**: Customer receives payment prompt ✅

### Scenario 2: Customer Creates Payment
- Customer logs in → Creates payment for their booking
- **Phone Used**: Customer's profile phone (`user.profile.phone`)
- **Result**: Customer receives payment prompt ✅

### Scenario 3: Customer Has No Phone
- Customer tries to create payment but has no phone in profile
- **Result**: Error message asking them to add phone to profile ✅

### Scenario 4: Admin Creates Payment, Customer Has No Phone
- Admin creates payment but customer has no phone
- **Result**: Error message asking admin to add phone to customer profile ✅
