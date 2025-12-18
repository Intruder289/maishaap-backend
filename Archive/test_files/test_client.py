#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, Booking, Room
from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware

def test_hotel_dashboard_with_client():
    print("TESTING HOTEL DASHBOARD WITH CLIENT")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Login
    login_success = client.login(username='admin', password='admin123')
    if not login_success:
        login_success = client.login(username='property_manager1', password='password123')
    
    if login_success:
        print("Login successful")
    else:
        print("Login failed")
        return
    
    # Test hotel dashboard
    response = client.get('/properties/hotel/dashboard/')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        # Check context
        context = response.context
        print("\nContext variables:")
        for key, value in context.items():
            print(f"  {key}: {value}")
        
        # Check template content
        content = response.content.decode('utf-8')
        
        # Check for specific elements
        if "Total Rooms" in content:
            print("\nTemplate check: 'Total Rooms' found in content")
        else:
            print("\nTemplate check: 'Total Rooms' NOT found in content")
            
        if "Managing: All Hotels" in content:
            print("Template check: 'Managing: All Hotels' found in content")
        else:
            print("Template check: 'Managing: All Hotels' NOT found in content")
            
        if "create_hotel_booking" in content:
            print("Template check: 'create_hotel_booking' found in content")
        else:
            print("Template check: 'create_hotel_booking' NOT found in content")
    else:
        print(f"Failed to get dashboard: {response.status_code}")

if __name__ == "__main__":
    test_hotel_dashboard_with_client()
