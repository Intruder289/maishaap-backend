# Sandbox Testing on Hosted Server (HTTPS)

## 🎯 Goal
Deploy your system to a server with HTTPS, but keep it in **sandbox mode** for testing before going to production.

---

## ✅ This Approach is Correct!

**Why this is good:**
- ✅ Test with real HTTPS (like production)
- ✅ Test webhooks with real server (not localhost)
- ✅ Verify everything works before production
- ✅ Safe - using sandbox, not real money

---

## 🔧 Configuration for Sandbox Testing on Hosted Server

### Step 1: Deploy to Server with HTTPS

**Deploy your code to your server:**
- Example: `https://test.maishaapp.co.tz` or `https://portal.maishaapp.co.tz`
- Ensure HTTPS is working
- Ensure Django is running

### Step 2: Configure .env for Sandbox Testing

**On your hosted server, update `.env` file:**

```bash
# =============================================================================
# SANDBOX TESTING CONFIGURATION (Hosted Server with HTTPS)
# =============================================================================

# Django Settings
DEBUG=True  # Can be True for testing, but False is safer
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=your-hosted-domain.com,www.your-hosted-domain.com

# Base URL (Your hosted HTTPS URL)
BASE_URL=https://your-hosted-domain.com

# AzamPay SANDBOX Configuration
AZAM_PAY_CLIENT_ID=your_sandbox_client_id
AZAM_PAY_CLIENT_SECRET=your_sandbox_client_secret
AZAM_PAY_API_KEY=your_sandbox_api_key
AZAM_PAY_APP_NAME=mishap

# SANDBOX Mode (Important!)
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# Webhook URL (Your hosted HTTPS URL)
AZAM_PAY_WEBHOOK_URL=https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/
AZAM_PAY_WEBHOOK_SECRET=

# Database (Your hosted database)
DATABASE_NAME=maisha
DATABASE_USER=postgres
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Step 3: Update AzamPay Sandbox Dashboard

**Login to AzamPay Sandbox Dashboard:**
- Go to: `https://sandbox.azampay.co.tz` (or your sandbox dashboard URL)
- Navigate to: Settings → Webhooks/Callbacks

**Configure Webhook URL:**
```
https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/
```

**Important:** Use your **hosted HTTPS URL**, not localhost!

### Step 4: Restart Server

**After updating `.env`, restart your Django server:**

```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For uWSGI
sudo systemctl restart uwsgi

# For Apache
sudo systemctl restart apache2
```

---

## 🧪 Testing Checklist

### 1. Verify Configuration

**On your hosted server, check:**

```bash
# Check .env values
grep -E "(AZAM_PAY_SANDBOX|AZAM_PAY_WEBHOOK_URL|BASE_URL)" .env
```

**Expected:**
```
AZAM_PAY_SANDBOX=True
AZAM_PAY_WEBHOOK_URL=https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/
BASE_URL=https://your-hosted-domain.com
```

### 2. Test Webhook Endpoint

**From any machine:**

```bash
curl -X POST https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected:** Should return 200 or 400 (not 404)

### 3. Make Test Payment

1. **Initiate payment** through your hosted website
2. **Complete payment** on AzamPay sandbox
3. **Check server logs** for webhook:

```bash
tail -f /var/log/gunicorn/error.log | grep "AzamPay webhook"
```

**Expected logs:**
```
[INFO] AzamPay webhook received
[INFO] Webhook payload: {...}
[INFO] Found payment by transaction ID: {id}
[INFO] Payment {id} marked as completed
```

### 4. Verify Payment Status

- Check in your database/admin panel
- Payment should be marked as "completed"
- Transaction record should be created

---

## 📋 Complete Configuration Summary

### On Your Hosted Server (.env):

```bash
# SANDBOX MODE
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz

# Your Hosted HTTPS URL
BASE_URL=https://your-hosted-domain.com
AZAM_PAY_WEBHOOK_URL=https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/

# Sandbox Credentials
AZAM_PAY_CLIENT_ID=your_sandbox_client_id
AZAM_PAY_CLIENT_SECRET=your_sandbox_client_secret
AZAM_PAY_API_KEY=your_sandbox_api_key
```

### In AzamPay Sandbox Dashboard:

- **Webhook URL:** `https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/`
- **Environment:** Sandbox (not production)

---

## ⚠️ Important Notes

### 1. **Sandbox vs Production**

**Sandbox Mode (`AZAM_PAY_SANDBOX=True`):**
- Uses `https://sandbox.azampay.co.tz`
- Test payments only (no real money)
- Configure webhook in **sandbox dashboard**

**Production Mode (`AZAM_PAY_SANDBOX=False`):**
- Uses `https://api.azampay.co.tz`
- Real payments
- Configure webhook in **production dashboard**

### 2. **HTTPS Required**

- Webhooks require HTTPS
- Your hosted server must have valid SSL certificate
- AzamPay will not send webhooks to HTTP URLs

### 3. **Two Separate Dashboards**

- **Sandbox Dashboard:** For testing
- **Production Dashboard:** For live payments
- Each has its own webhook URL configuration

---

## 🔄 Migration Path: Sandbox → Production

### When Ready for Production:

1. **Update `.env` on hosted server:**
   ```bash
   AZAM_PAY_SANDBOX=False
   AZAM_PAY_BASE_URL=https://api.azampay.co.tz
   AZAM_PAY_CLIENT_ID=your_production_client_id
   AZAM_PAY_CLIENT_SECRET=your_production_client_secret
   AZAM_PAY_API_KEY=your_production_api_key
   ```

2. **Update AzamPay Production Dashboard:**
   - Login to production dashboard
   - Configure webhook URL: `https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/`

3. **Restart server**

4. **Test with real payment** (small amount first!)

---

## ✅ Summary

**Your Plan:**
1. ✅ Deploy to server with HTTPS
2. ✅ Configure for sandbox testing
3. ✅ Test thoroughly in sandbox
4. ✅ Switch to production when ready

**Configuration:**
- `AZAM_PAY_SANDBOX=True` (for testing)
- Webhook URL: Your hosted HTTPS URL
- Configure in AzamPay **sandbox** dashboard

**This is the correct approach!** 🎯

---

**Status:** Ready for sandbox testing on hosted server
