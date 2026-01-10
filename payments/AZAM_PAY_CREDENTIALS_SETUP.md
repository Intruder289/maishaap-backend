# AZAM Pay Credentials Setup Guide

## After Registering Your App

Once you've registered your app at https://developers.azampay.co.tz/sandbox/registerapp, follow these steps to get your credentials:

## Step 1: Log in to AZAM Pay Dashboard

- **Sandbox Dashboard:** https://sandbox.azampay.co.tz/
- **Production Dashboard:** https://developers.azampay.co.tz/

## Step 2: Find Your App Credentials

1. **Navigate to "My Apps" or "Applications"** in the dashboard
2. **Click on your registered app** to view details

You should see these fields:
- ✅ **Client ID** - Copy this value → Use for `AZAM_PAY_CLIENT_ID`
- ✅ **Client Secret Key** - Copy this value → Use for `AZAM_PAY_CLIENT_SECRET`
  - ⚠️ **WARNING:** Usually shown only once! Save it securely!
- ⚠️ **Token** - This is a temporary access token (expires). You don't need to save this.

**Good News for Sandbox Mode:**
- ✅ You **only need Client ID and Client Secret** for sandbox testing
- ✅ The code automatically uses Client ID as API Key if `AZAM_PAY_API_KEY` is not set
- ✅ The code automatically uses Client Secret as Webhook Secret if `AZAM_PAY_WEBHOOK_SECRET` is not set
- ✅ No need to find separate API Key or Webhook Secret fields!

## Step 3: Configure Webhook URL (Optional for Sandbox)

1. **In the Callback URL section** (visible in your dashboard):
   - **Add your webhook URL:**
     ```
     https://yourdomain.com/api/v1/payments/webhook/azam-pay/
     ```
     Replace `yourdomain.com` with your actual domain (or use ngrok for local testing)
   - Click **"Update"** button

2. **Note:** For sandbox mode, you don't need a separate webhook secret. The code will automatically use your Client Secret for webhook verification.

## Step 4: Add Credentials to Your Environment

Create or update your `.env` file in the project root:

```bash
# AZAM Pay Credentials (from dashboard) - Minimum Required for Sandbox
AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9  # From "Client ID" field
AZAM_PAY_CLIENT_SECRET=S8E4EnDja5VC7MYNnDvNAODfvFIC9r  # From "Client Secret Key" field

# Optional - Code will auto-use Client ID/Secret if not provided (sandbox only)
# AZAM_PAY_API_KEY=43a4545a-e1c3-479e-a07e-9bb7c9  # Optional in sandbox
# AZAM_PAY_WEBHOOK_SECRET=your_webhook_secret_here  # Optional in sandbox

# Optional Settings
AZAM_PAY_APP_NAME=Maisha Property Management
AZAM_PAY_SANDBOX=True  # Set to False for production
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# Base URL for webhook callbacks (update with your domain)
BASE_URL=https://yourdomain.com
```

## Step 5: Verify Your Setup

After adding the credentials:

1. **Restart your Django server** to load the new environment variables
2. **Test the connection** by initiating a test payment
3. **Check the logs** for any authentication errors

## Common Issues

### Can't Find Credentials?
- Check your registration confirmation email
- Look in "Settings" → "API Settings" or "Developer Tools"
- Contact AZAM Pay support: support@azampay.com

### Webhook Secret Not Visible?
- Some dashboards only show it once during generation
- Check if there's a "Regenerate" or "Show" button
- You may need to save the webhook URL first before the secret appears

### Testing Locally?
- Use **ngrok** or similar tool to expose your local server:
  ```bash
  ngrok http 8000
  ```
- Use the ngrok URL as your `BASE_URL`:
  ```bash
  BASE_URL=https://abc123.ngrok.io
  ```
- Update the webhook URL in AZAM Pay dashboard to:
  ```
  https://abc123.ngrok.io/api/v1/payments/webhook/azam-pay/
  ```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit your `.env` file to version control
- Keep your Client Secret and Webhook Secret secure
- Rotate credentials if they are ever exposed
- Use different credentials for sandbox and production

## Next Steps

1. ✅ Get all credentials from dashboard
2. ✅ Add to `.env` file
3. ✅ Configure webhook URL in AZAM Pay dashboard
4. ✅ Test payment flow in sandbox
5. ✅ Request production credentials when ready

## Support

- **AZAM Pay Documentation:** https://developerdocs.azampay.co.tz/redoc
- **AZAM Pay Support:** support@azampay.com
- **Dashboard:** https://sandbox.azampay.co.tz/
