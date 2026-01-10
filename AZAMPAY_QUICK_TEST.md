# 🚀 AZAMpay Integration - Quick Test Guide

## ✅ Setup Confirmed

You have:
- ✅ Webhook URL configured in AZAMpay dashboard: `/api/v1/payments/webhook/azam-pay/`
- ✅ Credentials set in `.env` file

## 🧪 Quick Test Steps

### Step 1: Verify Configuration

1. **Check your `.env` file has:**
   ```bash
   AZAM_PAY_CLIENT_ID=your_client_id
   AZAM_PAY_CLIENT_SECRET=your_client_secret
   AZAM_PAY_SANDBOX=True
   BASE_URL=https://yourdomain.com  # or http://localhost:8081 for local testing
   ```

2. **Restart Django server** to load environment variables:
   ```bash
   python manage.py runserver
   ```

### Step 2: Test Booking Payment Flow

1. **Create or Select a Booking**
   - Go to: `/properties/bookings/` or your booking list
   - Select any booking (hotel, lodge, venue, or house)
   - **Important**: Ensure the customer has a phone number

2. **Go to Payment Page**
   - Click on the booking
   - Click "Create Payment" or go to: `/properties/bookings/{booking_id}/payment/`

3. **Initiate AZAMpay Payment**
   - Enter payment amount
   - Select **"Online Payment (AZAM Pay)"** or **"Mobile Money (AZAM Pay)"**
   - Click "Record Payment"
   - You should be redirected to AZAMpay payment page

4. **Complete Payment on AZAMpay**
   - Use sandbox test credentials if needed
   - Complete the payment
   - You'll be redirected back

5. **Verify Payment Status**
   - Go back to booking detail page
   - Check that `paid_amount` has been updated
   - Check that `payment_status` is updated (partial/paid)

### Step 3: Verify Webhook (Optional)

If you want to test webhook manually:

1. **Check Webhook Endpoint is Accessible:**
   ```
   POST https://yourdomain.com/api/v1/payments/webhook/azam-pay/
   ```

2. **Check Server Logs:**
   - Look for webhook requests in Django logs
   - Should see: "Webhook received from AZAM Pay"

## 🔍 Troubleshooting

### Issue: "Failed to initiate payment"
**Check:**
- ✅ Customer has phone number
- ✅ AZAMpay credentials are correct
- ✅ Server can reach AZAMpay API (check network/firewall)
- ✅ Check Django logs for error details

### Issue: "Phone number is required"
**Solution:**
- Ensure customer record has a phone number
- Phone number should be in format: `+255XXXXXXXXX` or `0XXXXXXXXX`

### Issue: Payment not updating after webhook
**Check:**
- ✅ Webhook URL is accessible from internet (use ngrok for local testing)
- ✅ Webhook signature verification is working
- ✅ Check Django logs for webhook processing errors
- ✅ Verify payment_id is in webhook payload

### Issue: "Invalid webhook signature"
**Solution:**
- In sandbox mode, webhook secret should be your Client Secret
- Check `AZAM_PAY_WEBHOOK_SECRET` in `.env` (or leave empty for sandbox)

## 📋 Test Checklist

- [ ] Can access payment page for booking
- [ ] Can select "Online Payment (AZAM Pay)"
- [ ] Payment form submits successfully
- [ ] Redirects to AZAMpay payment page
- [ ] Can complete payment on AZAMpay
- [ ] Returns from AZAMpay after payment
- [ ] Booking payment status updated
- [ ] Payment appears in payment history
- [ ] Webhook received (check logs)

## 🔗 Important URLs

- **Payment Page**: `/properties/bookings/{booking_id}/payment/`
- **Booking Detail**: `/properties/bookings/{booking_id}/`
- **Webhook Endpoint**: `/api/v1/payments/webhook/azam-pay/`
- **AZAMpay Sandbox**: https://sandbox.azampay.co.tz/

## 📝 Notes

1. **Sandbox Mode**: Use sandbox credentials for testing
2. **Phone Number**: Customer must have phone number for AZAMpay
3. **Webhook**: Must be accessible from internet (use ngrok for local dev)
4. **Payment Status**: Updates automatically when webhook is received

## ✅ Ready to Test!

Everything is configured. Start testing the payment flow now!

If you encounter any issues, check:
1. Django server logs
2. Browser console (for frontend errors)
3. AZAMpay dashboard (for transaction status)
