#!/usr/bin/env python3
"""
Simple test to check what's actually being rendered in the template
"""

import requests

def check_template_content():
    """Check what's actually in the template"""
    print("Checking template content...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/properties/create/", timeout=10)
        print(f"📄 Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Look for specific sections
            print("\n🔍 Looking for specific sections:")
            
            # Check if the enhanced image upload section is present
            if 'Property Images' in content:
                print("✅ 'Property Images' section found")
            else:
                print("❌ 'Property Images' section not found")
            
            # Check if the enhanced image upload HTML is present
            if 'drag-drop-area' in content:
                print("✅ 'drag-drop-area' class found")
            else:
                print("❌ 'drag-drop-area' class not found")
            
            # Check if the JavaScript is present
            if 'dragDropArea' in content:
                print("✅ 'dragDropArea' JavaScript found")
            else:
                print("❌ 'dragDropArea' JavaScript not found")
            
            # Check if the CSS is present
            if 'image-upload-container' in content:
                print("✅ 'image-upload-container' CSS found")
            else:
                print("❌ 'image-upload-container' CSS not found")
            
            # Check if the formset is present
            if 'form-TOTAL_FORMS' in content:
                print("✅ Formset management form found")
            else:
                print("❌ Formset management form not found")
            
            # Check if the image_formset condition is present
            if '{% if image_formset %}' in content:
                print("✅ image_formset condition found")
            else:
                print("❌ image_formset condition not found")
            
            # Check if the template is using the enhanced version
            if 'dragDropArea' in content and 'image-upload-container' in content:
                print("\n✅ Enhanced image upload template is being used")
            else:
                print("\n❌ Enhanced image upload template is NOT being used")
                
                # Let's see what's actually in the template
                print("\n🔍 Checking for any image-related content:")
                image_keywords = ['image', 'upload', 'file', 'formset', 'Property']
                for keyword in image_keywords:
                    if keyword in content:
                        print(f"✅ '{keyword}' found in template")
                    else:
                        print(f"❌ '{keyword}' not found in template")
                
                # Check the template structure
                print("\n🔍 Checking template structure:")
                if '{% extends' in content:
                    print("✅ Template extends found")
                else:
                    print("❌ Template extends not found")
                
                if '{% block content %}' in content:
                    print("✅ Content block found")
                else:
                    print("❌ Content block not found")
                
                if '{% endblock %}' in content:
                    print("✅ Endblock found")
                else:
                    print("❌ Endblock not found")
            
            return True
        else:
            print(f"❌ Cannot access property creation page: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing property creation page: {e}")
        return False

if __name__ == "__main__":
    check_template_content()
