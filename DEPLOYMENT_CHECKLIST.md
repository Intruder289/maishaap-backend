# Deployment Checklist for Invalid Vendor Fix

## ✅ Files to Upload

**ONLY ONE FILE NEEDS TO BE UPDATED:**
- `payments/gateway_service.py`

## 📋 Deployment Steps

### Step 1: Upload the File

Upload `payments/gateway_service.py` to your server at:
```
/home/maishaapp/app/payments/gateway_service.py
```
(Adjust path based on your actual server structure)

### Step 2: Clear Python Cache (IMPORTANT!)

Python caches compiled bytecode (.pyc files). Clear it to ensure new code loads:

```bash
# SSH into your server
ssh your-server

# Navigate to your project directory
cd /home/maishaapp/app  # or wherever your project is

# Remove all Python cache files
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete

# Or manually remove cache in payments directory
rm -rf payments/__pycache__
rm -f payments/*.pyc
```

### Step 3: Restart Gunicorn

```bash
# Option 1: Using systemd
sudo systemctl restart gunicorn

# Option 2: Using supervisor
sudo supervisorctl restart gunicorn

# Option 3: Send HUP signal to reload
sudo pkill -HUP gunicorn

# Option 4: Full restart (if using systemd)
sudo systemctl stop gunicorn
sudo systemctl start gunicorn
```

### Step 4: Verify Deployment

After restarting, make a test payment and check logs. You should see:

**✅ GOOD - Fix is working:**
```
[AZAMPAY FIX] Using CLIENT_ID as X-API-Key (API_KEY not set): 019bb775-c4be-7171-9...
[AZAMPAY FIX] Headers: Authorization=Bearer ***, X-API-Key=***
[AZAMPAY FIX] Provider mapping: AIRTEL -> Airtel
```

**❌ BAD - Old code still running:**
```
No X-API-Key available - authentication may fail
[AZAMPAY] Headers: Authorization=Bearer ***, X-API-Key=none
```

## 🔍 Troubleshooting

### If logs don't show "[AZAMPAY FIX]" messages:

1. **Verify file was uploaded:**
   ```bash
   grep -n "AZAMPAY FIX" /home/maishaapp/app/payments/gateway_service.py
   ```
   Should show multiple lines with "[AZAMPAY FIX]"

2. **Check file permissions:**
   ```bash
   ls -la /home/maishaapp/app/payments/gateway_service.py
   ```
   Should be readable by gunicorn user

3. **Clear cache again and restart:**
   ```bash
   find . -name "*.pyc" -delete
   find . -type d -name __pycache__ -exec rm -r {} +
   sudo systemctl restart gunicorn
   ```

4. **Check gunicorn is using correct Python:**
   ```bash
   # Check which Python gunicorn uses
   ps aux | grep gunicorn
   # Should show Python path
   ```

### If you see "[AZAMPAY FIX]" but still get "Invalid Vendor":

This means the code is working, but there's a vendor account issue:

1. **Check AzamPay Production Dashboard:**
   - Login: https://developers.azampay.co.tz/
   - Verify vendor account is **ACTIVATED** and **APPROVED**
   - Verify providers (Airtel, Tigo, Mpesa) are **ENABLED**
   - Contact AzamPay support if account appears inactive

## 📝 Quick Verification Command

Run this on your server to verify the fix is in the file:

```bash
grep -A 2 "Using CLIENT_ID as X-API-Key" /home/maishaapp/app/payments/gateway_service.py
```

Should output:
```python
                headers["X-API-Key"] = client_id_value
                logger.error(f"[AZAMPAY FIX] Using CLIENT_ID as X-API-Key (API_KEY not set): {client_id_value[:20]}...")
                print(f"[AZAMPAY FIX] Using CLIENT_ID as X-API-Key (API_KEY not set): {client_id_value[:20]}...")
```
