#!/usr/bin/env python
"""
Script to check current .env configuration values
Shows what's configured locally before uploading to hosted server
"""

import os
import sys
from pathlib import Path
from decouple import config, Csv

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent

print("=" * 70)
print("CURRENT .ENV CONFIGURATION CHECK")
print("=" * 70)
print()

# Check if .env file exists
env_file = BASE_DIR / '.env'
if not env_file.exists():
    print("⚠️  WARNING: .env file not found!")
    print(f"   Expected location: {env_file}")
    print()
    print("   The script will show default values from settings.py")
    print()
else:
    print(f"✅ Found .env file: {env_file}")
    print()

print("-" * 70)
print("AZAMPAY CONFIGURATION")
print("-" * 70)

# AzamPay Settings
azam_pay_sandbox = config('AZAM_PAY_SANDBOX', default='True', cast=bool)
azam_pay_base_url = config('AZAM_PAY_BASE_URL', default='https://sandbox.azampay.co.tz')
azam_pay_webhook_url = config('AZAM_PAY_WEBHOOK_URL', default='https://portal.maishaapp.co.tz/api/v1/payments/webhook/azam-pay/')
azam_pay_client_id = config('AZAM_PAY_CLIENT_ID', default='')
azam_pay_client_secret = config('AZAM_PAY_CLIENT_SECRET', default='')
azam_pay_api_key = config('AZAM_PAY_API_KEY', default='')
azam_pay_app_name = config('AZAM_PAY_APP_NAME', default='Maisha Property Management')

print(f"AZAM_PAY_SANDBOX:        {azam_pay_sandbox}")
print(f"AZAM_PAY_BASE_URL:       {azam_pay_base_url}")
print(f"AZAM_PAY_WEBHOOK_URL:    {azam_pay_webhook_url}")
print(f"AZAM_PAY_CLIENT_ID:      {azam_pay_client_id[:20]}..." if len(azam_pay_client_id) > 20 else f"AZAM_PAY_CLIENT_ID:      {azam_pay_client_id or '(not set)'}")
print(f"AZAM_PAY_CLIENT_SECRET:  {'***' if azam_pay_client_secret else '(not set)'}")
print(f"AZAM_PAY_API_KEY:        {'***' if azam_pay_api_key else '(not set)'}")
print(f"AZAM_PAY_APP_NAME:       {azam_pay_app_name}")

print()
print("-" * 70)
print("BASE URL CONFIGURATION")
print("-" * 70)

base_url = config('BASE_URL', default='http://localhost:8000')
print(f"BASE_URL:                {base_url}")

print()
print("-" * 70)
print("DJANGO SETTINGS")
print("-" * 70)

debug = config('DEBUG', default='False', cast=bool)
allowed_hosts = config('ALLOWED_HOSTS', default='', cast=Csv())
secret_key = config('SECRET_KEY', default='')

print(f"DEBUG:                   {debug}")
print(f"ALLOWED_HOSTS:           {', '.join(allowed_hosts) if allowed_hosts else '(not set)'}")
print(f"SECRET_KEY:              {'***' if secret_key else '(not set)'}")

print()
print("-" * 70)
print("DATABASE CONFIGURATION")
print("-" * 70)

db_name = config('DATABASE_NAME', default='')
db_user = config('DATABASE_USER', default='')
db_host = config('DATABASE_HOST', default='localhost')
db_port = config('DATABASE_PORT', default='5432')

print(f"DATABASE_NAME:           {db_name or '(not set)'}")
print(f"DATABASE_USER:           {db_user or '(not set)'}")
print(f"DATABASE_HOST:           {db_host}")
print(f"DATABASE_PORT:           {db_port}")

print()
print("=" * 70)
print("CONFIGURATION ANALYSIS")
print("=" * 70)
print()

# Analysis
issues = []
recommendations = []

# Check sandbox mode
if azam_pay_sandbox:
    print("✅ AZAM_PAY_SANDBOX=True (Sandbox mode - good for testing)")
else:
    print("⚠️  AZAM_PAY_SANDBOX=False (Production mode)")
    recommendations.append("Set AZAM_PAY_SANDBOX=True for sandbox testing")

