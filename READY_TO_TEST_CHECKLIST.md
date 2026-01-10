# Ready to Test Checklist

## ✅ What's Already Done

- [x] ngrok is running: `https://unperceivably-brutalitarian-krystyna.ngrok-free.dev`
- [x] Sandbox mode enabled
- [x] AzamPay credentials configured
- [x] Webhook signature validation removed
- [x] Webhook handler code ready

## ⚠️ What You Need to Do (2 Steps)

### Step 1: Update .env File (REQUIRED)

**Open:** `d:\KAZI\Maisha_backend\.env`

**Find this line:**
```bash
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/
```

**Change it to:**
```bash
AZAM_PAY_WEBHOOK_URL=https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/
```

**Also update:**
```bash
BASE_URL=https://unperceivably-brutalitarian-krystyna.ngrok-free.dev
```

**Save the file!**

---

### Step 2: Restart Django Server (REQUIRED)

1. **Stop Django** (if running): Press `Ctrl+C`
2. **Restart:**
   ```bash
   python manage.py runserver 8081
   ```

---

### Step 3: Configure AzamPay Dashboard (REQUIRED)

1. **Log into AzamPay Sandbox Dashboard**
2. **Go to:** Settings → Webhooks (or App Settings → Webhooks)
3. **Add webhook URL:**
   ```
   https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/
   ```
4. **Save**

---

## ✅ After Completing Steps 1-3

**Verify setup:**
```bash
python test_local_azampay_setup.py
```

**You should see:**
```
[OK] Webhook URL configured
```

---

## 🧪 Then You Can Test!

### Quick Test Steps:

1. **Open your app:** `http://localhost:8081`
2. **Create a payment** (through booking, rent invoice, etc.)
3. **Select "Online Payment (AZAM Pay)"**
4. **Complete payment on AzamPay**
5. **Watch Django logs** for webhook receipt
6. **Verify payment status** updates to "completed"

---

## 📊 What to Watch For

### In Django Logs (Terminal):
```
[INFO] AzamPay webhook received
[INFO] Headers: {...}
[INFO] Webhook payload: {...}
[INFO] Found payment by transaction ID: {id}
```

### In ngrok Dashboard (`http://localhost:4040`):
- You'll see the webhook request appear
- Status should be 200 OK

### Payment Status:
- Should change from `pending` → `completed`
- Payment date should be set
- Related records (RentInvoice/Booking) should update

---

## 🚨 Current Status

**Not quite ready yet** - You need to:
1. ✅ Update .env file (2 minutes)
2. ✅ Restart Django server (30 seconds)
3. ✅ Configure webhook in AzamPay dashboard (2 minutes)

**Total time:** ~5 minutes

**After that:** ✅ Ready to test!

---

**Your ngrok URL:** `https://unperceivably-brutalitarian-krystyna.ngrok-free.dev`  
**Webhook URL to use:** `https://unperceivably-brutalitarian-krystyna.ngrok-free.dev/api/v1/payments/webhook/azam-pay/`
