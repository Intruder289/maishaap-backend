"""
Test script to verify rent reminder dashboard functionality
"""

import os
import sys
import django

# Setup Django FIRST
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from properties.models import (
    Property, PropertyType, Region, Booking, Customer,
    HouseRentReminderSettings, HouseRentReminderTemplate, HouseRentReminder
)

def test_rent_reminder_dashboard():
    print("TESTING RENT REMINDER DASHBOARD")
    print("=" * 50)
    
    # Check if we have data
    print("\n1. Checking database data...")
    
    house_properties = Property.objects.filter(property_type__name__iexact='house')
    print(f"   House properties: {house_properties.count()}")
    
    settings = HouseRentReminderSettings.objects.all()
    print(f"   Reminder settings: {settings.count()}")
    
    templates = HouseRentReminderTemplate.objects.all()
    print(f"   Templates: {templates.count()}")
    
    reminders = HouseRentReminder.objects.all()
    print(f"   Reminders: {reminders.count()}")
    
    # Test dashboard view
    print("\n2. Testing dashboard view...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    
    # Create client and login
    client = Client()
    client.force_login(user)
    
    # Test dashboard URL
    response = client.get('/properties/house/rent-reminders/')
    
    if response.status_code == 200:
        print("   ✅ Dashboard loads successfully!")
        print(f"   Status code: {response.status_code}")
        
        # Check if context has data
        context = response.context
        if context:
            print("   ✅ Context data available")
            
            # Check specific context variables
            context_vars = [
                'total_settings', 'total_templates', 'total_reminders',
                'sent_reminders', 'pending_reminders', 'failed_reminders',
                'overdue_reminders', 'upcoming_reminders', 'recent_logs'
            ]
            
            for var in context_vars:
                if var in context:
                    value = context[var]
                    print(f"   {var}: {value}")
                else:
                    print(f"   ⚠️  {var}: Not found in context")
        else:
            print("   ⚠️  No context data")
    else:
        print(f"   ❌ Dashboard failed to load!")
        print(f"   Status code: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   Error: {response.content.decode()[:200]}...")
    
    print("\n3. Testing other URLs...")
    
    # Test other URLs
    urls_to_test = [
        '/properties/house/rent-reminders/list/',
        '/properties/house/rent-reminders/settings/',
        '/properties/house/rent-reminders/templates/',
        '/properties/house/rent-reminders/analytics/',
    ]
    
    for url in urls_to_test:
        response = client.get(url)
        if response.status_code == 200:
            print(f"   ✅ {url} - OK")
        else:
            print(f"   ❌ {url} - Failed ({response.status_code})")
    
    print("\n" + "=" * 50)
    print("RENT REMINDER DASHBOARD TEST COMPLETE")

if __name__ == "__main__":
    test_rent_reminder_dashboard()
