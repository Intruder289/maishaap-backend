#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, PropertyType, Booking, Room, Customer, Payment

print("=== HOTEL DATA CHECK ===")
print(f"Hotel Properties: {Property.objects.filter(property_type__name__iexact='hotel').count()}")
print(f"Hotel Bookings: {Booking.objects.filter(property_obj__property_type__name__iexact='hotel').count()}")
print(f"Hotel Rooms: {Room.objects.filter(property_obj__property_type__name__iexact='hotel').count()}")
print(f"Hotel Customers: {Customer.objects.filter(customer_bookings__property_obj__property_type__name__iexact='hotel').distinct().count()}")
print(f"Hotel Payments: {Payment.objects.filter(booking__property_obj__property_type__name__iexact='hotel').count()}")

print("\n=== PROPERTY TYPES ===")
for pt in PropertyType.objects.all():
    print(f"- {pt.name}")

print("\n=== HOTEL PROPERTIES ===")
for prop in Property.objects.filter(property_type__name__iexact='hotel'):
    print(f"- {prop.title} (ID: {prop.id})")

print("\n=== LODGE PROPERTIES ===")
for prop in Property.objects.filter(property_type__name__iexact='lodge'):
    print(f"- {prop.title} (ID: {prop.id})")

print("\n=== VENUE PROPERTIES ===")
for prop in Property.objects.filter(property_type__name__iexact='venue'):
    print(f"- {prop.title} (ID: {prop.id})")

print("\n=== HOUSE PROPERTIES ===")
for prop in Property.objects.filter(property_type__name__iexact='house'):
    print(f"- {prop.title} (ID: {prop.id})")