# Check base URL
if 'localhost' in base_url or '127.0.0.1' in base_url or 'ngrok' in base_url:
    print(f"⚠️  BASE_URL is set to local/ngrok: {base_url}")
    recommendations.append(f"Update BASE_URL to your hosted domain: https://your-hosted-domain.com")
else:
    print(f"✅ BASE_URL: {base_url}")

# Check webhook URL
if 'localhost' in azam_pay_webhook_url or '127.0.0.1' in azam_pay_webhook_url or 'ngrok' in azam_pay_webhook_url:
    print(f"⚠️  AZAM_PAY_WEBHOOK_URL is set to local/ngrok: {azam_pay_webhook_url}")
    recommendations.append(f"Update AZAM_PAY_WEBHOOK_URL to your hosted domain: https://your-hosted-domain.com/api/v1/payments/webhook/azam-pay/")
elif 'portal.maishaapp.co.tz' in azam_pay_webhook_url:
    print(f"✅ AZAM_PAY_WEBHOOK_URL: {azam_pay_webhook_url} (Production URL)")
    if azam_pay_sandbox:
        recommendations.append("For sandbox testing, update webhook URL to your hosted domain")
else:
    print(f"✅ AZAM_PAY_WEBHOOK_URL: {azam_pay_webhook_url}")

# Check credentials
if not azam_pay_client_id:
    issues.append("AZAM_PAY_CLIENT_ID is not set")
if not azam_pay_client_secret:
    issues.append("AZAM_PAY_CLIENT_SECRET is not set")
if not azam_pay_api_key:
    issues.append("AZAM_PAY_API_KEY is not set")

if issues:
    print()
    print("❌ ISSUES FOUND:")
    for issue in issues:
        print(f"   - {issue}")
else:
    print()
    print("✅ All AzamPay credentials are set")

# Check sandbox base URL
if azam_pay_sandbox and 'sandbox' not in azam_pay_base_url:
    issues.append(f"AZAM_PAY_SANDBOX=True but AZAM_PAY_BASE_URL is not sandbox: {azam_pay_base_url}")
    recommendations.append("Set AZAM_PAY_BASE_URL=https://sandbox.azampay.co.tz for sandbox testing")
elif azam_pay_sandbox and 'sandbox' in azam_pay_base_url:
    print(f"✅ AZAM_PAY_BASE_URL is correct for sandbox: {azam_pay_base_url}")

print()
if recommendations:
    print("📋 RECOMMENDATIONS FOR HOSTED SERVER:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
else:
    print("✅ Configuration looks good for sandbox testing!")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

# Determine status
if 'ngrok' in base_url or 'ngrok' in azam_pay_webhook_url:
    print("📍 CURRENT STATUS: Local testing with ngrok")
    print()
    print("   Before uploading to hosted server, update:")
    print(f"   - BASE_URL → Your hosted HTTPS URL")
    print(f"   - AZAM_PAY_WEBHOOK_URL → Your hosted HTTPS URL + /api/v1/payments/webhook/azam-pay/")
elif 'localhost' in base_url or '127.0.0.1' in base_url:
    print("📍 CURRENT STATUS: Local development")
    print()
    print("   Before uploading to hosted server, update:")
    print(f"   - BASE_URL → Your hosted HTTPS URL")
    print(f"   - AZAM_PAY_WEBHOOK_URL → Your hosted HTTPS URL + /api/v1/payments/webhook/azam-pay/")
elif 'portal.maishaapp.co.tz' in base_url or 'portal.maishaapp.co.tz' in azam_pay_webhook_url:
    print("📍 CURRENT STATUS: Production configuration")
    print()
    if azam_pay_sandbox:
        print("   ⚠️  You have sandbox mode but production URLs")
        print("   For sandbox testing, use your hosted domain (not portal.maishaapp.co.tz)")
    else:
        print("   ✅ Ready for production")
else:
    print("📍 CURRENT STATUS: Custom configuration")
    print()
    print(f"   BASE_URL: {base_url}")
    print(f"   AZAM_PAY_WEBHOOK_URL: {azam_pay_webhook_url}")

print()
print("=" * 70)
