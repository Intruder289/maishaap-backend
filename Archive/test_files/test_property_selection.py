#!/usr/bin/env python
import requests
import json
from bs4 import BeautifulSoup

def test_property_selection():
    print("TESTING PROPERTY SELECTION PAGES")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    session = requests.Session()
    
    # Test Hotel Property Selection
    print("\n1. Testing Hotel Property Selection...")
    try:
        response = session.get(f"{base_url}/properties/hotel/select-property/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for property selection content
            if "Property Selection" in response.text:
                print("   Property Selection page loaded successfully")
            else:
                print("   Property Selection content not found")
                
            # Check for hotel properties
            if "Grand Hotel" in response.text:
                print("   Hotel properties found in page")
            else:
                print("   Hotel properties not found")
                
        else:
            print(f"   Hotel selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Hotel selection error: {e}")
    
    # Test Lodge Property Selection
    print("\n2. Testing Lodge Property Selection...")
    try:
        response = session.get(f"{base_url}/properties/lodge/select-property/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "Property Selection" in response.text:
                print("   Lodge Property Selection page loaded successfully")
            else:
                print("   Lodge Property Selection content not found")
        else:
            print(f"   Lodge selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Lodge selection error: {e}")
    
    # Test Venue Property Selection
    print("\n3. Testing Venue Property Selection...")
    try:
        response = session.get(f"{base_url}/properties/venue/select-property/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "Property Selection" in response.text:
                print("   Venue Property Selection page loaded successfully")
            else:
                print("   Venue Property Selection content not found")
        else:
            print(f"   Venue selection failed: {response.status_code}")
    except Exception as e:
        print(f"   Venue selection error: {e}")
    
    # Test House Property Selection
    print("\n4. Testing House Property Selection...")
    try:
        response = session.get(f"{base_url}/properties/house/select-property/")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "Property Selection" in response.text:
                print("   House Property Selection page loaded successfully")
            else:
                print("   House Property Selection content not found")
        else:
            print(f"   House selection failed: {response.status_code}")
    except Exception as e:
        print(f"   House selection error: {e}")

if __name__ == "__main__":
    test_property_selection()
