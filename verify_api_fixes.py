#!/usr/bin/env python
"""
Quick verification script to check if the API fixes are correctly implemented.
This script checks the code structure without making actual API calls.
"""

import os
import sys
import re

def check_file_exists(filepath):
    """Check if a file exists"""
    return os.path.exists(filepath)

def check_string_in_file(filepath, search_strings, description):
    """Check if strings exist in a file"""
    if not check_file_exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = []
        for search_str in search_strings:
            found = search_str in content
            results.append(found)
            status = "✅" if found else "❌"
            print(f"  {status} {description}: '{search_str}'")
        
        return all(results)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def main():
    """Verify all fixes"""
    print("="*80)
    print("  VERIFYING API FIXES")
    print("="*80)
    
    # Check 1: Image Upload API - Swagger documentation
    print("\n1. Checking Image Upload API Documentation...")
    image_upload_checks = [
        ("properties/api_views.py", 
         ["manual_parameters", "openapi.IN_FORM", "openapi.TYPE_FILE", "image"],
         "Image upload Swagger documentation"),
    ]
    
    for filepath, search_strings, desc in image_upload_checks:
        print(f"\n   Checking {filepath}:")
        check_string_in_file(filepath, search_strings, desc)
    
    # Check 2: Phone Login - Improved phone handling
    print("\n2. Checking Phone Login Improvements...")
    phone_login_checks = [
        ("accounts/serializers.py",
         ["_normalize_phone", "_find_user_by_phone", "phone.startswith('+')"],
         "Phone normalization and lookup"),
    ]
    
    for filepath, search_strings, desc in phone_login_checks:
        print(f"\n   Checking {filepath}:")
        check_string_in_file(filepath, search_strings, desc)
    
    # Check 3: Manager Login - Manager role support
    print("\n3. Checking Manager Login Support...")
    manager_login_checks = [
        ("accounts/serializers.py",
         ["'Manager'", "valid_roles = ['Tenant', 'Property Owner', 'Manager']"],
         "Manager role in valid roles"),
    ]
    
    for filepath, search_strings, desc in manager_login_checks:
        print(f"\n   Checking {filepath}:")
        check_string_in_file(filepath, search_strings, desc)
    
    # Check 4: Verify serializer includes image field
    print("\n4. Checking PropertyImageUploadSerializer...")
    serializer_checks = [
        ("properties/serializers.py",
         ["class PropertyImageUploadSerializer", "'image'", "fields = ['id', 'property', 'image'"],
         "Image field in serializer"),
    ]
    
    for filepath, search_strings, desc in serializer_checks:
        print(f"\n   Checking {filepath}:")
        check_string_in_file(filepath, search_strings, desc)
    
    print("\n" + "="*80)
    print("  VERIFICATION COMPLETE")
    print("="*80)
    print("\n✅ Code structure checks completed.")
    print("⚠️  Note: This only verifies code structure, not runtime behavior.")
    print("   Run test_fixed_apis.py with actual credentials to test the APIs.")

if __name__ == "__main__":
    main()

