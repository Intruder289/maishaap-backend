#!/usr/bin/env python3
"""
Test script to verify image upload functionality in the property form
"""

import os
import requests
from PIL import Image
import io

def create_test_image(filename, size=(800, 600), color='blue'):
    """Create a test image file"""
    img = Image.new('RGB', size, color)
    img.save(filename, 'JPEG')
    return filename

def test_image_upload():
    """Test the image upload functionality"""
    print("Testing image upload functionality...")
    
    # Create test images
    test_images = []
    colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink']
    
    for i, color in enumerate(colors):
        filename = f"test_image_{i+1}.jpg"
        create_test_image(filename, (800, 600), color)
        test_images.append(filename)
        print(f"Created test image: {filename}")
    
    # Test the dashboard endpoint
    try:
        response = requests.get("http://127.0.0.1:8001/")
        if response.status_code == 200:
            print("✅ Dashboard is accessible")
            
            # Check if the image upload form is present
            if 'property_images' in response.text and 'multiple' in response.text:
                print("✅ Image upload form is present with multiple file support")
            else:
                print("❌ Image upload form not found or missing multiple attribute")
                
            # Check if image preview functionality is present
            if 'image-preview-container' in response.text:
                print("✅ Image preview container is present")
            else:
                print("❌ Image preview container not found")
                
            # Check if validation is present
            if 'Maximum 10 images allowed' in response.text:
                print("✅ Image validation messages are present")
            else:
                print("❌ Image validation messages not found")
                
        else:
            print(f"❌ Dashboard returned status code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing dashboard: {e}")
    
    # Clean up test images
    for filename in test_images:
        try:
            os.remove(filename)
            print(f"Cleaned up: {filename}")
        except OSError:
            pass
    
    print("\nImage upload functionality test completed!")

if __name__ == "__main__":
    test_image_upload()
