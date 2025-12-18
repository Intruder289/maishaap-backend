#!/usr/bin/env python3
"""
Test script to check if image_formset is being passed to the template
"""

import requests
import re

def test_image_formset_in_template():
    """Test if image_formset is present in the template"""
    print("Testing image_formset in template...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/properties/create/", timeout=10)
        print(f"📄 Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for image_formset related content
            checks = [
                ('image_formset', 'image_formset variable'),
                ('Property Images', 'Property Images section'),
                ('form-TOTAL_FORMS', 'Formset management form'),
                ('form-INITIAL_FORMS', 'Formset initial forms'),
                ('form-MIN_NUM_FORMS', 'Formset min forms'),
                ('form-MAX_NUM_FORMS', 'Formset max forms'),
                ('PropertyImageFormSet', 'PropertyImageFormSet class'),
                ('image', 'image field'),
                ('caption', 'caption field'),
                ('is_primary', 'is_primary field'),
                ('order', 'order field')
            ]
            
            print("\n🔍 Checking for image formset elements:")
            for element, description in checks:
                if element in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Check if the enhanced image upload section is present
            print("\n🔍 Checking for enhanced image upload elements:")
            enhanced_elements = [
                ('dragDropArea', 'Drag drop area'),
                ('imageFileInput', 'File input'),
                ('browseImagesBtn', 'Browse button'),
                ('imagePreviewContainer', 'Preview container'),
                ('uploadProgress', 'Upload progress'),
                ('drag-drop-area', 'Drag drop CSS class'),
                ('image-preview-container', 'Preview CSS class')
            ]
            
            for element, description in enhanced_elements:
                if element in content:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            # Check if the template is using the enhanced version
            if 'dragDropArea' in content:
                print("\n✅ Enhanced image upload template is being used")
            else:
                print("\n❌ Enhanced image upload template is NOT being used")
                print("🔍 This suggests the template changes are not taking effect")
                
                # Check if there are any template errors
                if 'error' in content.lower() or 'exception' in content.lower():
                    print("⚠️ Possible template errors detected")
                
                # Check the template structure
                if '{% if image_formset %}' in content:
                    print("✅ image_formset condition is present")
                else:
                    print("❌ image_formset condition is missing")
                
                if '{% endif %}' in content:
                    print("✅ Template has proper endif")
                else:
                    print("❌ Template missing endif")
            
            return True
        else:
            print(f"❌ Cannot access property creation page: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing property creation page: {e}")
        return False

if __name__ == "__main__":
    test_image_formset_in_template()
