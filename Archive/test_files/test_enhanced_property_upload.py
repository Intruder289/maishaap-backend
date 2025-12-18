#!/usr/bin/env python3
"""
Comprehensive test for enhanced property creation with image upload functionality
"""

import os
import requests
from PIL import Image
import io
import time

def create_test_images():
    """Create multiple test images for property upload"""
    test_images = []
    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan']
    
    for i, color in enumerate(colors):
        filename = f"test_property_image_{i+1}.jpg"
        img = Image.new('RGB', (800, 600), color)
        img.save(filename, 'JPEG')
        test_images.append(filename)
        print(f"✅ Created test image: {filename}")
    
    return test_images

def test_property_creation_page():
    """Test if the property creation page loads correctly"""
    print("Testing property creation page...")
    
    try:
        response = requests.get("http://127.0.0.1:8001/properties/create/", timeout=10)
        print(f"📄 Property creation page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Property creation page is accessible")
            
            # Check for enhanced image upload elements
            checks = [
                ('dragDropArea', 'Drag and drop area'),
                ('imageFileInput', 'File input'),
                ('browseImagesBtn', 'Browse button'),
                ('imagePreviewContainer', 'Preview container'),
                ('uploadProgress', 'Upload progress'),
                ('Property Images', 'Image section title'),
                ('drag-drop-area', 'Drag drop CSS class'),
                ('image-preview-container', 'Preview CSS class')
            ]
            
            for element, description in checks:
                if element in response.text:
                    print(f"✅ {description} found")
                else:
                    print(f"❌ {description} not found")
            
            return True
        else:
            print(f"❌ Property creation page returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing property creation page: {e}")
        return False

def test_image_upload_functionality():
    """Test the image upload functionality"""
    print("\nTesting image upload functionality...")
    
    # Create test images
    test_images = create_test_images()
    
    try:
        # Test uploading images to property ID 3 (existing property)
        property_id = 3
        image_file = test_images[0]
        
        print(f"📸 Testing image upload to property {property_id}...")
        
        with open(image_file, 'rb') as f:
            files = {'image': f}
            data = {
                'property': property_id,
                'caption': 'Test image upload to existing property',
                'is_primary': True,
                'order': 1
            }
            
            response = requests.post(
                "http://127.0.0.1:8001/api/property-images/",
                files=files,
                data=data,
                timeout=10
            )
            
            print(f"📤 Image upload response status: {response.status_code}")
            if response.status_code == 201:
                print("✅ Image uploaded successfully to existing property!")
                print(f"📋 Response: {response.json()}")
                return True
            elif response.status_code == 401:
                print("⚠️ Authentication required for image upload")
                return False
            elif response.status_code == 404:
                print("❌ API endpoint not found")
                return False
            else:
                print(f"❌ Upload failed: {response.text}")
                return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing image upload: {e}")
        return False
    
    finally:
        # Clean up test images
        for filename in test_images:
            try:
                os.remove(filename)
                print(f"🧹 Cleaned up: {filename}")
            except OSError:
                pass

def test_property_creation_with_images():
    """Test creating a new property with images"""
    print("\nTesting property creation with images...")
    
    # Create test images
    test_images = create_test_images()
    
    try:
        # First, get the page to extract CSRF token
        session = requests.Session()
        response = session.get("http://127.0.0.1:8001/properties/create/")
        
        if response.status_code != 200:
            print(f"❌ Cannot access property creation page: {response.status_code}")
            return False
        
        # Extract CSRF token
        csrf_token = None
        if 'csrfmiddlewaretoken' in response.text:
            import re
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print("✅ CSRF token found")
        
        if not csrf_token:
            print("⚠️ CSRF token not found - proceeding without authentication")
        
        # Prepare form data for property creation
        property_data = {
            'title': 'Test Property with Enhanced Image Upload',
            'description': 'A test property created with the enhanced image upload functionality',
            'property_type': '1',  # Assuming House type has ID 1
            'region': '1',  # Assuming first region has ID 1
            'address': '123 Test Street, Dar es Salaam',
            'bedrooms': '3',
            'bathrooms': '2',
            'size_sqft': '1200',
            'rent_amount': '500000',
            'status': 'available',
            'utilities_included': 'on',
            'is_furnished': 'on',
            'pets_allowed': 'on',
            'smoking_allowed': 'off',
            'is_featured': 'off',
            # Formset management data
            'form-TOTAL_FORMS': '3',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '10',
        }
        
        if csrf_token:
            property_data['csrfmiddlewaretoken'] = csrf_token
        
        # Prepare files for upload
        files = {}
        for i, image_file in enumerate(test_images[:3]):  # Upload first 3 images
            files[f'form-{i}-image'] = open(image_file, 'rb')
            property_data[f'form-{i}-caption'] = f'Test image {i+1}'
            property_data[f'form-{i}-is_primary'] = 'on' if i == 0 else 'off'
            property_data[f'form-{i}-order'] = str(i)
        
        print(f"📝 Attempting to create property with {len(files)} images...")
        
        response = session.post(
            "http://127.0.0.1:8001/properties/create/",
            data=property_data,
            files=files,
            timeout=30
        )
        
        print(f"📤 Property creation response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect after successful creation
            print("✅ Property created successfully!")
            print(f"🔄 Redirect location: {response.headers.get('Location', 'Unknown')}")
            return True
        elif response.status_code == 200:
            print("⚠️ Form returned 200 - checking for validation errors...")
            if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                print("❌ Form validation errors detected")
                # Print first few lines of response for debugging
                lines = response.text.split('\n')[:10]
                for line in lines:
                    if 'error' in line.lower() or 'invalid' in line.lower():
                        print(f"🔍 Error line: {line.strip()}")
            else:
                print("✅ Form processed successfully")
                return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            return False
        
        # Close file handles
        for file_handle in files.values():
            file_handle.close()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating property: {e}")
        return False
    
    finally:
        # Clean up test images
        for filename in test_images:
            try:
                os.remove(filename)
                print(f"🧹 Cleaned up: {filename}")
            except OSError:
                pass

def main():
    """Run all tests"""
    print("=== Enhanced Property Creation with Image Upload Tests ===\n")
    
    # Test 1: Property creation page
    page_ok = test_property_creation_page()
    
    if page_ok:
        # Test 2: Image upload to existing properties
        upload_ok = test_image_upload_functionality()
        
        # Test 3: Property creation with images
        creation_ok = test_property_creation_with_images()
        
        print(f"\n=== Test Results ===")
        print(f"📄 Property creation page: {'✅ PASS' if page_ok else '❌ FAIL'}")
        print(f"📸 Image upload functionality: {'✅ PASS' if upload_ok else '❌ FAIL'}")
        print(f"🏠 Property creation with images: {'✅ PASS' if creation_ok else '❌ FAIL'}")
        
        if page_ok and upload_ok and creation_ok:
            print("\n🎉 All tests passed! Enhanced image upload functionality is working.")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Cannot proceed with tests - property creation page not accessible")
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()
