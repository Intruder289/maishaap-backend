# 🔧 Troubleshooting: AZAM_PAY_CLIENT_ID Not Set on Server

## Error Message
```
Failed to initiate payment: AZAM_PAY_CLIENT_ID is not set in settings. Please add it to your .env file.
```

## What This Means
The Django application on your server cannot read the `AZAM_PAY_CLIENT_ID` from your `.env` file. This is usually a file location or permissions issue.

---

## 🔍 Step-by-Step Diagnosis

### Step 1: Run Diagnostic Script

**On your hosted server, run:**

```bash
cd /path/to/Maisha_backend
python check_server_env.py
```

This will tell you:
- ✅ If `.env` file exists
- ✅ If `.env` file is in the correct location
- ✅ If python-decouple can read it
- ✅ What Django settings sees

---

### Step 2: Verify .env File Location

**The `.env` file MUST be in the project root directory:**

```
Maisha_backend/
├── .env                    ← MUST BE HERE (same level as manage.py)
├── manage.py
├── Maisha_backend/
│   └── settings.py
├── payments/
└── ...
```

**Check on your server:**
```bash
cd /path/to/Maisha_backend
ls -la .env
```

**Expected output:**
```
-rw-r--r-- 1 user user 1234 date .env
```

If you see "No such file or directory", the `.env` file is missing or in the wrong location.

---

### Step 3: Verify .env File Content

**Check that AZAM_PAY_CLIENT_ID is in the file:**
```bash
grep AZAM_PAY_CLIENT_ID .env
```

**Expected output:**
```
AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9f289d1
```

If nothing is returned, the variable is missing from `.env`.

---

### Step 4: Check File Permissions

**The `.env` file must be readable:**
```bash
chmod 644 .env
```

**Verify:**
```bash
ls -la .env
```

Should show: `-rw-r--r--`

---

## ✅ Solutions

### Solution 1: Upload .env File to Server

**If `.env` file is missing:**

1. **From your local machine, upload `.env` to server:**
   ```bash
   # Using SCP
   scp .env user@your-server:/path/to/Maisha_backend/.env
   
   # Or using SFTP/FTP client
   # Upload .env to /path/to/Maisha_backend/
   ```

2. **Set correct permissions:**
   ```bash
   chmod 644 .env
   ```

3. **Verify it's there:**
   ```bash
   ls -la .env
   cat .env | grep AZAM_PAY_CLIENT_ID
   ```

---

### Solution 2: Create .env File on Server

**If `.env` doesn't exist, create it:**

```bash
cd /path/to/Maisha_backend
nano .env
```

**Add these lines (update with your actual values):**
```bash
# AZAM Pay Credentials
AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9f289d1
AZAM_PAY_CLIENT_SECRET=your_sandbox_secret_here
AZAM_PAY_APP_NAME=mishap

# AZAM Pay Settings
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# Base URL
BASE_URL=https://portal.maishaapp.co.tz
AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/

# Database
DATABASE_NAME=maisha
DATABASE_USER=postgres
DATABASE_PASSWORD=your_server_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django Settings
DEBUG=False
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=portal.maishaapp.co.tz,www.portal.maishaapp.co.tz
```

**Save and set permissions:**
```bash
chmod 644 .env
```

---

### Solution 3: Check Working Directory

**The web server might be running from a different directory.**

**For Gunicorn, check your service file:**
```bash
sudo systemctl cat gunicorn
# or
cat /etc/systemd/system/gunicorn.service
```

**Look for `WorkingDirectory` - it should be:**
```ini
WorkingDirectory=/path/to/Maisha_backend
```

**If wrong, update it:**
```bash
sudo systemctl edit gunicorn
```

**Add:**
```ini
[Service]
WorkingDirectory=/path/to/Maisha_backend
```

**Then restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

---

### Solution 4: Restart Web Server

**After creating/updating `.env` file, ALWAYS restart your web server:**

```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For uWSGI
sudo systemctl restart uwsgi

# For Apache
sudo systemctl restart apache2

# For Nginx (if needed)
sudo systemctl restart nginx
```

**Why?** The web server loads environment variables when it starts. Changes to `.env` won't take effect until restart.

---

### Solution 5: Verify python-decouple is Installed

**Check if python-decouple is installed:**
```bash
pip list | grep decouple
```

**If not installed:**
```bash
pip install python-decouple
```

**Or if using virtual environment:**
```bash
source venv/bin/activate
pip install python-decouple
```

---

## 🧪 Test After Fixing

**1. Run diagnostic script:**
```bash
python check_server_env.py
```

**2. Test Django can read the variable:**
```bash
python manage.py shell
```

**In Django shell:**
```python
from django.conf import settings
print(settings.AZAM_PAY_CLIENT_ID)
```

**Expected:** Should print your Client ID (not empty string)

**3. Try making a payment again**

---

## 📋 Quick Checklist

- [ ] `.env` file exists in project root (same directory as `manage.py`)
- [ ] `.env` file has `AZAM_PAY_CLIENT_ID=your_client_id`
- [ ] `.env` file is readable: `chmod 644 .env`
- [ ] Web server working directory is correct
- [ ] Web server restarted after `.env` changes
- [ ] `python-decouple` is installed
- [ ] Django can read the variable (test with shell)

---

## 🆘 Still Not Working?

**If after all these steps it still doesn't work:**

1. **Check server logs:**
   ```bash
   tail -f /var/log/gunicorn/error.log
   # or
   journalctl -u gunicorn -f
   ```

2. **Check Django logs:**
   ```bash
   tail -f /path/to/Maisha_backend/logs/django.log
   ```

3. **Try setting environment variable directly (temporary test):**
   ```bash
   export AZAM_PAY_CLIENT_ID=43a4545a-e1c3-479e-a07e-9bb7c9f289d1
   # Then restart server
   ```
   
   If this works, the issue is definitely with `.env` file location/reading.

4. **Check if multiple .env files exist:**
   ```bash
   find /path/to/Maisha_backend -name ".env" -type f
   ```
   
   Make sure there's only one, and it's in the project root.

---

## ✅ Success Indicators

**You'll know it's fixed when:**
- ✅ `python check_server_env.py` shows variables are set
- ✅ Django shell can read `settings.AZAM_PAY_CLIENT_ID`
- ✅ Payment initiation works without the error
- ✅ No more "AZAM_PAY_CLIENT_ID is not set" error

---

**Most Common Issue:** `.env` file not uploaded to server or in wrong location! 📁
