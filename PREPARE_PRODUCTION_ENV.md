# Prepare Production .env File Before Upload

## 🎯 Goal
Configure your `.env` file locally with production values, so when you upload everything, it's ready to go!

---

## ✅ Step-by-Step Guide

### Step 1: Backup Your Current Local .env

**On your local machine:**

```bash
# Backup your local .env (for development)
cp .env .env.local.backup
```

### Step 2: Update Local .env with Production Values

**Edit your local `.env` file and update these values:**

```bash
# =============================================================================
# PRODUCTION VALUES - Update these before uploading
# =============================================================================

# Database (Production)
DATABASE_NAME=maisha
DATABASE_USER=postgres
DATABASE_PASSWORD=YOUR_PRODUCTION_DATABASE_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django (Production)
SECRET_KEY=YOUR_PRODUCTION_SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz

# AzamPay (Production)
AZAM_PAY_CLIENT_ID=YOUR_PRODUCTION_CLIENT_ID
AZAM_PAY_CLIENT_SECRET=YOUR_PRODUCTION_CLIENT_SECRET
AZAM_PAY_API_KEY=YOUR_PRODUCTION_API_KEY
AZAM_PAY_APP_NAME=mishap
AZAM_PAY_SANDBOX=False
AZAM_PAY_BASE_URL=https://api.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
AZAM_PAY_WEBHOOK_SECRET=

# Base URL (Production)
BASE_URL=https://portal.maishaapp.co.tz
```

### Step 3: Verify Critical Settings

**Before uploading, verify these are correct:**

- [ ] `DEBUG=False` (CRITICAL for production)
- [ ] `AZAM_PAY_SANDBOX=False` (Production mode)
- [ ] `AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- [ ] `BASE_URL=https://portal.maishaapp.co.tz`
- [ ] All production credentials are correct

### Step 4: Upload to Production

**When uploading to production server:**

1. **Upload all files including `.env`**
2. **OR** if production already has `.env`, you can:
   - Upload `.env.production.template` as reference
   - Manually copy values to production `.env`

### Step 5: After Upload - Verify on Production Server

**SSH into production server and verify:**

```bash
# Navigate to project directory
cd /path/to/your/Maisha_backend

# Check critical settings
grep -E "(DEBUG|AZAM_PAY_SANDBOX|AZAM_PAY_WEBHOOK_URL|BASE_URL)" .env
```

**Expected output:**
```
DEBUG=False
AZAM_PAY_SANDBOX=False
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
BASE_URL=https://portal.maishaapp.co.tz
```

---

## ⚠️ Important Warnings

### 1. **Backup Production .env First!**

**If production already has a `.env` file, BACKUP IT FIRST:**

```bash
# On production server
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
```

### 2. **Don't Overwrite Existing Production Credentials**

If production `.env` already has correct values, you might want to:
- Keep the existing `.env` on production
- Only update specific values that changed

### 3. **Never Commit .env to Git**

Make sure `.env` is in `.gitignore`:
```bash
# Check .gitignore
cat .gitignore | grep .env
```

---

## 🔄 Two Approaches

### Approach A: Upload Complete .env (Recommended if starting fresh)

**If production doesn't have `.env` or you want to replace it:**

1. Update local `.env` with production values
2. Upload entire project including `.env`
3. Verify on production server

### Approach B: Keep Existing Production .env (Safer)

**If production already has working `.env`:**

1. **Backup production `.env` first**
2. Upload code (but NOT `.env`)
3. Manually update only changed values in production `.env`:
   ```bash
   # On production server
   nano .env
   # Update only: AZAM_PAY_WEBHOOK_URL, BASE_URL, AZAM_PAY_SANDBOX
   ```

---

## 📋 Pre-Upload Checklist

**Before uploading, ensure your local `.env` has:**

- [ ] `DEBUG=False`
- [ ] `AZAM_PAY_SANDBOX=False`
- [ ] `AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- [ ] `BASE_URL=https://portal.maishaapp.co.tz`
- [ ] Production database credentials
- [ ] Production AzamPay credentials
- [ ] Production `SECRET_KEY`
- [ ] `ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz`

---

## 🚀 Quick Setup Script

**Create a script to prepare production .env locally:**

```bash
#!/bin/bash
# prepare_production_env.sh

echo "Preparing production .env file..."

# Backup local .env
cp .env .env.local.backup

# Update critical production settings
sed -i 's/DEBUG=True/DEBUG=False/' .env
sed -i 's|BASE_URL=.*|BASE_URL=https://portal.maishaapp.co.tz|' .env
sed -i 's|AZAM_PAY_SANDBOX=True|AZAM_PAY_SANDBOX=False|' .env
sed -i 's|AZAM_PAY_WEBHOOK_URL=.*|AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/|' .env
sed -i 's|AZAM_PAY_BASE_URL=.*|AZAM_PAY_BASE_URL=https://api.azampay.co.tz|' .env

echo "✅ Production .env prepared!"
echo "⚠️  Remember to update production credentials manually!"
echo ""
echo "Review: grep -E '(DEBUG|BASE_URL|AZAM_PAY)' .env"
```

---

## ✅ Summary

**Yes, you can configure `.env` locally before uploading!**

**Steps:**
1. ✅ Update local `.env` with production values
2. ✅ Verify critical settings (`DEBUG=False`, webhook URL, etc.)
3. ✅ Upload entire project including `.env`
4. ✅ On production: Verify `.env` values
5. ✅ Restart server

**OR** (if production already has `.env`):
1. ✅ Backup production `.env` first
2. ✅ Upload code (but keep existing production `.env`)
3. ✅ Manually update only changed values

---

**Status:** Ready to prepare and upload!
