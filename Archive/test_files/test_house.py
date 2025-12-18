#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, Booking, Room
from django.contrib.auth.models import User
from django.template.loader import render_to_string

def test_house_management():
    print("TESTING HOUSE MANAGEMENT")
    print("=" * 50)
    
    # Test data
    house_properties = Property.objects.filter(property_type__name__iexact='house')
    bookings = Booking.objects.filter(property_obj__property_type__name__iexact='house')
    total_bookings = bookings.count()
    active_bookings = bookings.filter(booking_status__in=['confirmed', 'checked_in']).count()
    revenue = sum(booking.total_amount for booking in bookings.filter(payment_status='paid'))
    
    context = {
        'house_properties': house_properties,
        'selected_property': None,
        'total_houses': house_properties.count(),
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'revenue': revenue,
        'is_single_property_mode': False,
    }
    
    print("House Context data:")
    for key, value in context.items():
        print(f"  {key}: {value}")
    
    # Test template rendering
    try:
        rendered = render_to_string('properties/house_dashboard.html', context)
        print(f"\nHouse template rendered successfully, length: {len(rendered)}")
        
        # Check for specific content
        if "Total Houses" in rendered:
            print("House Template check: 'Total Houses' found")
        else:
            print("House Template check: 'Total Houses' NOT found")
            
        if "Managing: All Houses" in rendered:
            print("House Template check: 'Managing: All Houses' found")
        else:
            print("House Template check: 'Managing: All Houses' NOT found")
            
        if "create_house_booking" in rendered:
            print("House Template check: 'create_house_booking' found")
        else:
            print("House Template check: 'create_house_booking' NOT found")
            
    except Exception as e:
        print(f"House template rendering error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_house_management()
