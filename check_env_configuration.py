#!/usr/bin/env python
"""
Script to check current .env configuration for AzamPay
Run this to see what values are currently set in your .env file
"""

import os
from pathlib import Path

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'

print("=" * 60)
print("Current .env Configuration Check")
print("=" * 60)
print()

if not ENV_FILE.exists():
    print("❌ ERROR: .env file not found!")
    print(f"   Expected location: {ENV_FILE}")
    print()
    print("   Please ensure .env file exists in the project root.")
    exit(1)

# Read .env file
env_vars = {}
with open(ENV_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        # Parse KEY=VALUE
        if '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()

# Check critical AzamPay settings
print("🔍 Checking AzamPay Configuration:")
print("-" * 60)

# Critical settings to check
critical_settings = {
    'AZAM_PAY_SANDBOX': {
        'required': True,
        'expected_sandbox': 'True',
        'expected_production': 'False',
        'description': 'Sandbox mode (True for testing, False for production)'
    },
    'BASE_URL': {
        'required': True,
        'description': 'Base URL of your application'
    },
    'AZAM_PAY_WEBHOOK_URL': {
        'required': True,
        'description': 'Webhook URL for AzamPay callbacks'
    },
    'AZAM_PAY_BASE_URL': {
        'required': True,
        'expected_sandbox': 'https://sandbox.azampay.co.tz',
        'expected_production': 'https://api.azampay.co.tz',
        'description': 'AzamPay API base URL'
    },
    'AZAM_PAY_CLIENT_ID': {
        'required': True,
        'description': 'AzamPay Client ID'
    },
    'AZAM_PAY_CLIENT_SECRET': {
        'required': True,
        'description': 'AzamPay Client Secret'
    },
    'AZAM_PAY_API_KEY': {
        'required': True,
        'description': 'AzamPay API Key'
    },
}

# Check each setting
all_good = True
for key, config in critical_settings.items():
    value = env_vars.get(key, 'NOT SET')
    required = config.get('required', False)
    
    # Check if set
    if value == 'NOT SET':
        if required:
            print(f"❌ {key}: NOT SET (REQUIRED)")
            all_good = False
        else:
            print(f"⚠️  {key}: NOT SET (optional)")
    else:
        # Check if value matches expected for sandbox
        expected_sandbox = config.get('expected_sandbox')
        expected_production = config.get('expected_production')
        
        if expected_sandbox and value == expected_sandbox:
            print(f"✅ {key}: {value} (Sandbox mode)")
        elif expected_production and value == expected_production:
            print(f"✅ {key}: {value} (Production mode)")
        elif 'sandbox' in value.lower() or 'sandbox' in key.lower():
            print(f"✅ {key}: {value} (Looks like sandbox)")
        elif 'portal.maishaapp.co.tz' in value or 'localhost' in value or 'ngrok' in value:
            print(f"✅ {key}: {value}")
        else:
            print(f"✅ {key}: {value}")
    
    # Show description
    desc = config.get('description', '')
    if desc:
        print(f"   └─ {desc}")

print()
print("-" * 60)
print("📋 Configuration Summary:")
print("-" * 60)

# Determine mode
sandbox_mode = env_vars.get('AZAM_PAY_SANDBOX', '').lower() == 'true'
base_url = env_vars.get('BASE_URL', 'NOT SET')
webhook_url = env_vars.get('AZAM_PAY_WEBHOOK_URL', 'NOT SET')

print(f"Mode: {'🔵 SANDBOX (Testing)' if sandbox_mode else '🟢 PRODUCTION (Live)'}")
print(f"Base URL: {base_url}")
print(f"Webhook URL: {webhook_url}")
print()

# Check for common issues
print("🔍 Checking for Common Issues:")
print("-" * 60)

issues_found = []

# Check if BASE_URL matches webhook URL domain
if base_url != 'NOT SET' and webhook_url != 'NOT SET':
    if 'localhost' in base_url and 'ngrok' not in webhook_url and 'portal.maishaapp.co.tz' not in webhook_url:
        issues_found.append("⚠️  BASE_URL is localhost but webhook URL is not ngrok/localhost")
    elif 'ngrok' in base_url and 'ngrok' not in webhook_url:
        issues_found.append("⚠️  BASE_URL is ngrok but webhook URL doesn't match")
    elif 'portal.maishaapp.co.tz' in base_url and 'portal.maishaapp.co.tz' not in webhook_url:
        issues_found.append("⚠️  BASE_URL is production but webhook URL doesn't match")

# Check sandbox mode consistency
if sandbox_mode:
    if 'sandbox.azampay.co.tz' not in env_vars.get('AZAM_PAY_BASE_URL', ''):
        issues_found.append("⚠️  AZAM_PAY_SANDBOX=True but AZAM_PAY_BASE_URL is not sandbox URL")
else:
    if 'api.azampay.co.tz' not in env_vars.get('AZAM_PAY_BASE_URL', ''):
        issues_found.append("⚠️  AZAM_PAY_SANDBOX=False but AZAM_PAY_BASE_URL is not production URL")

# Check webhook URL format
if webhook_url != 'NOT SET':
    if not webhook_url.startswith('https://'):
        issues_found.append("❌ Webhook URL must use HTTPS (not HTTP)")
    if not webhook_url.endswith('/api/v1/payments/webhook/azam-pay/'):
        issues_found.append("⚠️  Webhook URL should end with /api/v1/payments/webhook/azam-pay/")

if issues_found:
    for issue in issues_found:
        print(issue)
else:
    print("✅ No issues found!")

print()
print("-" * 60)
print("📝 Recommendations for Hosted Server:")
print("-" * 60)

if sandbox_mode:
    print("✅ You're in SANDBOX mode - Good for testing!")
    print()
    print("For hosted server sandbox testing, ensure:")
    print("  • BASE_URL=https://your-hosted-domain.com")
    print("  • AZAM_PAY_WEBHOOK_URL=https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/")
    print("  • AZAM_PAY_SANDBOX=True")
    print("  • AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz")
else:
    print("⚠️  You're in PRODUCTION mode!")
    print()
    print("For production, ensure:")
    print("  • BASE_URL=https://portal.maishaapp.co.tz")
    print("  • AZAM_PAY_WEBHOOK_URL=https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/")
    print("  • AZAM_PAY_SANDBOX=False")
    print("  • AZAM_PAY_BASE_URL=https://api.azampay.co.tz")

print()
print("=" * 60)
if all_good and not issues_found:
    print("✅ Configuration looks good!")
else:
    print("⚠️  Please review the issues above before uploading.")
print("=" * 60)
