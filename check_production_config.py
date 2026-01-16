#!/usr/bin/env python
"""
Production Configuration Verification Script

This script checks your current Django settings against production requirements.
Run this before deploying to production.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Error setting up Django: {e}")
    print("Make sure you're in the project root directory and Django is installed.")
    sys.exit(1)

from django.conf import settings
from decouple import config, Csv

print("=" * 70)
print("PRODUCTION CONFIGURATION VERIFICATION")
print("=" * 70)
print()

# Check if .env file exists
env_file = BASE_DIR / '.env'
if env_file.exists():
    print("[OK] .env file found")
else:
    print("[ERROR] .env file NOT found - create one before production!")
    print()

issues = []
warnings = []
passed = []

# 1. Check DEBUG
print("1. DEBUG Setting")
print("-" * 70)
debug_value = settings.DEBUG
if debug_value:
    issues.append("DEBUG is True - CRITICAL SECURITY RISK!")
    print(f"[ERROR] DEBUG = {debug_value} - MUST be False in production")
else:
    passed.append("DEBUG is False")
    print(f"[OK] DEBUG = {debug_value}")
print()

# 2. Check SECRET_KEY
print("2. SECRET_KEY Setting")
print("-" * 70)
secret_key = settings.SECRET_KEY
if secret_key == 'django-insecure--lcr^7cu6oeuae)6&4(*s8h_4e@2aph+104tmjtm%2nt0n0*m6':
    issues.append("SECRET_KEY is using insecure default - CRITICAL SECURITY RISK!")
    print("[ERROR] SECRET_KEY is using the insecure default value")
    print("   Generate a new key: python manage.py shell -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"")
elif len(secret_key) < 50:
    warnings.append("SECRET_KEY seems too short")
    print(f"[WARN] SECRET_KEY length: {len(secret_key)} (should be at least 50 characters)")
else:
    passed.append("SECRET_KEY is set and secure")
    print(f"[OK] SECRET_KEY is set (length: {len(secret_key)} characters)")
print()

# 3. Check ALLOWED_HOSTS
print("3. ALLOWED_HOSTS Setting")
print("-" * 70)
allowed_hosts = settings.ALLOWED_HOSTS
if '*' in allowed_hosts or len(allowed_hosts) == 0:
    issues.append("ALLOWED_HOSTS contains '*' or is empty - SECURITY RISK!")
    print(f"[ERROR] ALLOWED_HOSTS = {allowed_hosts}")
    print("   Must specify exact domains, not '*'")
else:
    passed.append("ALLOWED_HOSTS is properly configured")
    print(f"[OK] ALLOWED_HOSTS = {allowed_hosts}")
print()

# 4. Check ENVIRONMENT
print("4. ENVIRONMENT Setting")
print("-" * 70)
# Read from Django settings (which reads from .env via config())
# We need to check how Django is reading it
try:
    # Try to read from config directly (same way Django does)
    from decouple import config
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        from decouple import Config, RepositoryEnv
        _env_repo = RepositoryEnv(str(env_file))
        _config_obj = Config(_env_repo)
        environment = _config_obj('ENVIRONMENT', default='development')
    else:
        environment = os.environ.get('ENVIRONMENT', 'development')
except:
    # Fallback to checking Django settings
    environment = getattr(settings, 'ENVIRONMENT', os.environ.get('ENVIRONMENT', 'development'))

if environment == 'production':
    passed.append("ENVIRONMENT is set to production")
    print(f"[OK] ENVIRONMENT = {environment}")
else:
    warnings.append("ENVIRONMENT not set to production")
    print(f"[WARN] ENVIRONMENT = {environment} (should be 'production' for production deployment)")
    print(f"       Check your .env file has: ENVIRONMENT=production")
print()

# 5. Check Security Headers
print("5. Security Headers")
print("-" * 70)
security_headers = {
    'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', None),
    'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', None),
    'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', None),
    'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', None),
    'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', None),
}

if environment == 'production':
    if not security_headers['SECURE_SSL_REDIRECT']:
        warnings.append("SECURE_SSL_REDIRECT not set")
        print("[WARN] SECURE_SSL_REDIRECT not set (should be True in production)")
    else:
        passed.append("SECURE_SSL_REDIRECT is set")
        print("[OK] SECURE_SSL_REDIRECT = True")
    
    if not security_headers['SECURE_HSTS_SECONDS']:
        warnings.append("SECURE_HSTS_SECONDS not set")
        print("[WARN] SECURE_HSTS_SECONDS not set (recommended for production)")
    else:
        passed.append("SECURE_HSTS_SECONDS is set")
        print(f"[OK] SECURE_HSTS_SECONDS = {security_headers['SECURE_HSTS_SECONDS']}")
    
    if security_headers['SESSION_COOKIE_SECURE']:
        passed.append("SESSION_COOKIE_SECURE is set")
        print("[OK] SESSION_COOKIE_SECURE = True")
    else:
        warnings.append("SESSION_COOKIE_SECURE not set")
        print("[WARN] SESSION_COOKIE_SECURE not set (should be True in production)")
else:
    print("[INFO] Skipping security headers check (not in production mode)")
print()

# 6. Check CORS Configuration
print("6. CORS Configuration")
print("-" * 70)
cors_allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
cors_allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])

if environment == 'production':
    if cors_allow_all:
        issues.append("CORS_ALLOW_ALL_ORIGINS is True in production - SECURITY RISK!")
        print("[ERROR] CORS_ALLOW_ALL_ORIGINS = True (should be False in production)")
    else:
        passed.append("CORS_ALLOW_ALL_ORIGINS is False")
        print("[OK] CORS_ALLOW_ALL_ORIGINS = False")
    
    if not cors_allowed_origins or 'localhost' in str(cors_allowed_origins).lower():
        warnings.append("CORS_ALLOWED_ORIGINS not properly configured")
        print(f"[WARN] CORS_ALLOWED_ORIGINS = {cors_allowed_origins}")
        print("   Should contain production domains only")
    else:
        passed.append("CORS_ALLOWED_ORIGINS is configured")
        print(f"[OK] CORS_ALLOWED_ORIGINS = {cors_allowed_origins}")
else:
    print(f"[INFO] CORS_ALLOW_ALL_ORIGINS = {cors_allow_all} (OK for development)")
print()

# 7. Check Database Configuration
print("7. Database Configuration")
print("-" * 70)
db_config = settings.DATABASES['default']
db_engine = db_config.get('ENGINE', '')
if 'sqlite' in db_engine.lower():
    warnings.append("Using SQLite database (not recommended for production)")
    print("[WARN] Database engine: SQLite (PostgreSQL recommended for production)")
else:
    passed.append("Using PostgreSQL database")
    print(f"[OK] Database engine: {db_engine}")

db_password = db_config.get('PASSWORD', '')
if db_password == 'alfred' or not db_password:
    warnings.append("Database password may be using default or empty")
    print("[WARN] Database password: Check if using strong password")
else:
    passed.append("Database password is set")
    print("[OK] Database password is configured")
print()

# 8. Check AZAM Pay Configuration
print("8. AZAM Pay Configuration")
print("-" * 70)
azam_sandbox = getattr(settings, 'AZAM_PAY_SANDBOX', True)
if environment == 'production':
    if azam_sandbox:
        issues.append("AZAM_PAY_SANDBOX is True in production - CRITICAL!")
        print("[ERROR] AZAM_PAY_SANDBOX = True (MUST be False in production)")
    else:
        passed.append("AZAM_PAY_SANDBOX is False")
        print("[OK] AZAM_PAY_SANDBOX = False")
else:
    print(f"[INFO] AZAM_PAY_SANDBOX = {azam_sandbox} (OK for development)")

azam_client_id = getattr(settings, 'AZAM_PAY_CLIENT_ID', '')
if azam_client_id:
    passed.append("AZAM_PAY_CLIENT_ID is set")
    print("[OK] AZAM_PAY_CLIENT_ID is configured")
else:
    warnings.append("AZAM_PAY_CLIENT_ID not set")
    print("[WARN] AZAM_PAY_CLIENT_ID not set")
print()

# 9. Check Static Files Configuration
print("9. Static Files Configuration")
print("-" * 70)
static_root = getattr(settings, 'STATIC_ROOT', None)
if static_root:
    passed.append("STATIC_ROOT is configured")
    print(f"[OK] STATIC_ROOT = {static_root}")
    if Path(static_root).exists():
        print(f"   Directory exists: {Path(static_root).exists()}")
    else:
        warnings.append("STATIC_ROOT directory doesn't exist (run collectstatic)")
        print("[WARN] STATIC_ROOT directory doesn't exist - run: python manage.py collectstatic")
else:
    warnings.append("STATIC_ROOT not configured")
    print("[WARN] STATIC_ROOT not configured")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()

if issues:
    print("[CRITICAL] ISSUES (Must fix before production):")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print()

if warnings:
    print("[WARNINGS] (Should fix before production):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    print()

if passed:
    print("[PASSED] CHECKS:")
    for i, check in enumerate(passed, 1):
        print(f"   {i}. {check}")
    print()

# Final verdict
print("=" * 70)
if issues:
    print("[RESULT] NOT PRODUCTION READY - Fix critical issues above")
    sys.exit(1)
elif warnings:
    print("[RESULT] PRODUCTION READY WITH WARNINGS - Review warnings above")
    sys.exit(0)
else:
    print("[RESULT] PRODUCTION READY - All checks passed!")
    sys.exit(0)
