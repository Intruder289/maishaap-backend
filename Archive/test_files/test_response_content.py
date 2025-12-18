#!/usr/bin/env python3
"""
Test to see what's actually being returned by the server
"""

import requests

def check_actual_response():
    """Check what's actually being returned"""
    print("Checking actual response content...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/properties/create/", timeout=10)
        print(f"📄 Response status: {response.status_code}")
        print(f"📄 Response headers: {dict(response.headers)}")
        print(f"📄 Content length: {len(response.text)}")
        
        if response.status_code == 200:
            content = response.text
            
            # Show first 500 characters
            print(f"\n📄 First 500 characters of response:")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
            
            # Show last 500 characters
            print(f"\n📄 Last 500 characters of response:")
            print("-" * 50)
            print(content[-500:])
            print("-" * 50)
            
            # Check if it's HTML
            if content.strip().startswith('<!DOCTYPE html>') or content.strip().startswith('<html'):
                print("✅ Response is HTML")
            else:
                print("❌ Response is not HTML")
                print(f"📄 Response starts with: {content[:100]}")
            
            # Check for Django template tags
            if '{%' in content:
                print("✅ Django template tags found")
            else:
                print("❌ Django template tags not found")
            
            # Check for any error messages
            if 'error' in content.lower() or 'exception' in content.lower():
                print("⚠️ Possible error in response")
            
            return True
        else:
            print(f"❌ Cannot access property creation page: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing property creation page: {e}")
        return False

if __name__ == "__main__":
    check_actual_response()
