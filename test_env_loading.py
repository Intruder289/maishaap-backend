#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test to verify .env file is being loaded correctly
Run this on your server: python test_env_loading.py
"""

import os
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add project to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')

import django
django.setup()

from django.conf import settings

print("=" * 70)
print("TESTING ENV FILE LOADING")
print("=" * 70)
print()

# Check .env file location
env_file = BASE_DIR / '.env'
print(f"Project root: {BASE_DIR}")
print(f".env file path: {env_file}")
print(f".env exists: {env_file.exists()}")
print()

# Test Django settings
print("Django Settings:")
print(f"  AZAM_PAY_CLIENT_ID: {'✅ SET' if getattr(settings, 'AZAM_PAY_CLIENT_ID', '') else '❌ NOT SET'}")
if getattr(settings, 'AZAM_PAY_CLIENT_ID', ''):
    client_id = settings.AZAM_PAY_CLIENT_ID
    print(f"    Value: {client_id[:20]}...")
    
print(f"  AZAM_PAY_CLIENT_SECRET: {'✅ SET' if getattr(settings, 'AZAM_PAY_CLIENT_SECRET', '') else '❌ NOT SET'}")
print(f"  AZAM_PAY_APP_NAME: {getattr(settings, 'AZAM_PAY_APP_NAME', 'NOT SET')}")
print(f"  AZAM_PAY_SANDBOX: {getattr(settings, 'AZAM_PAY_SANDBOX', 'NOT SET')}")
print(f"  BASE_URL: {getattr(settings, 'BASE_URL', 'NOT SET')}")
print()

if getattr(settings, 'AZAM_PAY_CLIENT_ID', ''):
    print("✅ SUCCESS! Environment variables are loading correctly!")
    print("   The fix is working. Restart your web server and try payment again.")
else:
    print("❌ FAILED! Environment variables are still not loading.")
    print()
    print("Troubleshooting:")
    print(f"  1. Check .env file is at: {env_file}")
    print(f"  2. Check .env file has AZAM_PAY_CLIENT_ID set")
    print(f"  3. Check file permissions: ls -la {env_file}")
    print(f"  4. Check Django project root matches: {BASE_DIR}")

print()
print("=" * 70)
