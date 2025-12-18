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

def test_lodge_management():
    print("TESTING LODGE MANAGEMENT")
    print("=" * 50)
    
    # Test data
    lodge_properties = Property.objects.filter(property_type__name__iexact='lodge')
    total_rooms = sum(prop.total_rooms or 0 for prop in lodge_properties)
    bookings = Booking.objects.filter(property_obj__property_type__name__iexact='lodge')
    total_bookings = bookings.count()
    active_bookings = bookings.filter(booking_status__in=['confirmed', 'checked_in']).count()
    revenue = sum(booking.total_amount for booking in bookings.filter(payment_status='paid'))
    
    context = {
        'lodge_properties': lodge_properties,
        'selected_property': None,
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'revenue': revenue,
        'is_single_property_mode': False,
    }
    
    print("Lodge Context data:")
    for key, value in context.items():
        print(f"  {key}: {value}")
    
    # Test template rendering
    try:
        rendered = render_to_string('properties/lodge_dashboard.html', context)
        print(f"\nLodge template rendered successfully, length: {len(rendered)}")
        
        # Check for specific content
        if "Total Rooms" in rendered:
            print("Lodge Template check: 'Total Rooms' found")
        else:
            print("Lodge Template check: 'Total Rooms' NOT found")
            
        if "Managing: All Lodges" in rendered:
            print("Lodge Template check: 'Managing: All Lodges' found")
        else:
            print("Lodge Template check: 'Managing: All Lodges' NOT found")
            
        if "create_lodge_booking" in rendered:
            print("Lodge Template check: 'create_lodge_booking' found")
        else:
            print("Lodge Template check: 'create_lodge_booking' NOT found")
            
        if "add_lodge_room" in rendered:
            print("Lodge Template check: 'add_lodge_room' found")
        else:
            print("Lodge Template check: 'add_lodge_room' NOT found")
            
    except Exception as e:
        print(f"Lodge template rendering error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_lodge_management()
