# Update Production .env File - Instructions

## ✅ Your Webhook URL is Correct!

**Webhook URL:** `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`

This is the correct format and matches what you've configured in AzamPay dashboard.

---

## 🔧 How to Update Production .env File

### Option 1: Manual Edit (Recommended for First Time)

**SSH into your production server and run:**

```bash
# 1. Navigate to your project directory
cd /path/to/your/Maisha_backend

# 2. Backup current .env file
cp .env .env.backup

# 3. Edit .env file
nano .env
# or
vi .env
```

**Find and update these lines:**

```bash
# Update or add these lines:
BASE_URL=https://portal.maishaapp.co.tz
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
AZAM_PAY_SANDBOX=False
```

**Save the file:**
- In `nano`: Press `Ctrl+X`, then `Y`, then `Enter`
- In `vi`: Press `Esc`, type `:wq`, then `Enter`

---

### Option 2: Using sed Commands (Quick Update)

**SSH into your production server and run:**

```bash
# Navigate to project directory
cd /path/to/your/Maisha_backend

# Backup .env
cp .env .env.backup

# Update BASE_URL
sed -i 's|^BASE_URL=.*|BASE_URL=https://portal.maishaapp.co.tz|' .env

# Update or add AZAM_PAY_WEBHOOK_URL
if grep -q "^AZAM_PAY_WEBHOOK_URL=" .env; then
    sed -i 's|^AZAM_PAY_WEBHOOK_URL=.*|AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/|' .env
else
    echo "AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/" >> .env
fi

# Ensure AZAM_PAY_SANDBOX is False
if grep -q "^AZAM_PAY_SANDBOX=" .env; then
    sed -i 's|^AZAM_PAY_SANDBOX=.*|AZAM_PAY_SANDBOX=False|' .env
else
    echo "AZAM_PAY_SANDBOX=False" >> .env
fi

# Verify changes
echo "=== Updated Values ==="
grep -E "(BASE_URL|AZAM_PAY_WEBHOOK_URL|AZAM_PAY_SANDBOX)" .env
```

---

### Option 3: Using the Provided Script

**If you have the script file on your production server:**

```bash
# 1. Upload update_production_env.sh to your server
# 2. Make it executable
chmod +x update_production_env.sh

# 3. Run it
./update_production_env.sh
```

---

## ✅ Verification

**After updating, verify the changes:**

```bash
# Check the updated values
grep -E "(BASE_URL|AZAM_PAY_WEBHOOK_URL|AZAM_PAY_SANDBOX)" .env
```

**Expected output:**
```
BASE_URL=https://portal.maishaapp.co.tz
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
AZAM_PAY_SANDBOX=False
```

---

## 🔄 After Updating .env

**1. Restart your Django/Gunicorn server:**

```bash
# For Gunicorn
sudo systemctl restart gunicorn
# or
sudo supervisorctl restart gunicorn

# For uWSGI
sudo systemctl restart uwsgi

# For Apache
sudo systemctl restart apache2
```

**2. Test the webhook endpoint:**

```bash
curl -X POST https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/ \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Expected:** Should return 200 or 400 (not 404)

**3. Check logs:**

```bash
tail -f /var/log/gunicorn/error.log | grep "AzamPay"
```

---

## 📋 Complete .env Configuration Checklist

**Ensure these are set in your production .env:**

```bash
# Base URL
BASE_URL=https://portal.maishaapp.co.tz

# AzamPay Webhook URL
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# AzamPay Production Settings
AZAM_PAY_SANDBOX=False
AZAM_PAY_BASE_URL=https://api.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# AzamPay Credentials (your production values)
AZAM_PAY_CLIENT_ID=your_production_client_id
AZAM_PAY_CLIENT_SECRET=your_production_client_secret
AZAM_PAY_API_KEY=your_production_api_key

# Django Settings
DEBUG=False
SECRET_KEY=your_production_secret_key
ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz
```

---

## ⚠️ Important Notes

1. **Backup First**: Always backup `.env` before making changes
2. **Restart Required**: Server must be restarted after changing `.env`
3. **No Spaces**: Ensure no spaces around `=` in `.env` file
4. **HTTPS Only**: Use `https://` not `http://` for production

---

## 🆘 Troubleshooting

### If changes don't take effect:

1. **Check file was saved:**
   ```bash
   cat .env | grep AZAM_PAY_WEBHOOK_URL
   ```

2. **Restart server:**
   ```bash
   sudo systemctl restart gunicorn
   ```

3. **Check server logs:**
   ```bash
   tail -f /var/log/gunicorn/error.log
   ```

---

**Status:** Ready to update production .env file
