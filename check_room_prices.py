"""
Script to check room prices and identify discrepancies
Run this in Django shell: python manage.py shell < check_room_prices.py
Or copy-paste into Django shell
"""

from properties.models import Booking, Room, Property

# Find the booking HTL-000002
booking = Booking.objects.filter(booking_reference='HTL-000002').first()

if booking:
    print(f"\n=== Booking HTL-000002 ===")
    print(f"Property: {booking.property_obj.title}")
    print(f"Room Number: {booking.room_number}")
    print(f"Check-in: {booking.check_in_date}")
    print(f"Check-out: {booking.check_out_date}")
    print(f"Duration: {booking.duration_days} days")
    print(f"\nStored total_amount: Tsh {booking.total_amount:,.2f}")
    print(f"Calculated total_amount: Tsh {booking.calculated_total_amount:,.2f}")
    
    # Check property rate
    print(f"\nProperty rent_amount: Tsh {booking.property_obj.rent_amount:,.2f}")
    
    # Check room rate if room exists
    if booking.room_number:
        try:
            room = Room.objects.get(property_obj=booking.property_obj, room_number=booking.room_number)
            print(f"\nRoom {room.room_number} ({room.room_type}):")
            print(f"  Room base_rate: Tsh {room.base_rate:,.2f}")
            print(f"  Expected total: Tsh {room.base_rate * booking.duration_days:,.2f}")
        except Room.DoesNotExist:
            print(f"\n⚠️  Room {booking.room_number} not found!")
    
    # Check what base_rate property returns
    print(f"\nBooking.base_rate property: Tsh {booking.base_rate:,.2f}")
    print(f"Expected calculation: {booking.base_rate} × {booking.duration_days} = Tsh {booking.base_rate * booking.duration_days:,.2f}")
else:
    print("Booking HTL-000002 not found!")

# List all rooms for the property
if booking:
    print(f"\n=== All Rooms for {booking.property_obj.title} ===")
    rooms = Room.objects.filter(property_obj=booking.property_obj).order_by('room_number')
    for room in rooms:
        print(f"Room {room.room_number} ({room.room_type}): Tsh {room.base_rate:,.2f}/night")
