# Fix for "Invalid Vendor" Error - Deployment Guide

## 🔍 Problem Identified

Your server logs show:
```
No X-API-Key available - authentication may fail
Response returned 200 but success=false or no transactionId. Message: Your request could not be initiated. Please contact system admin. Invalid Vendor
```

**Root Cause:** The checkout endpoint requires the `X-API-Key` header, but the code wasn't sending it in production mode when `AZAM_PAY_API_KEY` was not set.

## ✅ Fix Applied

Updated `payments/gateway_service.py` to:
1. Use `CLIENT_ID` as `X-API-Key` in production when `API_KEY` is not set
2. Added better logging to track which key is being used
3. Added provider format mapping (AIRTEL → Airtel, etc.)

## 📋 Files Changed

1. **payments/gateway_service.py**
   - Fixed X-API-Key header logic (lines 592-608)
   - Added provider format mapping (lines 538-555)

## 🚀 Deployment Steps

### Step 1: Upload Updated Files to Server

Upload the updated `payments/gateway_service.py` file to your production server.

### Step 2: Restart Your Django/Gunicorn Server

**For Gunicorn:**
```bash
# Find your gunicorn process
ps aux | grep gunicorn

# Restart gunicorn (method depends on your setup)
# Option 1: If using systemd
sudo systemctl restart gunicorn

# Option 2: If using supervisor
sudo supervisorctl restart gunicorn

# Option 3: If running manually, kill and restart
pkill -HUP gunicorn
```

**For other setups:**
- If using Docker: `docker-compose restart`
- If using PM2: `pm2 restart your-app`
- If using uWSGI: `touch /path/to/uwsgi.ini` (reloads)

### Step 3: Verify the Fix

After restarting, check the logs when making a payment. You should see:

**✅ Good Log (what you should see):**
```
Using CLIENT_ID as X-API-Key (API_KEY not set): 019bb775-c4be-7171-9...
[AZAMPAY CHECKOUT] Response: 200 OK
```

**❌ Bad Log (old code - what you're seeing now):**
```
No X-API-Key available - authentication may fail
Response returned 200 but success=false... Invalid Vendor
```

## 🧪 Testing

1. **Make a test payment** at: `https://portal.maishaapp.co.tz/properties/bookings/10/payment/`
2. **Check server logs** for the new log message
3. **Verify payment succeeds** (or at least gets past the "Invalid Vendor" error)

## 📊 Expected Behavior After Fix

### Before Fix:
- ❌ Missing `X-API-Key` header
- ❌ AzamPay returns "Invalid Vendor" error
- ❌ Payment fails

### After Fix:
- ✅ `X-API-Key` header sent (using CLIENT_ID)
- ✅ Provider format correct (Airtel, Tigo, Mpesa - title case)
- ✅ Payment should succeed (or show a different error if vendor account issue)

## 🔍 If Still Getting Errors

If you still get "Invalid Vendor" after deploying:

1. **Check AzamPay Production Dashboard:**
   - Login: https://developers.azampay.co.tz/
   - Verify vendor account is **activated** and **approved**
   - Verify app is **verified/approved**
   - Check that providers (Airtel, Tigo, Mpesa) are **enabled** in your vendor account

2. **Check Server Logs:**
   - Look for the new log message: "Using CLIENT_ID as X-API-Key"
   - If you don't see it, the code hasn't been deployed yet
   - If you see it but still get errors, it's likely a vendor account configuration issue

3. **Run Diagnostic Script:**
   ```bash
   python check_azampay_production_config.py
   ```
   This will verify all your configurations.

## 📝 Summary

**The Fix:**
- ✅ Code updated to send `X-API-Key` header using `CLIENT_ID` when `API_KEY` not set
- ✅ Provider format fixed (uppercase → title case)
- ✅ Better error logging added

**What You Need to Do:**
1. Upload updated `payments/gateway_service.py` to server
2. Restart your Django/Gunicorn server
3. Test payment again
4. Check logs to verify fix is working

**If It Still Fails:**
- Check AzamPay production dashboard for vendor account status
- Verify providers are enabled in your vendor account
- Contact AzamPay support if vendor account is not activated
