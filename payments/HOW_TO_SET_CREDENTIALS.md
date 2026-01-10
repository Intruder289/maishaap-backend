# How to Set AZAM Pay Credentials

## Quick Answer

**Create a file named `.env` in the project root directory** (same folder as `manage.py`)

## Step-by-Step Instructions

### 1. Create the `.env` file

In the project root directory (`e:\KAZI\Maisha_backend\`), create a new file named `.env`

### 2. Add your credentials

Copy the template from `ENV_TEMPLATE.txt` and fill in your actual values:

```bash
# AZAM Pay Credentials
AZAM_PAY_CLIENT_ID=your_actual_client_id
AZAM_PAY_CLIENT_SECRET=your_actual_client_secret
AZAM_PAY_API_KEY=your_actual_api_key
AZAM_PAY_WEBHOOK_SECRET=your_actual_webhook_secret

# Optional Settings
AZAM_PAY_APP_NAME=Maisha Property Management
AZAM_PAY_SANDBOX=True
AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz
AZAM_PAY_PRODUCTION_URL=https://api.azampay.co.tz

# Base URL for webhook callbacks
BASE_URL=https://yourdomain.com
```

### 3. Install python-decouple (if not already installed)

```bash
pip install python-decouple
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 4. Restart your Django server

After creating the `.env` file, restart your server to load the new credentials.

## File Location

```
Maisha_backend/
├── manage.py
├── .env          ← CREATE THIS FILE HERE
├── requirements.txt
├── Maisha_backend/
│   └── settings.py
└── ...
```

## Important Notes

⚠️ **Never commit the `.env` file to git!** It contains sensitive credentials.

The `.env` file should be in `.gitignore` to prevent accidental commits.

## Alternative: Set Environment Variables Directly

If you prefer not to use a `.env` file, you can set environment variables directly:

### Windows (PowerShell):
```powershell
$env:AZAM_PAY_CLIENT_ID="your_client_id"
$env:AZAM_PAY_CLIENT_SECRET="your_client_secret"
$env:AZAM_PAY_API_KEY="your_api_key"
$env:AZAM_PAY_WEBHOOK_SECRET="your_webhook_secret"
```

### Windows (Command Prompt):
```cmd
set AZAM_PAY_CLIENT_ID=your_client_id
set AZAM_PAY_CLIENT_SECRET=your_client_secret
set AZAM_PAY_API_KEY=your_api_key
set AZAM_PAY_WEBHOOK_SECRET=your_webhook_secret
```

### Linux/Mac:
```bash
export AZAM_PAY_CLIENT_ID="your_client_id"
export AZAM_PAY_CLIENT_SECRET="your_client_secret"
export AZAM_PAY_API_KEY="your_api_key"
export AZAM_PAY_WEBHOOK_SECRET="your_webhook_secret"
```

## Verify It's Working

After setting up, test by checking if the credentials are loaded:

```python
python manage.py shell
```

Then in the shell:
```python
from django.conf import settings
print(settings.AZAM_PAY_CLIENT_ID)  # Should show your client ID (not empty)
```
