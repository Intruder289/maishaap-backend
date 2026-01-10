# AZAMpay 404 Error Troubleshooting Guide

## Error Message
```
Failed to initiate payment: Failed to authenticate with AZAM Pay: 404 Client Error: Not Found for url: https://sandbox.azampay.co.tz/api/v1/Token/GetToken
```

## What This Error Means

A **404 Not Found** error means the API endpoint URL doesn't exist on the AZAMpay server. This is **NOT** an authentication failure (which would be 401) or a network issue.

## Common Causes

### 1. **Incorrect Endpoint Path** ⚠️ MOST LIKELY
The endpoint `/api/v1/Token/GetToken` might not be the correct path for AZAMpay's API. The code has been updated to try multiple endpoint variations automatically.

### 2. **App Name Mismatch**
Your `AZAM_PAY_APP_NAME` in `.env` must **exactly match** the "App Name" in your AZAMpay dashboard.

**From your screenshot:**
- Dashboard App Name: `mishap`
- Make sure your `.env` has: `AZAM_PAY_APP_NAME=mishap`

### 3. **Missing or Incorrect Credentials**
Verify all credentials in your `.env` file match the dashboard:

```env
AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9
AZAM_PAY_CLIENT_SECRET=your_client_secret_here
AZAM_PAY_APP_NAME=mishap  # ⚠️ Must match dashboard exactly
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
```

### 4. **API Key Configuration**
- If you have an API Key in the dashboard, add it: `AZAM_PAY_API_KEY=your_api_key`
- If not provided, the code will use Client ID as fallback (for sandbox)

## Solutions

### Solution 1: Verify App Name ✅ **DO THIS FIRST**

1. Check your AZAMpay dashboard App Name (from screenshot: `mishap`)
2. Update your `.env` file:
   ```env
   AZAM_PAY_APP_NAME=mishap
   ```
3. Restart your Django server
4. Try again

### Solution 2: Check AZAMpay API Documentation

1. Visit: https://developerdocs.azampay.co.tz/redoc
2. Look for the **authentication/token endpoint**
3. Verify the exact endpoint path
4. If different, we may need to update the code

### Solution 3: Test Endpoint Directly

The updated code now tries multiple endpoint variations:
- `/api/v1/token` (tried first)
- `/api/v1/Token/GetToken`
- `/api/v1/token/get-token`
- `/api/v1/oauth/token`
- `/api/v1/auth/token`
- And more...

Check your server logs to see which endpoints were tried and what responses were received.

### Solution 4: Contact AZAMpay Support

If none of the above work:
1. Contact AZAMpay support with:
   - Your App Name: `mishap`
   - Your Client ID: `43a4545a-e1c3-479e-a07e-9bb7c9`
   - The error you're getting
   - Ask for the correct token endpoint URL

## Verification Steps

1. **Check .env file:**
   ```bash
   # Make sure these are set correctly
   AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9
   AZAM_PAY_CLIENT_SECRET=your_secret_here
   AZAM_PAY_APP_NAME=mishap  # ⚠️ Critical: Must match dashboard
   AZAM_PAY_SANDBOX=True
   AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
   ```

2. **Check Django settings:**
   ```python
   # In Django shell: python manage.py shell
   from django.conf import settings
   print("Client ID:", settings.AZAM_PAY_CLIENT_ID)
   print("App Name:", settings.AZAM_PAY_APP_NAME)
   print("Sandbox:", settings.AZAM_PAY_SANDBOX)
   print("Base URL:", settings.AZAM_PAY_BASE_URL)
   ```

3. **Check server logs:**
   - Look for lines starting with "Trying AZAM Pay token endpoint:"
   - See which endpoints were tried
   - Check the response codes

## Important Notes

- **The "Token" field in your dashboard** (5e25d8db-0449-4a94-ba7e-7f09be) is a **temporary token** that expires. You don't need to save this - the code automatically fetches new tokens.

- **Local vs Hosted:** The 404 error is **NOT** because your app is local. The error is happening when your server tries to connect to AZAMpay's API, which should work from anywhere with internet access.

- **Callback URL:** The callback URL in your dashboard (`https://portal.maishaapp.co.tz/api/v1/payn`) is for webhooks coming **FROM** AZAMpay **TO** your server. It doesn't affect the token endpoint.

## Next Steps

1. ✅ Update `AZAM_PAY_APP_NAME=mishap` in `.env`
2. ✅ Restart Django server
3. ✅ Try making a payment again
4. ✅ Check server logs for detailed endpoint attempts
5. ✅ If still failing, check AZAMpay API documentation or contact support

## Updated Code Features

The code has been updated to:
- ✅ Try multiple endpoint variations automatically
- ✅ Validate credentials before attempting
- ✅ Provide detailed error messages
- ✅ Log all endpoint attempts for debugging

Check your server logs to see which endpoints are being tried and their responses.
