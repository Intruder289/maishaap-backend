# Production Readiness Checklist ✅

## 🔍 Pre-Deployment Verification

Use this checklist to ensure your application is ready for production deployment.

---

## ✅ 1. Environment Configuration (.env file)

### Critical Settings
- [ ] **ENVIRONMENT=production**
  - ✅ Sets production security settings
  - ✅ Enables HTTPS-only cookies
  - ✅ Restricts CORS origins

- [ ] **DEBUG=False**
  - ✅ Prevents exposing sensitive error information
  - ✅ Improves performance

- [ ] **ALLOWED_HOSTS=portal.maishaapp.co.tz**
  - ✅ Set to your production domain (NOT `*`)
  - ✅ Include all domains/subdomains that will access the app

- [ ] **SECRET_KEY**
  - ✅ Strong, unique key (NOT the default insecure key)
  - ✅ Different from development/staging keys

---

## ✅ 2. AZAM Pay Production Configuration

### Credentials
- [ ] **AZAM_PAY_CLIENT_ID**
  - ✅ Production Client ID: `019bb775-c4be-7171-904f-9106b7e5002a`

- [ ] **AZAM_PAY_CLIENT_SECRET**
  - ✅ Production Client Secret (complete, no line breaks)

- [ ] **AZAM_PAY_APP_NAME=maishaapp**
  - ✅ Matches AZAM Pay dashboard exactly (case-sensitive)

### Production Mode
- [ ] **AZAM_PAY_SANDBOX=False**
  - ✅ CRITICAL: Must be False for production

### Endpoints
- [ ] **AZAM_PAY_AUTHENTICATOR_BASE_URL=https://authenticator.azampay.co.tz**
  - ✅ Production authenticator endpoint

- [ ] **AZAM_PAY_CHECKOUT_BASE_URL=https://checkout.azampay.co.tz**
  - ✅ Production checkout endpoint

### Webhook Configuration
- [ ] **BASE_URL=https://portal.maishaapp.co.tz**
  - ✅ Your production domain (HTTPS)

