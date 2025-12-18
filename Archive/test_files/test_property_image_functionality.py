#!/usr/bin/env python3
"""
Test script for property creation with image upload functionality
"""

import os
import requests
from PIL import Image
import io

def create_test_images():
    """Create multiple test images for property upload"""
    test_images = []
    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'cyan']
    
    for i, color in enumerate(colors):
        filename = f"test_property_image_{i+1}.jpg"
        img = Image.new('RGB', (800, 600), color)
        img.save(filename, 'JPEG')
        test_images.append(filename)
        print(f"Created test image: {filename}")
    
    return test_images

def test_property_creation_form():
    """Test the property creation form"""
    print("Testing property creation form...")
    
    try:
        # Test accessing the property creation page
        response = requests.get("http://127.0.0.1:8001/properties/create/")
        print(f"Property creation page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Property creation page is accessible")
            
            # Check if image upload form is present
            if 'image_formset' in response.text and 'Property Images' in response.text:
                print("✅ Image upload form is present")
            else:
                print("❌ Image upload form not found")
                
            # Check for formset management
            if 'management_form' in response.text:
                print("✅ Formset management form is present")
            else:
                print("❌ Formset management form not found")
                
        else:
            print(f"❌ Property creation page returned status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing property creation page: {e}")

def test_property_creation_with_images():
    """Test creating a property with images"""
    print("\nTesting property creation with images...")
    
    # Create test images
    test_images = create_test_images()
    
    try:
        # Prepare form data for property creation
        property_data = {
            'title': 'Test Property with Images',
            'description': 'A test property created with multiple images',
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
        
        # Prepare files for upload
        files = {}
        for i, image_file in enumerate(test_images[:3]):  # Upload first 3 images
            files[f'form-{i}-image'] = open(image_file, 'rb')
            property_data[f'form-{i}-caption'] = f'Test image {i+1}'
            property_data[f'form-{i}-is_primary'] = 'on' if i == 0 else 'off'
            property_data[f'form-{i}-order'] = str(i)
        
        print(f"Attempting to create property with {len(files)} images...")
        
        # Note: This would require authentication and CSRF token in a real scenario
        response = requests.post(
            "http://127.0.0.1:8001/properties/create/",
            data=property_data,
            files=files
        )
        
        print(f"Property creation response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect after successful creation
            print("✅ Property created successfully!")
            print(f"Redirect location: {response.headers.get('Location', 'Unknown')}")
        elif response.status_code == 200:
            print("⚠️ Form returned 200 - might have validation errors")
            if 'error' in response.text.lower() or 'invalid' in response.text.lower():
                print("❌ Form validation errors detected")
            else:
                print("✅ Form processed successfully")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
        
        # Close file handles
        for file_handle in files.values():
            file_handle.close()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating property: {e}")
    
    # Clean up test images
    for filename in test_images:
        try:
            os.remove(filename)
            print(f"Cleaned up: {filename}")
        except OSError:
            pass

def test_existing_property_image_upload():
    """Test uploading images to existing properties"""
    print("\nTesting image upload to existing properties...")
    
    # Create test images
    test_images = create_test_images()
    
    try:
        # Test uploading images to property ID 3
        property_id = 3
        image_file = test_images[0]
        
        print(f"Testing image upload to property {property_id}...")
        
        with open(image_file, 'rb') as f:
            files = {'image': f}
            data = {
                'property': property_id,
                'caption': 'Test image upload to existing property',
                'is_primary': True,
                'order': 1
            }
            
            # Note: This would require authentication in a real scenario
            response = requests.post(
                "http://127.0.0.1:8001/api/property-images/",
                files=files,
                data=data
            )
            
            print(f"Image upload response status: {response.status_code}")
            if response.status_code == 201:
                print("✅ Image uploaded successfully to existing property!")
                print(f"Response: {response.json()}")
            elif response.status_code == 401:
                print("⚠️ Authentication required for image upload")
            else:
                print(f"❌ Upload failed: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing image upload: {e}")
    
    # Clean up test images
    for filename in test_images:
        try:
            os.remove(filename)
            print(f"Cleaned up: {filename}")
        except OSError:
            pass

def main():
    """Run all tests"""
    print("=== Property Creation with Image Upload Tests ===\n")
    
    # Test 1: Property creation form
    test_property_creation_form()
    
    # Test 2: Property creation with images
    test_property_creation_with_images()
    
    # Test 3: Image upload to existing properties
    test_existing_property_image_upload()
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()
