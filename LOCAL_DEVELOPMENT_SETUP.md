# Local Development Setup Guide - AZAMpay Integration

## 📋 Your Current Configuration

Based on your `settings.py`:

```python
# Base URL for webhook callbacks
BASE_URL = config('BASE_URL', default='http://localhost:8000')

# AZAMpay Webhook URL (optional - overrides BASE_URL for webhooks)
AZAM_PAY_WEBHOOK_URL = config('AZAM_PAY_WEBHOOK_URL', default='https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/')
```

**Current Status**: ✅ **Already configured correctly!**

## 🎯 What This Means

### ✅ What Works Locally (Right Now)

1. **Payment Initiation**: 
   - You can initiate payments from `http://localhost:8081`
   - Your backend calls AZAMpay API ✅
   - Payment requests are created ✅

2. **Testing Payment Flow**:
   - Create payment records locally ✅
   - Test payment forms ✅
   - Test payment API endpoints ✅

### ⚠️ What Happens with Webhooks

**Current Behavior**:
- When AZAMpay processes a payment, it will call: `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- This goes to your **production server**, not localhost
- This is **perfectly fine** for development! ✅

**Why This Works**:
- Your production server is already running
- Webhooks will update payment status on production
- You can check production database/logs to see webhook results
- When you deploy your new code, webhooks will work automatically

## 📝 What You Need to Do

### For Local Development (Current Setup)

**Nothing! Your setup is already correct.** ✅

Just ensure your `.env` file has:

```bash
# Webhook URL - points to production (this is fine!)
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# Other AZAMpay settings
AZAM_PAY_CLIENT_ID=your_client_id
AZAM_PAY_CLIENT_SECRET=your_client_secret
AZAM_PAY_APP_NAME=mishap
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
```

### Development Workflow

1. **Develop locally** on `http://localhost:8081`
2. **Test payment initiation** - works locally ✅
3. **Webhooks go to production** - this is fine ✅
4. **Check production** for webhook results (if needed)
5. **Deploy your code** when ready
6. **Everything works** automatically on production ✅

## 🔄 Alternative: Test Webhooks Locally (Optional)

If you want to test webhooks on your local machine, use **ngrok**:

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com/download
# Or: npm install -g ngrok
```

### Step 2: Start ngrok
```bash
# In a separate terminal
ngrok http 8081
```

### Step 3: Get ngrok URL
You'll see something like:
```
Forwarding: https://abc123.ngrok.io -> http://localhost:8081
```

### Step 4: Update `.env` temporarily
```bash
# For local webhook testing only
AZAM_PAY_WEBHOOK_URL=https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/
```

### Step 5: Update AZAMpay Dashboard
- Go to sandbox dashboard
- Set webhook URL to: `https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/`
- Save

**Note**: ngrok free tier gives you a new URL each time. For consistent testing, you'd need ngrok paid plan.

### Step 6: Revert After Testing
```bash
# Change back to production URL
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
```

## 🚀 Production Deployment

When you deploy your code to production:

1. **No changes needed** - webhook URL is already correct ✅
2. **Ensure production server is running** ✅
3. **Verify webhook endpoint is accessible**:
   ```bash
   curl https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
   ```
4. **Check AZAMpay dashboard** - ensure webhook URL is set correctly

## ✅ Summary

### Your Current Setup:
- ✅ Webhook URL points to production: `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
- ✅ This is **perfect for development**!
- ✅ You can develop and test locally
- ✅ Webhooks will work on production
- ✅ When you deploy, everything works automatically

### What You Can Do Locally:
- ✅ Test payment initiation
- ✅ Test payment forms
- ✅ Test API endpoints
- ✅ Develop new features
- ⚠️ Webhooks go to production (which is fine!)

### What You Need:
- ✅ Just keep your `.env` file with `AZAM_PAY_WEBHOOK_URL` pointing to production
- ✅ That's it! No other changes needed

## 🎯 Recommendation

**Keep your current setup!** It's perfect for development:
- You can test everything locally
- Webhooks work on production
- No need for ngrok or HTTPS on localhost
- Simple and straightforward

**Only use ngrok if**:
- You specifically need to test webhook handling locally
- You're debugging webhook issues
- You want to see webhook requests in real-time on localhost

---

**Bottom Line**: Your configuration is already correct. Just develop locally, test payment initiation, and webhooks will work on production. When you deploy, everything will work automatically! ✅
