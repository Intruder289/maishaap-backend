#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, Booking, Room
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from properties.views import hotel_dashboard

def test_hotel_dashboard_context():
    print("TESTING HOTEL DASHBOARD CONTEXT")
    print("=" * 50)
    
    # Create a test request
    factory = RequestFactory()
    request = factory.get('/properties/hotel/dashboard/')
    
    # Add session middleware
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    
    # Set a test user
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.filter(username='property_manager1').first()
    
    if user:
        request.user = user
        print(f"Using user: {user.username}")
    else:
        print("No user found!")
        return
    
    # Call the view
    try:
        response = hotel_dashboard(request)
        print(f"Response status: {response.status_code}")
        
        # Check context
        context = response.context_data
        if context:
            print("\nContext variables:")
            for key, value in context.items():
                print(f"  {key}: {value}")
        else:
            print("No context data found")
            
    except Exception as e:
        print(f"Error calling view: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hotel_dashboard_context()
