#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, Booking, Room
from django.contrib.auth.models import User
from django.test import Client
from django.template.loader import render_to_string
from django.template import Context, Template

def test_template_rendering():
    print("TESTING TEMPLATE RENDERING")
    print("=" * 50)
    
    # Test data
    hotel_properties = Property.objects.filter(property_type__name__iexact='hotel')
    total_rooms = sum(prop.total_rooms or 0 for prop in hotel_properties)
    bookings = Booking.objects.filter(property_obj__property_type__name__iexact='hotel')
    total_bookings = bookings.count()
    active_bookings = bookings.filter(booking_status__in=['confirmed', 'checked_in']).count()
    revenue = sum(booking.total_amount for booking in bookings.filter(payment_status='paid'))
    
    context = {
        'hotel_properties': hotel_properties,
        'selected_property': None,
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'revenue': revenue,
        'is_single_property_mode': False,
    }
    
    print("Context data:")
    for key, value in context.items():
        print(f"  {key}: {value}")
    
    # Test template rendering
    try:
        rendered = render_to_string('properties/hotel_dashboard.html', context)
        print(f"\nTemplate rendered successfully, length: {len(rendered)}")
        
        # Check for specific content
        if "Total Rooms" in rendered:
            print("Template check: 'Total Rooms' found")
        else:
            print("Template check: 'Total Rooms' NOT found")
            
        if "Managing: All Hotels" in rendered:
            print("Template check: 'Managing: All Hotels' found")
        else:
            print("Template check: 'Managing: All Hotels' NOT found")
            
        if "create_hotel_booking" in rendered:
            print("Template check: 'create_hotel_booking' found")
        else:
            print("Template check: 'create_hotel_booking' NOT found")
            
    except Exception as e:
        print(f"Template rendering error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_rendering()
