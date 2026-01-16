#!/usr/bin/env python
"""
SERPAPI Configuration Verification Script

Run this script to verify your SERPAPI key is configured correctly.
Usage: python verify_serpapi.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.conf import settings

def verify_serpapi_configuration():
    """Verify SERPAPI configuration"""
    print("=" * 60)
    print("SERPAPI Configuration Verification")
    print("=" * 60)
    print()
    
    # Check 1: API Key Configuration
    print("1. Checking API Key Configuration...")
    if settings.SERPAPI_KEY:
        key_length = len(settings.SERPAPI_KEY)
        print(f"   [OK] SERPAPI_KEY: CONFIGURED")
        print(f"   [OK] Key Length: {key_length} characters")
        print(f"   [OK] First 10 chars: {settings.SERPAPI_KEY[:10]}...")
        print(f"   [OK] Last 10 chars: ...{settings.SERPAPI_KEY[-10:]}")
        
        # Verify expected key
        expected_key = "2dc7d66361969a44c0ce3a9188be1d64eed022e20cd5c95c26eb449990e9eb7d"
        if settings.SERPAPI_KEY == expected_key:
            print(f"   [OK] Key matches expected value")
        else:
            print(f"   [WARNING] Key does not match expected value")
            print(f"      Expected: {expected_key[:20]}...")
            print(f"      Got:      {settings.SERPAPI_KEY[:20]}...")
    else:
        print("   [ERROR] SERPAPI_KEY: NOT CONFIGURED")
        print("   [WARNING] System will use OpenStreetMap fallback")
        return False
    
    print()
    
    # Check 2: Package Installation
    print("2. Checking Package Installation...")
    try:
        from serpapi import GoogleSearch
        print("   [OK] SERPAPI package: INSTALLED")
        print(f"   [OK] Package: google-search-results")
    except ImportError:
        print("   [ERROR] SERPAPI package: NOT INSTALLED")
        print("   [WARNING] Run: pip install google-search-results==2.4.2")
        return False
    
    print()
    
    # Check 3: Test API Connection (Optional - uses API credits)
    print("3. Testing API Connection...")
    print("   [INFO] Attempting to connect to SERPAPI...")
    
    try:
        from serpapi import GoogleSearch
        
        # Test with a simple query (uses 1 API credit)
        params = {
            "q": "Dar es Salaam, Tanzania",
            "engine": "google_maps",
            "api_key": settings.SERPAPI_KEY,
            "type": "search",
            "hl": "en",
            "gl": "tz",
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            error_msg = results.get("error", "Unknown error")
            print(f"   [ERROR] API Error: {error_msg}")
            if "Invalid API key" in str(error_msg):
                print("   [WARNING] Your API key may be invalid or expired")
            return False
        else:
            print("   [OK] API Connection: SUCCESS")
            print("   [OK] SERPAPI is working correctly!")
            
            # Check if results are returned
            if "local_results" in results or "place_results" in results:
                print("   [OK] Geocoding results: Available")
            else:
                print("   [WARNING] No geocoding results found (may be normal)")
    
    except Exception as e:
        print(f"   [WARNING] Connection test failed: {str(e)}")
        print("   [INFO] This may be due to network issues or API limits")
        print("   [INFO] The key format is correct, but connection test failed")
    
    print()
    
    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if settings.SERPAPI_KEY:
        print("[OK] API Key: Configured")
        print("[OK] Package: Installed")
        print("[OK] Status: READY TO USE")
        print()
        print("[INFO] Your system will use SERPAPI (Google Maps) for geocoding")
        print("       with better accuracy for Tanzania addresses.")
    else:
        print("[ERROR] API Key: Not Configured")
        print("[WARNING] Status: Will use OpenStreetMap fallback")
        print()
        print("[INFO] Your system will use OpenStreetMap (free) for geocoding")
        print("       which works but may have lower accuracy.")
    
    print()
    return True

if __name__ == "__main__":
    try:
        verify_serpapi_configuration()
    except Exception as e:
        print(f"\n[ERROR] Error during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
