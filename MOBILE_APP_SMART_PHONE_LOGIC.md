# Mobile App Smart Phone Logic - AZAM Pay Integration

**✅ Confirmed: Smart Phone Logic Works Perfectly with Mobile Apps!**

---

## 🎯 How Smart Phone Logic Works

The smart phone logic is **100% server-side** and automatically selects the correct phone number based on:
1. **Who is making the payment** (authenticated user from JWT token)
2. **What type of payment** (booking, rent, visit)

**No manual phone number selection needed in mobile app!** 🎉

---

## 📱 Smart Phone Logic Rules

### 1. **Booking Payments** (Hotel, Lodge, Venue)

| User Type | Phone Number Used | Source |
|-----------|------------------|--------|
| **Admin/Staff** | Customer's phone | From `booking.customer.phone` |
| **Customer** | Their own phone | From `user.profile.phone` |

**Why?** When admin creates a booking payment, the customer should receive the payment prompt, not the admin.

---

### 2. **Rent Payments** (House Rent)

| User Type | Phone Number Used | Source |
|-----------|------------------|--------|
| **Admin/Staff** | Tenant's phone | From `rent_invoice.tenant.profile.phone` |
| **Tenant** | Their own phone | From `user.profile.phone` |

**Why?** When admin creates a rent payment, the tenant should receive the payment prompt.

---

### 3. **Visit Payments** (House - One-Time Access)

| User Type | Phone Number Used | Source |
|-----------|------------------|--------|
| **Admin/Staff** | Their own phone | From `user.profile.phone` |
| **Customer** | Their own phone | From `user.profile.phone` |

**Why?** Visit payments are always for the person making the payment.

---

## 🔄 Mobile App Flow (No Changes Needed!)

### Example: Hotel Booking Payment

```javascript
// Step 1: Create booking (customer phone stored in booking.customer.phone)
POST /api/v1/properties/bookings/create/
{
  "property_id": 123,
  "property_type": "hotel",
  "room_number": "10",
  "customer_name": "John Doe",
  "phone": "+255700000000",  // ← Customer phone stored here
  ...
}

// Step 2: Create payment (links to booking)
POST /api/v1/payments/payments/
{
  "booking": 456,  // ← Links payment to booking
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"
}

// Step 3: Initiate payment (SMART LOGIC AUTOMATICALLY SELECTS PHONE!)
POST /api/v1/payments/payments/{payment_id}/initiate-gateway/
// ✅ Server automatically:
//    - Checks if user is admin/staff (from JWT token)
//    - If admin: Uses booking.customer.phone (+255700000000)
//    - If customer: Uses user.profile.phone
//    - Sends payment prompt to correct phone number
```

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "transaction_id": 20,
  "phone_number_used": "+255700000000",  // ← Shows which phone was used
  "message": "Payment initiated successfully. The customer will receive a payment prompt on their phone."
}
```

---

## ✅ Why It Works with Mobile Apps

### 1. **Server-Side Logic**
- Smart phone selection happens in `PaymentGatewayService.initiate_payment()`
- Runs on backend, not in mobile app
- Mobile app doesn't need to know which phone to use

### 2. **Based on Authenticated User**
- Uses `payment.tenant` (from JWT token) to determine user role
- Checks `payment.tenant.is_staff` or `payment.tenant.is_superuser`
- No session or web form dependencies

### 3. **Uses Payment Relationships**
- Booking payments: Uses `payment.booking.customer.phone`
- Rent payments: Uses `payment.rent_invoice.tenant.profile.phone`
- Visit payments: Uses `payment.tenant.profile.phone`

### 4. **Automatic Phone Selection**
- Mobile app just calls the API endpoints
- Backend automatically selects correct phone number
- Payment prompt goes to the right person

---

## 📋 Mobile App Implementation

### What Mobile App Needs to Do:

1. **Create Booking** ✅
   - Include customer phone in booking request
   - Phone is stored in `booking.customer.phone`

2. **Create Payment** ✅
   - Link payment to booking (`booking: 456`)
   - Include payment method and provider

3. **Initiate Payment** ✅
   - Just call the endpoint!
   - **No phone number needed** - server selects automatically
   - Response includes `phone_number_used` for confirmation

4. **Poll Payment Status** ✅
   - Check payment status until completed
   - Customer receives payment prompt automatically

### What Mobile App Does NOT Need to Do:

❌ **Don't manually select phone numbers**
❌ **Don't check if user is admin/staff**
❌ **Don't pass phone number to initiate-gateway endpoint**

**The backend handles everything automatically!** 🎉

---

## 🔍 Verification

### Check Which Phone Was Used

After initiating payment, check the response:

```json
{
  "success": true,
  "payment_id": 80,
  "phone_number_used": "+255700000000",  // ← Confirms which phone was used
  "message": "Payment initiated successfully..."
}
```

### Check Payment Transaction

The `request_payload` in `PaymentTransaction` includes the phone number:

```javascript
GET /api/v1/payments/transactions/{transaction_id}/
```

Response includes:
```json
{
  "request_payload": {
    "accountNumber": "+255700000000",  // ← Phone number used
    "amount": "200000.00",
    ...
  }
}
```

---

## 🎯 Summary

**✅ Smart Phone Logic is Fully Compatible with Mobile Apps!**

- ✅ Works automatically - no manual phone selection needed
- ✅ Server-side logic - no mobile app changes required
- ✅ Based on authenticated user (JWT token)
- ✅ Uses payment relationships (booking, rent_invoice)
- ✅ Returns `phone_number_used` in response for verification
- ✅ Logs phone selection logic for debugging

**Mobile app developers can simply:**
1. Create booking with customer phone
2. Create payment linked to booking
3. Call initiate-gateway endpoint
4. **Backend automatically sends payment prompt to correct phone!** 🚀

---

## 📚 Related Documentation

- `MOBILE_APP_COMPLETE_BOOKING_FLOW.md` - Complete booking flow
- `MOBILE_PAYMENT_INTEGRATION_GUIDE.md` - Payment integration guide
- `COMPLETE_MOBILE_API_SUMMARY.md` - All API endpoints

---

**Ready for Mobile App Integration!** ✅
