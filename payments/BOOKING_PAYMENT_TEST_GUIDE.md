# 🏨 Property Booking Payment Test Guide

## Overview

This guide helps you test AZAM Pay integration for property bookings (hotels, houses, lodges, venues).

---

## 🚀 Quick Start

### Option 1: Automated Test Script

Run the comprehensive test script:

```bash
cd e:\KAZI\Maisha_backend
python test_booking_payment_azam.py
```

**What it does:**
1. ✅ Login and get JWT token
2. ✅ Get available properties
3. ✅ Create a booking (or use existing)
4. ✅ Create a payment for the booking
5. ✅ Initiate AZAM Pay payment
6. ✅ Open payment link
7. ✅ Verify payment status
8. ✅ Show transaction details

---

### Option 2: Manual Testing via Admin Panel

1. **Create a Booking:**
   - Go to Properties → Hotels/Houses → Bookings
   - Create a new booking for a property
   - Note the Booking ID

2. **Create Payment:**
   - Go to Payments → Payment List
   - Create new payment
   - Link it to the booking
   - Set amount and payment method to "online"

3. **Initiate Gateway Payment:**
   - Use the API or admin interface
   - Get payment link
   - Complete payment on AZAM Pay

4. **Verify:**
   - Check payment status
   - View transaction details

---

## 📋 Prerequisites

Before testing:

- [ ] Django server is running
- [ ] AZAM Pay credentials in `.env` file
- [ ] At least one property exists (hotel, house, lodge, etc.)
- [ ] User has phone number in profile (`+255712345678` format)
- [ ] Booking exists (or can be created)

---

## 🔍 API Endpoints

### 1. Get Properties
```
GET /api/v1/properties/
GET /api/v1/properties/?property_type=1  # House
GET /api/v1/properties/?property_type=2  # Hotel
```

### 2. Create Booking
```
POST /api/v1/properties/{property_id}/bookings/
{
  "check_in_date": "2025-01-15",
  "check_out_date": "2025-01-18",
  "number_of_guests": 2,
  "customer_name": "Test Customer",
  "phone": "+255712345678",
  "email": "test@example.com"
}
```

### 3. Create Payment for Booking
```
POST /api/v1/payments/payments/
{
  "booking": <booking_id>,
  "amount": "50000.00",
  "payment_method": "online",
  "status": "pending"
}
```

### 4. Initiate Gateway Payment
```
POST /api/v1/payments/payments/{payment_id}/initiate/
POST /api/v1/rent/payments/{payment_id}/initiate-gateway/
```

### 5. Verify Payment
```
POST /api/v1/rent/payments/{payment_id}/verify/
```

### 6. View Transactions
```
GET /api/v1/payments/transactions/
```

---

## ✅ Success Indicators

### Booking Created
- ✅ Status 200/201
- ✅ Returns booking ID
- ✅ Returns booking reference
- ✅ Returns total amount

### Payment Created
- ✅ Status 200/201
- ✅ Returns payment ID
- ✅ Payment linked to booking

### Gateway Initiated
- ✅ Status 200/201
- ✅ Returns `payment_link` (not null)
- ✅ Returns `transaction_id`
- ✅ Payment link opens AZAM Pay sandbox

### Payment Verified
- ✅ Status 200
- ✅ Returns `verified: true`
- ✅ Returns `status: "completed"`

### Transaction Created
- ✅ Transaction appears in list
- ✅ Status is "successful"
- ✅ Gateway transaction ID present
- ✅ AZAM reference present

---

## ❌ Common Issues

### Issue 1: No Properties Found
**Solution:**
- Create a property via admin panel
- Ensure property status is "active"
- Check property type is set correctly

---

### Issue 2: Booking Creation Fails
**Possible Causes:**
- Property not available for dates
- Missing required fields (room number for hotels)
- Invalid date format

**Solution:**
- Use future dates
- For hotels, ensure room is selected
- Check property availability

---

### Issue 3: Payment Creation Fails
**Possible Causes:**
- Booking ID not found
- Invalid amount
- Missing tenant/user

**Solution:**
- Verify booking exists
- Use positive amount
- Ensure user is logged in

---

### Issue 4: Gateway Initiation Fails
**Possible Causes:**
- User missing phone number
- Invalid AZAM Pay credentials
- Payment already completed

**Solution:**
- Add phone to user profile (`+255712345678`)
- Check `.env` credentials
- Create new payment if needed

---

### Issue 5: Payment Link Not Generated
**Possible Causes:**
- AZAM Pay API error
- Invalid callback URL
- Network issues

**Solution:**
- Check server logs
- Verify AZAM Pay sandbox is accessible
- Check callback URL configuration

---

## 📊 View Results

### Phoenix Admin Panel
```
http://localhost:8081/payments/transactions/
http://localhost:8081/payments/payments/
```

### API Endpoints
```
GET http://localhost:8081/api/v1/payments/transactions/
GET http://localhost:8081/api/v1/payments/payments/
```

---

## 🎯 Test Checklist

- [ ] Can login and get JWT token
- [ ] Can get properties list
- [ ] Can create booking (or use existing)
- [ ] Can create payment for booking
- [ ] Can initiate gateway payment
- [ ] Payment link is generated
- [ ] Payment link opens in browser
- [ ] Can complete payment on AZAM Pay
- [ ] Can verify payment status
- [ ] Payment status updates to "completed"
- [ ] Transaction appears in transactions list
- [ ] Transaction status is "successful"
- [ ] Booking payment status updates

---

## 💡 Tips

1. **Use Sandbox Mode:**
   - Ensure `AZAM_PAY_SANDBOX=True` in `.env`
   - Use test credentials from AZAM Pay dashboard

2. **Phone Number Format:**
   - Must be international format: `+255712345678`
   - No spaces or dashes

3. **Test Amounts:**
   - Use reasonable amounts (e.g., 50,000 TZS)
   - Avoid very small amounts

4. **Check Server Logs:**
   - Most errors are logged in Django console
   - Look for AZAM Pay API responses

5. **Multiple Properties:**
   - Test with different property types
   - Hotels may require room selection
   - Houses may have different booking flow

---

## 🆘 Need Help?

1. **Check Server Logs** - Detailed error messages
2. **Check Admin Panel** - View booking and payment details
3. **Check API Responses** - Error messages are descriptive
4. **Review Documentation:**
   - `AZAM_PAY_INTEGRATION_GUIDE.md`
   - `AZAM_PAY_QUICK_TEST.md`
   - `test_booking_payment_azam.py`

---

## 🎉 Ready to Test!

Run the test script:
```bash
python test_booking_payment_azam.py
```

Or test manually via admin panel and API!
