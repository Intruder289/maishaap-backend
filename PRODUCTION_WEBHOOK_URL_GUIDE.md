# Production Webhook URL Configuration Guide

## 🎯 Important Clarification

### The Webhook URL is an API Endpoint, NOT a Web Page

**Your webhook URL:**
```
https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
```

**This is different from:**
- `https://portal.maishaapp.co.tz/` (homepage - redirects to login)
- `https://portal.maishaapp.co.tz/login/` (login page)

---

## ✅ Key Points

### 1. **No Login Required**
- The webhook endpoint is a **public API endpoint**
- It has `@permission_classes([])` - no authentication needed
- It has `@csrf_exempt` - CSRF protection disabled for webhooks
- **AzamPay calls this URL directly** - no browser, no login needed

### 2. **How It Works**
```
AzamPay Server → POST Request → https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
                                    ↓
                            Django receives webhook
                                    ↓
                            Processes payment status
                                    ↓
                            Updates database
```

### 3. **Browser Redirect vs API Call**
- **Browser access** (`https://portal.maishaapp.co.tz/`):
  - Redirects to login page (normal behavior)
  - This is for **human users** accessing the website
  
- **API endpoint** (`https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`):
  - **No redirect** - direct API call
  - This is for **AzamPay servers** to send webhooks
  - Works without login

---

## 🔧 Configuration Steps

### Step 1: Update Your Production .env File

**On your production server**, edit `.env`:

```bash
# Base URL
BASE_URL=https://portal.maishaapp.co.tz

# AzamPay Webhook URL (FULL PATH)
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# AzamPay Production Settings
AZAM_PAY_SANDBOX=False
AZAM_PAY_BASE_URL=https://api.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# Your Production Credentials
AZAM_PAY_CLIENT_ID=your_production_client_id
AZAM_PAY_CLIENT_SECRET=your_production_client_secret
AZAM_PAY_API_KEY=your_production_api_key
```

### Step 2: Configure in AzamPay Production Dashboard

**You DO need to login to AzamPay dashboard** to configure the webhook URL:

1. **Go to AzamPay Production Dashboard:**
   - Login at: `https://portal.azampay.co.tz/` (or your AzamPay dashboard URL)
   - Use your **production account credentials** (not sandbox)

2. **Navigate to Webhook/Callback Settings:**
   - Look for "Webhook URL" or "Callback URL" settings
   - Usually under: Settings → Integration → Webhooks

3. **Enter the Webhook URL:**
   ```
   https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
   ```
   - **Important:** Include the full path including `/api/v1/payments/webhook/azam-pay/`
   - **Important:** Use `https://` (not `http://`)
   - **Important:** No trailing issues - should end with `/`

4. **Save the configuration**

---

## 🧪 Testing the Webhook URL

### Test 1: Verify Endpoint is Accessible

**From your production server or any machine:**

```bash
# Test if endpoint responds (should return error, but not 404)
curl -X POST https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected Response:**
- ✅ **200 OK** or **400 Bad Request** (means endpoint exists)
- ❌ **404 Not Found** (means URL is wrong)
- ❌ **302 Redirect to login** (should NOT happen for API endpoints)

### Test 2: Check Server Logs

**After configuring in AzamPay dashboard, make a test payment:**

```bash
# Watch logs on production server
tail -f /var/log/gunicorn/error.log | grep "AzamPay webhook"
```

**You should see:**
```
[INFO] AzamPay webhook received
[INFO] Webhook payload: {...}
[INFO] Found payment by transaction ID: {id}
[INFO] Payment {id} marked as completed
```

---

## 📋 Complete Production Configuration Checklist

### On Your Production Server (.env file):

- [ ] `BASE_URL=https://portal.maishaapp.co.tz`
- [ ] `AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- [ ] `AZAM_PAY_SANDBOX=False`
- [ ] `AZAM_PAY_BASE_URL=https://api.azampay.co.tz`
- [ ] `AZAM_PAY_CLIENT_ID=your_production_client_id`
- [ ] `AZAM_PAY_CLIENT_SECRET=your_production_client_secret`
- [ ] `AZAM_PAY_API_KEY=your_production_api_key`
- [ ] `DEBUG=False`

### In AzamPay Production Dashboard:

- [ ] Logged into **production** dashboard (not sandbox)
- [ ] Webhook URL configured: `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- [ ] Webhook URL saved and active

### After Deployment:

- [ ] Restart Django/Gunicorn server
- [ ] Test webhook endpoint with curl
- [ ] Make test payment
- [ ] Verify webhook received in logs
- [ ] Confirm payment status updated

---

## ❓ Common Questions

### Q: Do I need to login to configure the webhook URL?

**A:** Yes, you need to login to **AzamPay dashboard** to configure the webhook URL. But the webhook endpoint itself doesn't require login - it's a public API endpoint.

### Q: Why does `https://portal.maishaapp.co.tz/` redirect to login?

**A:** That's the homepage for human users. The webhook URL (`/api/v1/payments/webhook/azam-pay/`) is a different endpoint that doesn't redirect.

### Q: Can I test the webhook URL in a browser?

**A:** You can try, but:
- Browser will show an error (webhook expects POST with JSON)
- This is **normal** - webhooks are meant for server-to-server communication
- Use `curl` command instead for testing

### Q: Should I use sandbox or production credentials?

**A:** For production deployment:
- Use **production** credentials in `.env`
- Configure webhook URL in **production** AzamPay dashboard
- Set `AZAM_PAY_SANDBOX=False`

---

## 🔍 Troubleshooting

### If Webhook Returns 404:

1. **Check URL path:**
   ```bash
   # Verify the route exists
   python manage.py show_urls | grep webhook
   ```

2. **Check URL configuration:**
   - Ensure `.env` has correct `AZAM_PAY_WEBHOOK_URL`
   - Restart server after changing `.env`

3. **Check Nginx/Apache configuration:**
   - Ensure API routes are proxied correctly
   - Check for URL rewriting issues

### If Webhook Redirects to Login:

1. **Check Django settings:**
   - Verify `@permission_classes([])` is on webhook function
   - Verify `@csrf_exempt` is present

2. **Check middleware:**
   - Ensure no authentication middleware blocking API endpoints

### If Webhook Not Received:

1. **Check AzamPay dashboard:**
   - Verify webhook URL is saved correctly
   - Check if webhook is enabled/active

2. **Check server logs:**
   ```bash
   tail -f /var/log/gunicorn/error.log
   ```

3. **Check firewall/security:**
   - Ensure AzamPay IPs are not blocked
   - Check if HTTPS is working correctly

---

## ✅ Summary

**Webhook URL to use:**
```
https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
```

**Where to configure:**
1. ✅ Production `.env` file
2. ✅ AzamPay Production Dashboard (you login there)

**What happens:**
- AzamPay server calls the webhook URL directly
- No browser, no login required
- Payment status is updated automatically

---

**Status:** Ready to configure in production
