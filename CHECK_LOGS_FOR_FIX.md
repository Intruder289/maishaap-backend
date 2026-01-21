# How to Verify the Fix is Working

## 🔍 What to Look For in Server Logs

After deploying the fix and restarting the server, when you make a payment, you should see these log messages:

### ✅ GOOD LOGS (Fix is Working):

```
Using CLIENT_ID as X-API-Key (API_KEY not set): 019bb775-c4be-7171-9...
[AZAMPAY] Calling checkout endpoint: https://checkout.azampay.co.tz/azampay/mno/checkout
[AZAMPAY] Headers: Authorization=Bearer ***, X-API-Key=***
[AZAMPAY] Payload: {
  "accountNumber": "2557XXXXXXXX",
  "amount": 2000,
  "currency": "TZS",
  "externalId": "BOOKING-XXX-1234567890",
  "provider": "Airtel"
}
[AZAMPAY] Response: 200 OK
```

**Key indicators:**
- ✅ "Using CLIENT_ID as X-API-Key" message appears
- ✅ "X-API-Key=***" (not "X-API-Key=none")
- ✅ Provider is in title case: "Airtel", "Tigo", "Mpesa" (not "AIRTEL", "TIGO")

### ❌ BAD LOGS (Fix Not Working / Old Code):

```
No X-API-Key available - authentication may fail
[AZAMPAY] Headers: Authorization=Bearer ***, X-API-Key=none
Response returned 200 but success=false... Invalid Vendor
```

**Key indicators:**
- ❌ "No X-API-Key available" message
- ❌ "X-API-Key=none" (header not being sent)
- ❌ Still getting "Invalid Vendor" error

## 📋 Steps to Check

### Step 1: Verify Code is Deployed

On your server, check if the updated code is there:

```bash
# SSH into your server
ssh your-server

# Check the file has the fix
grep -A 5 "Using CLIENT_ID as X-API-Key" /path/to/your/project/payments/gateway_service.py
```

You should see:
```python
headers["X-API-Key"] = client_id_value
logger.info(f"Using CLIENT_ID as X-API-Key (API_KEY not set): {client_id_value[:20]}...")
```

### Step 2: Verify Server Was Restarted

Check when your server was last restarted:

```bash
# Check gunicorn process start time
ps aux | grep gunicorn

# Or check systemd service status
sudo systemctl status gunicorn
```

**Important:** The server MUST be restarted after uploading the file, or it will still run the old code!

### Step 3: Check Full Logs During Payment

When making a payment, check the FULL log output around that time:

```bash
# View recent logs (adjust path as needed)
tail -f /var/log/gunicorn/error.log
# or
journalctl -u gunicorn -f
# or wherever your Django logs are
```

Look for:
1. The "Using CLIENT_ID as X-API-Key" message
2. The "[AZAMPAY] Headers" line showing X-API-Key
3. The "[AZAMPAY] Payload" showing provider format

### Step 4: If X-API-Key IS Being Sent But Still Getting Error

If logs show "X-API-Key=***" but you still get "Invalid Vendor", then it's likely a **vendor account configuration issue** in AzamPay dashboard:

1. **Login to AzamPay Production Dashboard:**
   - https://developers.azampay.co.tz/

2. **Check Vendor Account Status:**
   - Go to your vendor/merchant account settings
   - Verify account is **ACTIVATED** and **APPROVED**
   - Check account status is not "Pending" or "Suspended"

3. **Check Provider Configuration:**
   - Verify providers (Airtel, Tigo, Mpesa) are **ENABLED** for your vendor account
   - Some vendors need to enable each provider separately

4. **Check App Configuration:**
   - Verify your app is **VERIFIED/APPROVED**
   - Check that CLIENT_ID matches the app in dashboard

5. **Contact AzamPay Support:**
   - If account appears active but still getting "Invalid Vendor"
   - They may need to enable providers or activate your vendor account

## 🚨 Common Issues

### Issue 1: Code Not Deployed
**Symptom:** Logs show "No X-API-Key available"
**Fix:** Upload `payments/gateway_service.py` to server and restart

### Issue 2: Server Not Restarted
**Symptom:** Code is updated but logs still show old messages
**Fix:** Restart gunicorn/Django server

### Issue 3: Python Cache (.pyc files)
**Symptom:** Code updated, server restarted, but still old behavior
**Fix:** Clear Python cache:
```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -name "*.pyc" -delete
# Then restart server
```

### Issue 4: Vendor Account Not Activated
**Symptom:** X-API-Key is sent, but still "Invalid Vendor"
**Fix:** Check AzamPay dashboard - vendor account needs to be activated/approved

## 📞 Next Steps

1. **Check your server logs** for the messages above
2. **Share the log output** around the payment attempt time
3. **Verify** the code is deployed and server is restarted
4. **Check AzamPay dashboard** for vendor account status
