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

def test_venue_management():
    print("TESTING VENUE MANAGEMENT")
    print("=" * 50)
    
    # Test data
    venue_properties = Property.objects.filter(property_type__name__iexact='venue')
    bookings = Booking.objects.filter(property_obj__property_type__name__iexact='venue')
    total_bookings = bookings.count()
    active_bookings = bookings.filter(booking_status__in=['confirmed', 'checked_in']).count()
    revenue = sum(booking.total_amount for booking in bookings.filter(payment_status='paid'))
    
    context = {
        'venue_properties': venue_properties,
        'selected_property': None,
        'total_venues': venue_properties.count(),
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'revenue': revenue,
        'is_single_property_mode': False,
    }
    
    print("Venue Context data:")
    for key, value in context.items():
        print(f"  {key}: {value}")
    
    # Test template rendering
    try:
        rendered = render_to_string('properties/venue_dashboard.html', context)
        print(f"\nVenue template rendered successfully, length: {len(rendered)}")
        
        # Check for specific content
        if "Total Venues" in rendered:
            print("Venue Template check: 'Total Venues' found")
        else:
            print("Venue Template check: 'Total Venues' NOT found")
            
        if "Managing: All Venues" in rendered:
            print("Venue Template check: 'Managing: All Venues' found")
        else:
            print("Venue Template check: 'Managing: All Venues' NOT found")
            
        if "create_venue_booking" in rendered:
            print("Venue Template check: 'create_venue_booking' found")
        else:
            print("Venue Template check: 'create_venue_booking' NOT found")
            
    except Exception as e:
        print(f"Venue template rendering error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_venue_management()