- [ ] **AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/**
  - ✅ Full webhook URL (matches Django URL config)
  - ✅ Must be accessible from internet
  - ✅ Configured in AZAM Pay dashboard

---

## ✅ 3. Code Verification

### Settings Configuration
- [x] **`Maisha_backend/settings.py`**
  - ✅ `AZAM_PAY_CHECKOUT_BASE_URL` setting added
  - ✅ `AZAM_PAY_AUTHENTICATOR_BASE_URL` setting added
  - ✅ `ENVIRONMENT` variable properly used
  - ✅ `SESSION_COOKIE_SECURE` set based on environment

### Gateway Service
- [x] **`payments/gateway_service.py`**
  - ✅ Production authenticator endpoint configured
  - ✅ Production checkout endpoint configured
  - ✅ Webhook URL construction logic correct

### URL Configuration
- [x] **Webhook endpoint path**
  - ✅ `/api/v1/payments/webhook/azam-pay/` matches Django URLs

---

## ✅ 4. Security Checklist

### Django Security Settings
- [ ] **DEBUG=False** ✅
- [ ] **ALLOWED_HOSTS** set (not `*`) ✅
- [ ] **SECRET_KEY** is strong and unique ✅
- [ ] **SESSION_COOKIE_SECURE=True** (when ENVIRONMENT=production) ✅
- [ ] **SESSION_COOKIE_HTTPONLY=True** ✅
- [ ] **CSRF protection** enabled ✅

### HTTPS Configuration
- [ ] **All URLs use HTTPS** (not HTTP)
  - ✅ BASE_URL
  - ✅ AZAM_PAY_WEBHOOK_URL
  - ✅ AZAM_PAY_AUTHENTICATOR_BASE_URL
  - ✅ AZAM_PAY_CHECKOUT_BASE_URL

### CORS Configuration
- [ ] **CORS_ALLOW_ALL_ORIGINS=False** (in production)
- [ ] **CORS_ALLOWED_ORIGINS** configured with production domains

---

## ✅ 5. Database Configuration

- [ ] **Production database credentials** configured
  - ✅ DATABASE_NAME
  - ✅ DATABASE_USER
  - ✅ DATABASE_PASSWORD
  - ✅ DATABASE_HOST
  - ✅ DATABASE_PORT

- [ ] **Database migrations** applied
  ```bash
  python manage.py migrate
  ```

- [ ] **Static files** collected
  ```bash
  python manage.py collectstatic --noinput
  ```

---

## ✅ 6. Server Configuration

### Web Server (Nginx/Apache)
- [ ] **HTTPS/SSL certificate** installed and valid
- [ ] **Static files** served correctly
- [ ] **Media files** served correctly
- [ ] **Reverse proxy** configured for Django

### Application Server (Gunicorn/uWSGI)
- [ ] **Worker processes** configured appropriately
- [ ] **Timeout settings** configured
- [ ] **Logging** configured

### Process Manager (systemd/supervisor)
- [ ] **Auto-restart** on failure configured
- [ ] **Log rotation** configured

---

## ✅ 7. AZAM Pay Dashboard Configuration

### Production Dashboard Settings
- [ ] **Webhook URL** configured in AZAM Pay dashboard:
  ```
  https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
  ```

- [ ] **App Name** matches: `maishaapp`

- [ ] **Client ID** matches production credentials

- [ ] **Production mode** enabled (not sandbox)

---

## ✅ 8. Testing Checklist

### Pre-Production Tests
- [ ] **Test token generation**
  - Verify authenticator endpoint works
  - Check logs for successful token retrieval

- [ ] **Test payment initiation**
  - Create a test payment
  - Verify checkout endpoint is called correctly

- [ ] **Test webhook endpoint**
  - Verify endpoint is accessible
  - Test with sample webhook payload (if possible)

- [ ] **Test database connectivity**
  - Verify production database is accessible
  - Test read/write operations

- [ ] **Test static files**
  - Verify CSS/JS files load correctly
  - Check media file uploads/downloads

---

## ✅ 9. Monitoring & Logging

- [ ] **Error logging** configured
- [ ] **Access logs** configured
- [ ] **AZAM Pay API logs** enabled
- [ ] **Database query logging** (optional, for debugging)

---

## ✅ 10. Backup & Recovery

- [ ] **Database backups** configured
- [ ] **Backup schedule** established
- [ ] **Recovery procedure** documented
- [ ] **Environment variables** backed up securely

---

## 🚀 Deployment Steps

1. **Update `.env` file** with all production values
2. **Restart Django server** to load new environment variables
3. **Run migrations**: `python manage.py migrate`
4. **Collect static files**: `python manage.py collectstatic --noinput`
5. **Restart web server** (Nginx/Apache)
6. **Restart application server** (Gunicorn/uWSGI)
7. **Verify application** is accessible
8. **Test payment flow** with a small test transaction
9. **Monitor logs** for any errors

---

## ⚠️ Common Issues to Watch For

### Issue 1: Webhook Not Receiving Calls
- **Check**: Webhook URL is accessible from internet
- **Check**: URL matches exactly in AZAM Pay dashboard
- **Check**: Firewall/security groups allow incoming POST requests

### Issue 2: Token Generation Fails
- **Check**: `AZAM_PAY_SANDBOX=False`
- **Check**: Client ID and Secret are correct
- **Check**: App Name matches dashboard exactly
- **Check**: Authenticator endpoint is accessible

### Issue 3: Payment Checkout Fails
- **Check**: Checkout endpoint URL is correct
- **Check**: Token is valid and not expired
- **Check**: Phone number format is correct (2557XXXXXXXX)

### Issue 4: Session/Cookie Issues
- **Check**: `SESSION_COOKIE_SECURE=True` in production
- **Check**: HTTPS is properly configured
- **Check**: Domain matches in cookie settings

---

## 📋 Final Verification

Before going live, verify:

- [ ] All checklist items above are completed
- [ ] `.env` file is NOT committed to version control
- [ ] Production credentials are secure
- [ ] Test payment transaction succeeds
- [ ] Webhook receives and processes callbacks
- [ ] Application logs show no critical errors
- [ ] Performance is acceptable

---

## ✅ Production Ready Status

**Status**: ⏳ **Pending Verification**

Complete all checklist items above, then mark as:
- ✅ **READY FOR PRODUCTION** - All checks passed
- ⚠️ **NEEDS ATTENTION** - Some items need fixing
- ❌ **NOT READY** - Critical issues found

---

**Last Updated**: 2026-01-12
**Next Review**: After deployment
