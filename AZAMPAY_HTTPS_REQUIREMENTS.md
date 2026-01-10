# AZAMpay HTTPS Requirements - Development & Production

## 🔒 Why HTTPS is Required

**AZAMpay webhooks require HTTPS** because:
1. **Security**: Payment callbacks must be encrypted
2. **External Access**: AZAMpay servers need to reach your webhook endpoint
3. **Production Standard**: All payment gateways require HTTPS for webhooks

## 📋 Current Situation

### ✅ What Works Locally (No HTTPS Needed)
- **Payment Initiation**: You can initiate payments from `localhost`
- **API Calls**: Your backend can call AZAMpay APIs from `localhost`
- **Testing Payment Flow**: You can test the payment creation process

### ❌ What Doesn't Work Locally (HTTPS Required)
- **Webhooks**: AZAMpay **cannot** send webhooks to `http://localhost:8081`
- **Payment Callbacks**: AZAMpay **cannot** call your local server
- **Payment Status Updates**: Automatic status updates won't work

## 🛠️ Solutions for Local Development

### Option 1: Use ngrok (Recommended for Testing)

**ngrok** creates a secure HTTPS tunnel to your localhost:

1. **Install ngrok**:
   ```bash
   # Download from https://ngrok.com/download
   # Or use: npm install -g ngrok
   ```

2. **Start your Django server**:
   ```bash
   python manage.py runserver 8081
   ```

3. **Start ngrok** (in another terminal):
   ```bash
   ngrok http 8081
   ```

4. **Get your ngrok URL**:
   ```
   Forwarding: https://abc123.ngrok.io -> http://localhost:8081
   ```

5. **Update your `.env` file**:
   ```bash
   # Use ngrok URL for webhooks during development
   AZAM_PAY_WEBHOOK_URL=https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/
   BASE_URL=https://abc123.ngrok.io
   ```

6. **Configure in AZAMpay Dashboard**:
   - Go to your app settings
   - Set webhook URL to: `https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/`
   - Save

**Note**: ngrok free tier gives you a random URL each time. For consistent testing, consider ngrok paid plan or use Option 2.

### Option 2: Use Production URL (During Development)

If you already have your production server running:

1. **Update `.env` for development**:
   ```bash
   # Use production URL for webhooks
   AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
   BASE_URL=https://portal.maishaapp.co.tz
   ```

2. **Test locally, webhooks go to production**:
   - Payment initiation: Works from localhost ✅
   - Webhook callbacks: Go to production server ✅
   - You can check production logs/database for webhook results

### Option 3: Skip Webhooks During Development

For basic testing, you can:
- Initiate payments locally ✅
- Manually verify payment status ✅
- Skip automatic webhook callbacks (test manually later)

**Update `.env`**:
```bash
# Use production URL (webhooks will work there)
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
```

## 🚀 Production Setup

### Required Configuration

Once you deploy to production with HTTPS:

1. **Update `.env` on production server**:
   ```bash
   AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
   BASE_URL=https://portal.maishaapp.co.tz
   AZAM_PAY_SANDBOX=False  # Switch to production
   AZAM_PAY_BASE_URL=https://api.azampay.co.tz  # Production API
   ```

2. **Configure in AZAMpay Dashboard**:
   - Go to production dashboard
   - Set webhook URL: `https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`
   - Save

3. **Verify HTTPS**:
   - Ensure your production server has valid SSL certificate
   - Test webhook endpoint is accessible: `curl https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/`

## 📝 Current Configuration

Looking at your `settings.py`, you currently have:

```python
# For local testing with ngrok: https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/
# For production: https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
AZAM_PAY_WEBHOOK_URL = config('AZAM_PAY_WEBHOOK_URL', default='https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/')
```

**This is already configured for production!** ✅

## ✅ Recommended Approach

### For Local Development:
1. **Use ngrok** when you need to test webhooks
2. **OR** use production URL (webhooks go to production, you test locally)
3. **OR** skip webhooks and test payment initiation only

### For Production:
1. **Already configured** ✅
2. **Just ensure** your production server has HTTPS
3. **Update AZAMpay dashboard** with production webhook URL

## 🎯 Summary

**Do you need HTTPS for local development?**

- **For payment initiation**: ❌ No - works with localhost
- **For webhook callbacks**: ✅ Yes - AZAMpay needs HTTPS to call you
- **For production**: ✅ Yes - Required

**Best Practice**:
- **Development**: Use ngrok OR point webhooks to production
- **Production**: Use your actual HTTPS domain (already configured)

---

**Your current setup is correct!** The webhook URL is already set to production. During local development:
- You can test payment initiation ✅
- Webhooks will go to production (which is fine) ✅
- When you deploy, everything will work ✅
