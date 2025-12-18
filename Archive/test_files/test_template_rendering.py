#!/usr/bin/env python3
"""
Test to check if there's a template rendering issue
"""

import requests
import re

def test_template_rendering():
    """Test template rendering"""
    print("Testing template rendering...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/login/", timeout=10)
        print(f"📄 Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if it's a Django error page
            if 'Django' in content and 'error' in content.lower():
                print("❌ Django error page detected")
                return False
            
            # Check if it's HTML
            if not content.strip().startswith('<!DOCTYPE html>') and not content.strip().startswith('<html'):
                print("❌ Response is not HTML")
                print(f"📄 Response starts with: {content[:200]}")
                return False
            
            # Check for basic HTML structure
            if '<html' in content and '</html>' in content:
                print("✅ Basic HTML structure found")
            else:
                print("❌ Basic HTML structure not found")
            
            # Check for Django template tags (should NOT be in rendered HTML)
            if '{%' in content:
                print("❌ Django template tags found (template not rendered properly)")
            else:
                print("✅ Django template tags properly processed")
            
            # Check for our specific content
            if 'Sign In' in content or 'Welcome Back' in content:
                print("✅ Login page content found")
            else:
                print("❌ Login page content not found")
            
            # Check if the template is being rendered at all
            if 'MAISHA' in content or 'Property Management' in content:
                print("✅ Template content found")
            else:
                print("❌ Template content not found")
            
            # Let's see what's actually in the response
            print(f"\n📄 Response length: {len(content)}")
            
            # Look for any error messages
            error_patterns = [
                r'TemplateDoesNotExist',
                r'TemplateSyntaxError',
                r'Exception',
                r'Error',
                r'Traceback'
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"⚠️ Found {pattern} in response")
            
            return True
        else:
            print(f"❌ Cannot access login page: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing login page: {e}")
        return False

if __name__ == "__main__":
    test_template_rendering()
