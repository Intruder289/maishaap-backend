# 🚀 Deployment Checklist - Sandbox Testing on Hosted Server

## ✅ Pre-Deployment Status

**Current Configuration:**
- ✅ `AZAM_PAY_SANDBOX=True` (Sandbox mode)
- ✅ `BASE_URL=https://portal.maishaapp.co.tz`
- ✅ `AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- ✅ `DEBUG=False` (Production-ready)
- ✅ `ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz`
- ✅ `SECRET_KEY` is set
- ✅ Database configuration via environment variables
- ✅ `AZAM_PAY_API_KEY` not set (OK - code uses Client ID in sandbox)

---

## 📋 Deployment Steps

### Step 1: Upload Files to Server ✅

**Upload these to your hosted server:**
- [ ] All project files (entire `Maisha_backend` directory)
- [ ] `.env` file (with your current configuration)
- [ ] `requirements.txt`
- [ ] Static files (if any)
- [ ] Media files (if any)

**Important:** Make sure `.env` file is uploaded and in the project root!

---

### Step 2: Server Requirements Check

**On your hosted server, verify:**

- [ ] **Python 3.8+** is installed
  ```bash
  python3 --version
  ```

- [ ] **PostgreSQL** is installed and running
  ```bash
  sudo systemctl status postgresql
  ```

- [ ] **Database exists:**
  ```bash
  psql -U postgres -l | grep maisha
  ```

- [ ] **HTTPS/SSL** is configured and working
  - Visit: `https://portal.maishaapp.co.tz`
  - Should show valid SSL certificate

- [ ] **Web server** is configured (Nginx/Apache)
- [ ] **WSGI server** is configured (Gunicorn/uWSGI)

---

### Step 3: Install Dependencies

**On your hosted server:**

```bash
cd /path/to/Maisha_backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### Step 4: Update .env on Server (if needed)

**Verify these settings in `.env` on your server:**

```bash
# Sandbox Mode
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz

# Your Hosted URL
BASE_URL=https://portal.maishaapp.co.tz
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# Sandbox Credentials (from your local .env)
AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9f289d1
AZAM_PAY_CLIENT_SECRET=your_sandbox_secret
AZAM_PAY_APP_NAME=mishap

# Django Settings
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz

# Database (Your server's database)
DATABASE_NAME=maisha
DATABASE_USER=postgres
DATABASE_PASSWORD=your_server_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**⚠️ Important:** Update `DATABASE_PASSWORD` to your server's actual database password!

---

### Step 5: Run Database Migrations

**On your hosted server:**

```bash
cd /path/to/Maisha_backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

---

### Step 6: Configure AzamPay Sandbox Dashboard

**1. Login to AzamPay Sandbox Dashboard:**
   - URL: `https://sandbox.azampay.co.tz/` (or your sandbox dashboard URL)

**2. Navigate to Webhook Settings:**
   - Go to: Settings → Webhooks/Callbacks
   - Or: App Settings → Webhooks

**3. Set Webhook URL:**
   ```
   https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
   ```

**4. Save the configuration**

**⚠️ Important:** Make sure you're in the **SANDBOX** dashboard, not production!

---

### Step 7: Restart Web Server

**After updating `.env` and configuring webhooks:**

```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For uWSGI
sudo systemctl restart uwsgi

# For Apache
sudo systemctl restart apache2

# For Nginx (if needed)
sudo systemctl restart nginx
```

---

## 🧪 Testing Checklist

### Test 1: Verify Webhook Endpoint is Accessible

**From any machine:**

```bash
curl -X POST https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected:** Should return `200 OK` or `400 Bad Request` (NOT `404 Not Found`)

---

### Test 2: Check Server Logs

**On your server:**

```bash
# Check Django logs
tail -f /var/log/gunicorn/error.log

# Or check your Django log file
tail -f /path/to/Maisha_backend/logs/django.log
```

**Expected:** No critical errors, webhook endpoint should be accessible

---

### Test 3: Make a Test Payment

**1. Initiate a payment:**
   - Go to your hosted website: `https://portal.maishaapp.co.tz`
   - Create a booking or rent invoice
   - Click "Pay with AzamPay"

**2. Complete payment on AzamPay sandbox:**
   - Use test credentials
   - Complete the payment flow

**3. Check webhook received:**
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

**4. Verify in database:**
   - Check payment status in your admin panel
   - Payment should be marked as "completed"
   - Transaction record should be created

---

## ✅ Success Criteria

**You're ready if:**
- ✅ Website loads at `https://portal.maishaapp.co.tz`
- ✅ Webhook endpoint returns 200/400 (not 404)
- ✅ Test payment can be initiated
- ✅ Webhook is received after payment
- ✅ Payment status updates in database
- ✅ No critical errors in logs

---

## ⚠️ Important Notes

### 1. **Sandbox vs Production**

**Current Setup (Sandbox):**
- `AZAM_PAY_SANDBOX=True`
- Uses `https://sandbox.azampay.co.tz`
- Test payments only (no real money)
- Configure webhook in **sandbox dashboard**

**When Ready for Production:**
- Change `AZAM_PAY_SANDBOX=False`
- Update to production credentials
- Configure webhook in **production dashboard**

### 2. **HTTPS Required**

- ✅ Your server must have valid SSL certificate
- ✅ AzamPay will NOT send webhooks to HTTP URLs
- ✅ All URLs must use `https://`

### 3. **Database Password**

- ⚠️ **CRITICAL:** Update `DATABASE_PASSWORD` in `.env` to match your server's database password
- The current password (`alfred`) is for local development only

### 4. **SECRET_KEY**

- ⚠️ **CRITICAL:** Generate a new strong `SECRET_KEY` for production
- Current key is for development only
- Use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

---

## 🆘 Troubleshooting

### Issue: Webhook returns 404

**Solution:**
- Check URL is correct: `/api/v1/payments/webhook/azam-pay/`
- Verify Django URLs are configured
- Check server logs for routing errors

### Issue: Webhook not received

**Solution:**
- Verify webhook URL in AzamPay sandbox dashboard
- Check HTTPS is working
- Check server firewall allows incoming connections
- Verify webhook URL is accessible from outside

### Issue: Database connection error

**Solution:**
- Verify database credentials in `.env`
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database exists: `psql -U postgres -l`
- Check database user has permissions

### Issue: Payment not updating

**Solution:**
- Check webhook logs for errors
- Verify payment lookup logic
- Check database for transaction records
- Review server logs for exceptions

---

## 📞 Next Steps After Successful Testing

**Once sandbox testing is successful:**

1. **Test thoroughly:**
   - Multiple payment scenarios
   - Different payment amounts
   - Error handling
   - Webhook retries

2. **When ready for production:**
   - Update `.env`: `AZAM_PAY_SANDBOX=False`
   - Get production credentials from AzamPay
   - Update webhook URL in production dashboard
   - Test with small real payment first!

---

## ✅ Ready to Deploy!

**Your configuration is ready for sandbox testing on the hosted server!**

**Summary:**
- ✅ Code is ready
- ✅ Configuration is correct
- ✅ Sandbox mode enabled
- ✅ Production URLs configured
- ✅ Database uses environment variables
- ✅ Security settings configured

**Proceed with deployment!** 🚀
