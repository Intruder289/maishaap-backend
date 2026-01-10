# 🚀 Quick Test: AZAM Pay Integration

## Prerequisites Checklist

Before testing, make sure:

- [ ] Django server is running (`python manage.py runserver`)
- [ ] Server is accessible at `http://localhost:8081` (or your port)
- [ ] `.env` file has AZAM Pay credentials:
  - `AZAM_PAY_CLIENT_ID`
  - `AZAM_PAY_CLIENT_SECRET`
  - `AZAM_PAY_SANDBOX=True`
- [ ] You have at least one **rent invoice** in the database
- [ ] Your user account has a **phone number** in the profile
- [ ] Phone number is in international format (e.g., `+255712345678`)

---

## 🧪 Run the Test Script

### Option 1: Interactive Test (Recommended)

```bash
cd e:\KAZI\Maisha_backend
python test_azam_pay.py
```

**What it does:**
1. ✅ Prompts for login credentials
2. ✅ Gets rent invoices
3. ✅ Creates a payment
4. ✅ Initiates AZAM Pay payment
5. ✅ Opens payment link in browser
6. ✅ Waits for you to complete payment
7. ✅ Verifies payment status
8. ✅ Shows transaction details

**Follow the prompts** - the script will guide you through each step!

---

### Option 2: Manual Testing via Swagger

1. **Start server:**
   ```bash
   python manage.py runserver
   ```

2. **Open Swagger:**
   ```
   http://localhost:8081/swagger/
   ```

3. **Login:**
   - Use `POST /api/v1/auth/login/`
   - Enter email and password
   - Copy the `access` token from `tokens.access`

4. **Authorize:**
   - Click "Authorize" button
   - Paste token: `Bearer <your_token>`

5. **Test Flow:**
   - `GET /api/v1/rent/invoices/` - Get invoice ID
   - `POST /api/v1/rent/payments/` - Create payment
   - `POST /api/v1/rent/payments/{id}/initiate-gateway/` - Initiate AZAM Pay
   - Copy `payment_link` and open in browser
   - Complete payment on AZAM Pay
   - `POST /api/v1/rent/payments/{id}/verify/` - Verify payment
   - `GET /api/v1/payments/transactions/` - View transactions

---

## ✅ What to Look For

### Success Indicators:

1. **Login:**
   - ✅ Status 200
   - ✅ Returns `tokens.access` and `tokens.refresh`

2. **Get Invoices:**
   - ✅ Status 200
   - ✅ Returns list of invoices

3. **Create Payment:**
   - ✅ Status 201
   - ✅ Returns payment ID

4. **Initiate Gateway:**
   - ✅ Status 201
   - ✅ Returns `payment_link` (not null/empty)
   - ✅ Returns `transaction_id`
   - ✅ Returns `transaction_reference`

5. **Payment Link:**
   - ✅ Opens AZAM Pay sandbox page
   - ✅ Shows payment amount
   - ✅ Allows payment completion

6. **Verify Payment:**
   - ✅ Status 200
   - ✅ Returns `verified: true`
   - ✅ Returns `status: "completed"` (after payment)

7. **View Transactions:**
   - ✅ Status 200
   - ✅ Shows transaction with status "successful"
   - ✅ Shows gateway transaction ID
   - ✅ Shows AZAM reference

---

## ❌ Common Issues

### Issue 1: Login Fails
**Error:** `Invalid email or password` or `Account pending approval`

**Solution:**
- Check email/password are correct
- Ensure account is approved (not pending)
- Try logging in via admin panel first

---

### Issue 2: No Invoices Found
**Error:** `No invoices found`

**Solution:**
- Create a rent invoice first:
  1. Go to admin panel
  2. Navigate to Rent → Invoices
  3. Create a new invoice for a tenant
  4. Run test script again

---

### Issue 3: Gateway Initiation Fails
**Error:** `Failed to initiate gateway payment`

**Check:**
- ✅ Server logs for detailed error
- ✅ `.env` file has correct credentials
- ✅ User has phone number in profile
- ✅ Phone number format: `+255712345678`
- ✅ AZAM Pay sandbox is accessible

**Common Errors:**
- `User phone number is required` → Add phone to user profile
- `Failed to obtain access token` → Check CLIENT_ID and CLIENT_SECRET
- `Invalid credentials` → Verify credentials match AZAM Pay dashboard

---

### Issue 4: Payment Link Not Working
**Error:** Payment link is null or doesn't open

**Check:**
- ✅ Payment was initiated successfully
- ✅ Check server logs for AZAM Pay API response
- ✅ Verify AZAM Pay sandbox is accessible
- ✅ Check if callback URL is configured in AZAM Pay dashboard

---

### Issue 5: Verification Fails
**Error:** `Failed to verify payment` or status stays "pending"

**Check:**
- ✅ Payment was completed on AZAM Pay side
- ✅ Wait a few seconds and try again
- ✅ Check transaction status in admin panel
- ✅ Verify with AZAM Pay dashboard

---

## 📊 View Test Results

### Option 1: Phoenix Admin Panel
```
http://localhost:8081/payments/transactions/
```

**Navigate:**
- Payments → Transactions
- See all payment gateway transactions
- Filter by status, provider, search

### Option 2: API
```
GET http://localhost:8081/api/v1/payments/transactions/
```

### Option 3: Server Logs
Check your Django server terminal for:
- `[INFO] AZAM Pay access token obtained successfully`
- `[INFO] AZAM Pay payment initiated`
- `[INFO] Payment verified: status=successful`

---

## 🎯 Test Checklist

Use this to verify everything works:

- [ ] Can login and get JWT token
- [ ] Can get rent invoices
- [ ] Can create payment record
- [ ] Can initiate gateway payment (gets payment link)
- [ ] Payment link opens in browser
- [ ] Can complete payment on AZAM Pay sandbox
- [ ] Can verify payment status
- [ ] Payment status changes to "completed"
- [ ] Transaction appears in transactions list
- [ ] Transaction status is "successful"
- [ ] Invoice status updates (if applicable)

---

## 🆘 Need Help?

1. **Check Server Logs** - Most errors are logged there
2. **Check Admin Panel** - View transaction details
3. **Check API Responses** - Error messages are usually descriptive
4. **Review Documentation:**
   - `AZAM_PAY_INTEGRATION_GUIDE.md`
   - `AZAM_PAY_TESTING_GUIDE.md`
   - `AZAM_PAY_CREDENTIALS_SETUP.md`

---

## 🎉 Ready to Test!

Run the test script:
```bash
python test_azam_pay.py
```

Follow the prompts and watch the magic happen! ✨
