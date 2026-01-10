# Production Deployment Checklist

## 🎯 Deployment Goal
Replace current production at `https://portal.maishaapp.co.tz/` with your local code (including AzamPay webhook fix).

---

## ✅ Pre-Deployment Checklist

### 1. Code Changes to Deploy
- [x] AzamPay webhook signature validation removed
- [x] Enhanced webhook error handling
- [x] All hardcoded values fixed (statistics now dynamic)
- [x] Swagger documentation complete
- [x] All recent fixes and improvements

### 2. Environment Variables (.env file)

**Critical settings to verify on production:**

```bash
# Database
DATABASE_NAME=maisha
DATABASE_USER=postgres
DATABASE_PASSWORD=your_production_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django
SECRET_KEY=your_production_secret_key
DEBUG=False  # IMPORTANT: Set to False in production
ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz

# AzamPay Configuration
AZAM_PAY_CLIENT_ID=your_production_client_id
AZAM_PAY_CLIENT_SECRET=your_production_client_secret
AZAM_PAY_API_KEY=your_production_api_key
AZAM_PAY_APP_NAME=mishap
AZAM_PAY_SANDBOX=False  # Set to False for production
AZAM_PAY_BASE_URL=https://api.azampay.co.tz  # Production URL
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
AZAM_PAY_WEBHOOK_SECRET=  # Not needed (signature validation removed)

# Base URL
BASE_URL=https://portal.maishaapp.co.tz

# Other settings
# ... (copy from your local .env, but update production values)
```

### 3. Database Backup
- [ ] **BACKUP PRODUCTION DATABASE FIRST!**
  ```bash
  pg_dump -U postgres -d maisha > backup_before_deployment_$(date +%Y%m%d_%H%M%S).sql
  ```

### 4. Static Files
- [ ] Collect static files:
  ```bash
  python manage.py collectstatic --noinput
  ```

### 5. Database Migrations
- [ ] Check for pending migrations:
  ```bash
  python manage.py showmigrations
  ```
- [ ] Apply migrations if needed:
  ```bash
  python manage.py migrate
  ```

---

## 🚀 Deployment Steps

### Step 1: Backup Current Production
```bash
# 1. Backup database
pg_dump -U postgres -d maisha > production_backup.sql

# 2. Backup current code (if using version control)
git tag production-backup-$(date +%Y%m%d)

# 3. Backup .env file
cp .env .env.backup
```

### Step 2: Upload Code to Production Server
```bash
# Option A: Using Git
git pull origin main  # or your branch name

# Option B: Using FTP/SFTP
# Upload all files except:
# - .env (keep existing)
# - __pycache__/
# - *.pyc
# - media/ (if separate)
# - staticfiles/ (will regenerate)
```

### Step 3: Update Environment Variables
```bash
# Edit production .env file
nano .env  # or vi .env

# Verify critical settings:
# - DEBUG=False
# - AZAM_PAY_SANDBOX=False
# - AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
# - Database credentials
```

### Step 4: Install Dependencies
```bash
# Activate virtual environment (if using)
source venv/bin/activate  # or your venv path

# Install/update packages
pip install -r requirements.txt
```

### Step 5: Run Database Migrations
```bash
python manage.py migrate
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Restart Application Server

**For Gunicorn:**
```bash
sudo systemctl restart gunicorn
# or
sudo supervisorctl restart gunicorn
```

**For uWSGI:**
```bash
sudo systemctl restart uwsgi
```

**For Apache/mod_wsgi:**
```bash
sudo systemctl restart apache2
```

**For Nginx + Gunicorn:**
```bash
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

### Step 8: Verify Deployment
```bash
# Check if server is running
curl https://portal.maishaapp.co.tz/

# Check application logs
tail -f /var/log/gunicorn/error.log
# or
tail -f /path/to/your/app.log
```

---

## 🧪 Post-Deployment Testing

### 1. Basic Functionality
- [ ] Homepage loads: `https://portal.maishaapp.co.tz/`
- [ ] Login works
- [ ] Dashboard accessible
- [ ] Static files loading (CSS, JS, images)

### 2. AzamPay Webhook Test (CRITICAL)
- [ ] Make a test payment through AzamPay
- [ ] Check server logs for webhook receipt:
  ```bash
  tail -f /var/log/gunicorn/error.log | grep "AzamPay webhook"
  ```
- [ ] Verify payment status updated in database
- [ ] Confirm NO "Invalid webhook signature" error

### 3. API Endpoints
- [ ] Swagger docs accessible: `https://portal.maishaapp.co.tz/swagger/`
- [ ] API endpoints responding correctly
- [ ] Authentication working

### 4. Database
- [ ] All data intact
- [ ] New features working
- [ ] Statistics calculating correctly (no hardcoded values)

---

## 🔍 Verification Commands

### Check Application Status
```bash
# Check if Django is running
python manage.py check --deploy

# Check for errors
python manage.py check
```

### Check Webhook Endpoint
```bash
# Test webhook endpoint (should return error but not "Invalid signature")
curl -X POST https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Check Logs
```bash
# Application logs
tail -f /var/log/gunicorn/error.log

# Django logs (if configured)
tail -f /path/to/your/app/logs/django.log

# System logs
journalctl -u gunicorn -f
```

---

## ⚠️ Important Notes

### 1. AzamPay Configuration
- **Production Mode**: Set `AZAM_PAY_SANDBOX=False`
- **Webhook URL**: Must be `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- **No Signature Validation**: Webhook will accept callbacks without signature (as per AzamPay instructions)

### 2. Security
- **DEBUG=False**: Critical for production security
- **SECRET_KEY**: Must be different from development
- **HTTPS**: Already configured (good!)

### 3. Database
- **Backup First**: Always backup before deployment
- **Migrations**: Test migrations on staging if possible

### 4. Static Files
- **Collect Static**: Run `collectstatic` after deployment
- **Nginx/Apache**: Ensure static files are served correctly

---

## 🐛 Troubleshooting

### If Webhook Still Shows "Invalid Signature" Error:
1. **Check code is updated**: Verify `payments/api_views.py` has signature validation removed
2. **Restart server**: Make sure application server restarted
3. **Check logs**: Look for "AzamPay webhook received" message
4. **Clear cache**: If using caching, clear it

### If Static Files Not Loading:
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check permissions
chmod -R 755 /path/to/staticfiles/
```

### If Database Errors:
```bash
# Check migrations
python manage.py showmigrations

# Rollback if needed (from backup)
psql -U postgres -d maisha < production_backup.sql
```

---

## 📞 After Deployment

### 1. Monitor Logs
- Watch for errors in first 24 hours
- Check webhook processing
- Monitor payment transactions

### 2. Test AzamPay Integration
- Make test payment
- Verify webhook received
- Confirm payment status updated
- Report to AzamPay technical support

### 3. User Communication
- Inform users of deployment (if needed)
- Monitor for user-reported issues

---

## ✅ Deployment Confirmation

After deployment, verify:
- [ ] Application running without errors
- [ ] Webhook endpoint accessible
- [ ] Test payment processed successfully
- [ ] No "Invalid webhook signature" errors
- [ ] All features working correctly

---

**Status:** Ready for deployment  
**Date:** Review Date  
**Next Step:** Deploy to production and test
