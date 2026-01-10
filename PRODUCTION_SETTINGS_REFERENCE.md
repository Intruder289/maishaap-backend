# Production Settings Reference

## ⚠️ Critical Settings to Change for Production

### 1. Security Settings

**File:** `Maisha_backend/settings.py` or `.env`

```python
# ❌ CURRENT (Development):
DEBUG = True
SECRET_KEY = 'django-insecure--lcr^7cu6oeuae)6&4(*s8h_4e@2aph+104tmjtm%2nt0n0*m6'
ALLOWED_HOSTS = ['*']

# ✅ PRODUCTION (Must Change):
DEBUG = False  # CRITICAL: Must be False
SECRET_KEY = config('SECRET_KEY')  # Use environment variable
ALLOWED_HOSTS = ['portal.maishaapp.co.tz', 'www.portal.maishaapp.co.tz']
```

**In .env file:**
```bash
DEBUG=False
SECRET_KEY=your_strong_random_secret_key_here
ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz
```

### 2. AzamPay Production Settings

**In .env file:**
```bash
# Production Mode
AZAM_PAY_SANDBOX=False
AZAM_PAY_BASE_URL=https://api.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# Webhook URL (must be HTTPS)
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# Production Credentials (from AzamPay dashboard)
AZAM_PAY_CLIENT_ID=your_production_client_id
AZAM_PAY_CLIENT_SECRET=your_production_client_secret
AZAM_PAY_API_KEY=your_production_api_key
AZAM_PAY_APP_NAME=mishap

# Webhook Secret (not needed - signature validation removed)
AZAM_PAY_WEBHOOK_SECRET=
```

### 3. Database Settings

**In .env file:**
```bash
DATABASE_NAME=maisha
DATABASE_USER=postgres
DATABASE_PASSWORD=your_production_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 4. Base URL

**In .env file:**
```bash
BASE_URL=https://portal.maishaapp.co.tz
```

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is strong and unique (not the development key)
- [ ] `ALLOWED_HOSTS` only includes your domain
- [ ] Database password is strong
- [ ] HTTPS is enabled (you already have this ✅)
- [ ] Environment variables are secure (not in code)
- [ ] `.env` file is not in version control

---

## 📝 Quick Deployment Steps

1. **Backup database**
2. **Upload code** (excluding .env)
3. **Update .env** with production values
4. **Run migrations**: `python manage.py migrate`
5. **Collect static**: `python manage.py collectstatic --noinput`
6. **Restart server**: `sudo systemctl restart gunicorn` (or your server)
7. **Test webhook**: Make test payment

---

## 🧪 Post-Deployment Test

```bash
# 1. Check if site loads
curl https://portal.maishaapp.co.tz/

# 2. Check webhook endpoint (should not return "Invalid signature")
curl -X POST https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# 3. Check logs
tail -f /var/log/gunicorn/error.log
```

---

**Remember:** The webhook signature validation has been removed, so webhooks will work without signature verification.
