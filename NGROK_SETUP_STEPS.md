# ngrok Setup Steps - Quick Guide

## Your ngrok URL
**https://unperceivably-brutalitarian-krystyna.ngrok-free.dev**

---

## Step 1: Update .env File

**Open your `.env` file** (in the project root: `d:\KAZI\Maisha_backend\.env`)

**Find these lines and update them:**

```bash
# Update this line:
AZAM_PAY_WEBHOOK_URL=https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/

# Update this line (optional, but recommended):
BASE_URL=https://unperceivably-brutalitarian-krystyna.ngrok-free.dev
```

**Full example of what should be in your .env:**

```bash
# AzamPay Configuration
AZAM_PAY_CLIENT_ID=your_sandbox_client_id
AZAM_PAY_CLIENT_SECRET=your_sandbox_client_secret
AZAM_PAY_API_KEY=your_sandbox_api_key
AZAM_PAY_APP_NAME=mishap
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz

# Webhook URL - UPDATE THIS WITH YOUR NGROK URL
AZAM_PAY_WEBHOOK_URL=https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/

# Base URL - UPDATE THIS TOO
BASE_URL=https://unperceivably-brutalitarian-krystyna.ngrok-free.dev
```

**Important:** 
- Make sure there are **NO spaces** around the `=` sign
- Make sure the URL ends with `/` (trailing slash)
- Save the file after editing

---

## Step 2: Restart Django Server

**After updating .env:**

1. **Stop Django server** (if running):
   - Press `Ctrl+C` in the terminal where Django is running

2. **Restart Django server:**
   ```bash
   python manage.py runserver 8081
   ```

**This loads the new webhook URL from .env**

---

## Step 3: Configure Webhook in AzamPay Sandbox Dashboard

### 3.1 Access AzamPay Sandbox Dashboard

1. **Log into AzamPay Sandbox Dashboard:**
   - URL: Usually `https://sandbox.azampay.co.tz` or your sandbox dashboard URL
   - Use your sandbox account credentials

### 3.2 Navigate to Webhook Settings

**Look for one of these:**
- **Settings** → **Webhooks**
- **App Settings** → **Webhooks**
- **Configuration** → **Webhooks**
- **API Settings** → **Webhooks**

### 3.3 Add Webhook URL

**Enter this exact URL:**
```
https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/
```

**Important:**
- Copy the URL exactly (including `https://` and trailing `/`)
- Make sure there are no extra spaces
- Save the webhook URL

### 3.4 Verify Webhook URL is Saved

- Check that the webhook URL is saved in the dashboard
- Some dashboards show a test button - you can test if available

---

## Step 4: Verify Setup

### 4.1 Check Django Server is Running

**In your Django terminal, you should see:**
```
Starting development server at http://127.0.0.1:8081/
```

### 4.2 Check ngrok is Running

**In your ngrok terminal, you should see:**
```
Forwarding: https://unperceivably-brutalitarian-krystyna.ngrok-free.dev -> http://localhost:8081
```

### 4.3 Test Webhook Endpoint

**Open a browser or use curl:**
```bash
# Test if webhook endpoint is accessible
curl https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/
```

**Or open in browser:**
```
https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/
```

**Expected:** Should return an error (since it's a POST endpoint), but it confirms the URL is accessible.

### 4.4 Check ngrok Web Interface

**Open in browser:**
```
http://localhost:4040
```

**This shows:**
- All incoming requests to your ngrok URL
- Request/response details
- Helpful for debugging

---

## Step 5: Ready to Test Payment

**Once everything is configured:**

1. ✅ Django server running on `http://localhost:8081`
2. ✅ ngrok running and forwarding to localhost:8081
3. ✅ `.env` file updated with ngrok URL
4. ✅ Django server restarted (to load new .env)
5. ✅ Webhook URL configured in AzamPay dashboard

**Now you can:**
- Create a test payment
- Complete payment on AzamPay
- Watch Django logs for webhook receipt
- Verify payment status updates

---

## Quick Verification Script

**Run this to verify your setup:**
```bash
python test_local_azampay_setup.py
```

**This will check:**
- Sandbox mode enabled
- Credentials configured
- Webhook URL matches ngrok
- Webhook handler code is correct

---

## Troubleshooting

### Issue: Can't find .env file

**Location:** `d:\KAZI\Maisha_backend\.env`

**If it doesn't exist:**
- Create it in the project root
- Copy settings from `settings.py` comments
- Or ask me to help create it

### Issue: Changes not taking effect

**Solution:**
1. Make sure you saved the .env file
2. Restart Django server (Ctrl+C, then restart)
3. Check for typos in the URL

### Issue: Webhook URL not accessible

**Check:**
1. ngrok is still running (check terminal)
2. Django server is running
3. URL is correct (no typos)
4. Try accessing: `https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/` (should show your app)

### Issue: Can't find webhook settings in AzamPay dashboard

**Try:**
- Look in different sections (Settings, Configuration, API)
- Check AzamPay documentation
- Contact AzamPay support for dashboard navigation help

---

## Next Steps

After completing these steps:

1. **Test Payment Creation**
   - Create a payment through your app
   - Initiate gateway payment
   - Complete on AzamPay

2. **Monitor Webhook**
   - Watch Django logs for: `"AzamPay webhook received"`
   - Check ngrok dashboard: `http://localhost:4040`
   - Verify payment status updates

3. **Verify Success**
   - Payment status should change to `completed`
   - No "Invalid webhook signature" error
   - Related records (RentInvoice/Booking) updated

---

**Your ngrok URL:** `https://unperceivably-brutalitarian-krystyna.ngrok-free.dev`  
**Webhook URL:** `https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/`

**Status:** Ready to configure ✅
