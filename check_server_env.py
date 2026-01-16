#!/usr/bin/env python
"""
Script to check if .env file is being read correctly on the server
Run this on your hosted server to diagnose environment variable issues
"""

import os
from pathlib import Path

# Get project root directory
BASE_DIR = Path(__file__).resolve().parent

print("=" * 70)
print("SERVER ENVIRONMENT VARIABLES DIAGNOSTIC")
print("=" * 70)
print()

# Check 1: .env file location
print("-" * 70)
print("1. CHECKING .ENV FILE LOCATION")
print("-" * 70)

env_file = BASE_DIR / '.env'
print(f"Expected .env location: {env_file}")
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    print(f"✅ .env file found!")
    print(f"File size: {env_file.stat().st_size} bytes")
    print(f"File permissions: {oct(env_file.stat().st_mode)}")
else:
    print(f"❌ .env file NOT FOUND!")
    print(f"   Please ensure .env file is in: {BASE_DIR}")

print()

# Check 2: Try reading .env file directly
print("-" * 70)
print("2. READING .ENV FILE CONTENT")
print("-" * 70)

if env_file.exists():
    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()
            print(f"Total lines in .env: {len(lines)}")
            print()
            print("AzamPay related variables found:")
            azampay_vars = [line.strip() for line in lines if 'AZAM_PAY' in line.upper() and not line.strip().startswith('#')]
            if azampay_vars:
                for var in azampay_vars:
                    # Mask secrets
                    if 'SECRET' in var or 'KEY' in var:
                        parts = var.split('=', 1)
                        if len(parts) == 2:
                            print(f"  {parts[0]}=***")
                        else:
                            print(f"  {var}")
                    else:
                        print(f"  {var}")
            else:
                print("  ❌ No AZAM_PAY variables found in .env file!")
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
else:
    print("❌ Cannot read .env file - file not found")

print()

# Check 3: Test python-decouple
print("-" * 70)
print("3. TESTING PYTHON-DECOUPLE")
print("-" * 70)

try:
    from decouple import config
    print("✅ python-decouple is installed")
    
    # Try to read a variable
    test_var = config('AZAM_PAY_CLIENT_ID', default='NOT_FOUND')
    if test_var == 'NOT_FOUND':
        print("❌ AZAM_PAY_CLIENT_ID not found by python-decouple")
        print("   This means .env file is not being read correctly")
    else:
        print(f"✅ AZAM_PAY_CLIENT_ID found: {test_var[:20]}...")
        
    # Check if .env file is in the right location for decouple
    print()
    print("python-decouple looks for .env in:")
    print(f"  1. Current directory: {os.getcwd()}")
    print(f"  2. Project root: {BASE_DIR}")
    
except ImportError:
    print("❌ python-decouple is NOT installed")
    print("   Install it: pip install python-decouple")

print()

# Check 4: Check Django settings
print("-" * 70)
print("4. CHECKING DJANGO SETTINGS")
print("-" * 70)

try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
    django.setup()
    
    from django.conf import settings
    
    print("✅ Django is configured")
    print()
    print("AzamPay settings from Django:")
    print(f"  AZAM_PAY_CLIENT_ID: {'SET' if getattr(settings, 'AZAM_PAY_CLIENT_ID', '') else 'NOT SET'}")
    print(f"  AZAM_PAY_CLIENT_SECRET: {'SET' if getattr(settings, 'AZAM_PAY_CLIENT_SECRET', '') else 'NOT SET'}")
    print(f"  AZAM_PAY_APP_NAME: {getattr(settings, 'AZAM_PAY_APP_NAME', 'NOT SET')}")
    print(f"  AZAM_PAY_SANDBOX: {getattr(settings, 'AZAM_PAY_SANDBOX', 'NOT SET')}")
    print(f"  AZAM_PAY_BASE_URL: {getattr(settings, 'AZAM_PAY_BASE_URL', 'NOT SET')}")
    
    client_id = getattr(settings, 'AZAM_PAY_CLIENT_ID', '')
    if not client_id:
        print()
        print("❌ AZAM_PAY_CLIENT_ID is NOT set in Django settings!")
        print("   This is why you're getting the error.")
        
except Exception as e:
    print(f"❌ Error checking Django settings: {e}")
    print("   Make sure you're running this from the project root directory")

print()

# Check 5: Environment variables
print("-" * 70)
print("5. SYSTEM ENVIRONMENT VARIABLES")
print("-" * 70)

azam_env_vars = {k: v for k, v in os.environ.items() if 'AZAM' in k.upper()}
if azam_env_vars:
    print("AzamPay variables in system environment:")
    for key, value in azam_env_vars.items():
        if 'SECRET' in key or 'KEY' in key:
            print(f"  {key}=***")
        else:
            print(f"  {key}={value}")
else:
    print("No AzamPay variables in system environment (this is OK if using .env file)")

print()

# Recommendations
print("=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print()

if not env_file.exists():
    print("1. ❌ .env file is missing!")
    print("   → Upload .env file to the server")
    print(f"   → Place it in: {BASE_DIR}")
    print()
elif not getattr(settings, 'AZAM_PAY_CLIENT_ID', ''):
    print("1. ❌ .env file exists but variables not being read!")
    print("   → Check .env file has AZAM_PAY_CLIENT_ID set")
    print("   → Make sure .env file is in project root (same directory as manage.py)")
    print("   → Restart your web server after updating .env")
    print()
    print("2. Common issues:")
    print("   → .env file in wrong directory")
    print("   → .env file has wrong permissions (should be readable)")
    print("   → Web server needs restart after .env changes")
    print("   → Working directory is different when server runs")
    print()

print("=" * 70)
