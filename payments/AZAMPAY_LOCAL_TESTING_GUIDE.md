# AZAMpay Local Testing Guide

## Can You Test AZAMpay Integration Locally?

**YES! You can test AZAMpay integration locally**, but there are some important considerations:

## What Works Locally ✅

### 1. **Payment Initiation (Token Request)**
- ✅ Your Django server can run on `localhost` (e.g., `http://localhost:8081`)
- ✅ You can initiate payments and request tokens from AZAMpay's API
- ✅ You need **internet connection** to reach AZAMpay's servers (`sandbox.azampay.co.tz`)
- ✅ This works from your local machine

### 2. **Payment Processing**
- ✅ Users can complete payments on AZAMpay's website
- ✅ Payment links work from anywhere (they redirect to AZAMpay's servers)

## What Requires Public Access ⚠️

### 1. **Webhook Callbacks** (Optional for Initial Testing)
- ⚠️ AZAMpay needs to send webhook notifications **TO** your server
- ⚠️ Your server must be **publicly accessible** for webhooks to work
- ✅ **BUT**: You can test payment initiation without webhooks first!

## Testing Options

### Option 1: Test Payment Initiation Only (No Webhooks) ✅ **EASIEST**

**What you can test:**
- ✅ Token authentication
- ✅ Payment link generation
- ✅ Redirecting users to AZAMpay

**What you can't test:**
- ❌ Automatic payment status updates via webhooks
- ✅ But you can manually verify payments in AZAMpay dashboard

**Steps:**
1. Run your Django server locally: `python manage.py runserver`
2. Make sure you have internet connection
3. Try initiating a payment
4. Check if you get a payment link
5. You can complete the payment on AZAMpay's website
6. Manually check payment status in AZAMpay dashboard

### Option 2: Full Testing with Webhooks (Requires Public URL)

**For webhooks to work, you need:**

1. **Use ngrok** (Recommended for local testing):
   ```bash
   # Install ngrok: https://ngrok.com/
   ngrok http 8081
   # This gives you a public URL like: https://abc123.ngrok.io
   ```

2. **Update your AZAMpay dashboard:**
   - Set Callback URL to: `https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/`
   - Update `.env`: `BASE_URL=https://abc123.ngrok.io`

3. **Now webhooks will work!**

### Option 3: Deploy to a Test Server

- Deploy to a staging server (e.g., Heroku, DigitalOcean, AWS)
- Use that URL for webhook callbacks
- Test everything end-to-end

## Current Error Analysis

Based on your logs, you're getting **404 errors** from AZAMpay's API. This means:

✅ **Your internet connection is working** (you're reaching AZAMpay's servers)
✅ **Your Django server is fine** (it's making the requests)
❌ **The API endpoint path is incorrect** (404 = endpoint doesn't exist)

**This is NOT because you're running locally!** The 404 error happens when your code tries to connect to AZAMpay's API, which works from anywhere with internet.

## What You Need

### For Local Testing (What You Have):
- ✅ Django server running locally
- ✅ Internet connection ✅ (You have this - you're getting 404s, not connection errors)
- ✅ AZAMpay credentials in `.env` ✅ (You have this)

### For Webhook Testing (Optional):
- ⚠️ Public URL (use ngrok or deploy to staging)

## Summary

**You CAN test AZAMpay integration locally!**

The current 404 errors are because:
1. The API endpoint path might be wrong
2. OR the request format doesn't match what AZAMpay expects

**This is NOT because you're running locally.** If it were a local/hosted issue, you'd get:
- Connection errors (can't reach AZAMpay servers)
- Timeout errors
- NOT 404 errors (which means you're successfully connecting, but the endpoint doesn't exist)

## Next Steps

1. ✅ Fix the syntax error (done!)
2. ✅ Restart your Django server
3. ✅ Try making a payment again
4. ✅ Check the detailed logs to see which endpoint/payload combination works
5. ⚠️ If you want webhook testing, set up ngrok or deploy to staging

## Quick Test Checklist

- [ ] Django server running locally
- [ ] Internet connection active
- [ ] AZAMpay credentials in `.env` file
- [ ] `AZAM_PAY_APP_NAME=mishap` in `.env`
- [ ] Try initiating a payment
- [ ] Check logs for detailed endpoint attempts

The 404 errors will be resolved once we find the correct endpoint path from AZAMpay's API documentation!
