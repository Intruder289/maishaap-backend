#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_property_selection_with_client():
    print("TESTING PROPERTY SELECTION WITH DJANGO CLIENT")
    print("=" * 60)
    
    # Create a test client
    client = Client()
    
    # Try different login credentials
    login_attempts = [
        ('admin', 'admin123'),
        ('admin', 'password'),
        ('admin', 'admin'),
        ('property_manager1', 'password123'),
        ('property_manager1', 'password'),
        ('admin_user', 'admin123'),
    ]
    
    logged_in = False
    for username, password in login_attempts:
        print(f"\nTrying login: {username} / {password}")
        login_success = client.login(username=username, password=password)
        if login_success:
            print(f"   Login successful with {username}")
            logged_in = True
            break
        else:
            print(f"   Login failed with {username}")
    
    if not logged_in:
        print("\nAll login attempts failed")
        return
    
    # Test Hotel Property Selection
    print("\n1. Testing Hotel Property Selection...")
    try:
        response = client.get('/properties/hotel/select-property/')
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.content)}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            if "Property Selection" in content:
                print("   Property Selection content found")
            else:
                print("   Property Selection content NOT found")
                
            if "Hotel Management" in content:
                print("   Hotel Management content found")
            else:
                print("   Hotel Management content NOT found")
                
            if "Grand Hotel" in content:
                print("   Grand Hotel content found")
            else:
                print("   Grand Hotel content NOT found")
                
            if "Work with All Properties" in content:
                print("   Work with All Properties content found")
            else:
                print("   Work with All Properties content NOT found")
                
        else:
            print(f"   Hotel selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Hotel selection error: {e}")
    
    # Test Lodge Property Selection
    print("\n2. Testing Lodge Property Selection...")
    try:
        response = client.get('/properties/lodge/select-property/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if "Property Selection" in content:
                print("   Lodge Property Selection content found")
            else:
                print("   Lodge Property Selection content NOT found")
        else:
            print(f"   Lodge selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Lodge selection error: {e}")
    
    # Test Venue Property Selection
    print("\n3. Testing Venue Property Selection...")
    try:
        response = client.get('/properties/venue/select-property/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if "Property Selection" in content:
                print("   Venue Property Selection content found")
            else:
                print("   Venue Property Selection content NOT found")
        else:
            print(f"   Venue selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Venue selection error: {e}")
    
    # Test House Property Selection
    print("\n4. Testing House Property Selection...")
    try:
        response = client.get('/properties/house/select-property/')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if "Property Selection" in content:
                print("   House Property Selection content found")
            else:
                print("   House Property Selection content NOT found")
        else:
            print(f"   House selection failed: {response.status_code}")
    except Exception as e:
        print(f"   House selection error: {e}")

if __name__ == "__main__":
    test_property_selection_with_client()
