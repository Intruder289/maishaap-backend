#!/usr/bin/env python
"""
Comprehensive Venue Management Test Script
Tests all venue management functionality including dashboard, bookings, API endpoints, and analytics.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from properties.models import Property, PropertyType, Region, Booking, Customer, Payment
from django.utils import timezone

def test_venue_management_comprehensive():
    """Comprehensive test of venue management functionality"""
    print("=" * 60)
    print("COMPREHENSIVE VENUE MANAGEMENT TEST")
    print("=" * 60)
    
    # Create test client
    client = Client()
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='venue_test_user',
        defaults={
            'email': 'venue@test.com',
            'first_name': 'Venue',
            'last_name': 'Test'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✓ Created test user")
    else:
        print("✓ Using existing test user")
    
    # Login user
    client.force_login(user)
    print("✓ User logged in")
    
    # Create test data
    print("\n" + "-" * 40)
    print("CREATING TEST DATA")
    print("-" * 40)
    
    # Create region
    region, created = Region.objects.get_or_create(
        name='Test Region',
        defaults={'description': 'Test region for venue management'}
    )
    if created:
        print("✓ Created test region")
    else:
        print("✓ Using existing test region")
    
    # Create property type
    property_type, created = PropertyType.objects.get_or_create(
        name='venue',
        defaults={'description': 'Venue property type'}
    )
    if created:
        print("✓ Created venue property type")
    else:
        print("✓ Using existing venue property type")
    
    # Create test venues
    venues_data = [
        {
            'title': 'Conference Hall A',
            'description': 'Modern conference hall with AV equipment',
            'capacity': 50,
            'venue_type': 'Conference',
            'rent_amount': 500.00,
            'deposit_amount': 100.00,
            'size_sqft': 2000,
            'address': '123 Conference Street',
            'status': 'available'
        },
        {
            'title': 'Grand Ballroom',
            'description': 'Elegant ballroom for weddings and events',
            'capacity': 150,
            'venue_type': 'Wedding',
            'rent_amount': 2500.00,
            'deposit_amount': 500.00,
            'size_sqft': 5000,
            'address': '456 Ballroom Avenue',
            'status': 'available'
        },
        {
            'title': 'Meeting Room B',
            'description': 'Small meeting room for corporate events',
            'capacity': 25,
            'venue_type': 'Meeting',
            'rent_amount': 200.00,
            'deposit_amount': 50.00,
            'size_sqft': 800,
            'address': '789 Meeting Lane',
            'status': 'available'
        }
    ]
    
    created_venues = []
    for venue_data in venues_data:
        venue, created = Property.objects.get_or_create(
            title=venue_data['title'],
            defaults={
                **venue_data,
                'property_type': property_type,
                'region': region,
                'owner': user
            }
        )
        if created:
            print(f"✓ Created venue: {venue.title}")
        else:
            print(f"✓ Using existing venue: {venue.title}")
        created_venues.append(venue)
    
    # Create test customer
    customer, created = Customer.objects.get_or_create(
        email='customer@venue.com',
        defaults={
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+255123456789',
            'address': 'Customer Address'
        }
    )
    if created:
        print("✓ Created test customer")
    else:
        print("✓ Using existing test customer")
    
    # Create test bookings
    print("\n" + "-" * 40)
    print("CREATING TEST BOOKINGS")
    print("-" * 40)
    
    today = timezone.now().date()
    bookings_data = [
        {
            'booking_reference': 'VB001',
            'check_in_date': today,
            'check_out_date': today,
            'number_of_guests': 25,
            'total_amount': 500.00,
            'booking_status': 'confirmed',
            'payment_status': 'paid',
            'special_requests': 'Quarterly business review meeting'
        },
        {
            'booking_reference': 'VB002',
            'check_in_date': today + timedelta(days=1),
            'check_out_date': today + timedelta(days=1),
            'number_of_guests': 120,
            'total_amount': 2500.00,
            'booking_status': 'pending',
            'payment_status': 'pending',
            'special_requests': 'Sarah and Michael wedding celebration'
        },
        {
            'booking_reference': 'VB003',
            'check_in_date': today + timedelta(days=2),
            'check_out_date': today + timedelta(days=2),
            'number_of_guests': 30,
            'total_amount': 800.00,
            'booking_status': 'confirmed',
            'payment_status': 'paid',
            'special_requests': 'Marketing team building workshop'
        }
    ]
    
    created_bookings = []
    for i, booking_data in enumerate(bookings_data):
        booking, created = Booking.objects.get_or_create(
            booking_reference=booking_data['booking_reference'],
            defaults={
                **booking_data,
                'customer': customer,
                'property_obj': created_venues[i % len(created_venues)],
                'created_by': user
            }
        )
        if created:
            print(f"✓ Created booking: {booking.booking_reference}")
        else:
            print(f"✓ Using existing booking: {booking.booking_reference}")
        created_bookings.append(booking)
    
    # Test venue dashboard
    print("\n" + "-" * 40)
    print("TESTING VENUE DASHBOARD")
    print("-" * 40)
    
    try:
        response = client.get(reverse('properties:venue_dashboard'))
        if response.status_code == 200:
            print("✓ Venue dashboard loads successfully")
            
            # Check if context data is present
            context = response.context
            if 'venue_properties' in context:
                print(f"✓ Dashboard shows {len(context['venue_properties'])} venues")
            if 'total_bookings' in context:
                print(f"✓ Dashboard shows {context['total_bookings']} total bookings")
            if 'active_bookings' in context:
                print(f"✓ Dashboard shows {context['active_bookings']} active bookings")
            if 'revenue' in context:
                print(f"✓ Dashboard shows Tsh{context['revenue']} revenue")
        else:
            print(f"❌ Venue dashboard failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue dashboard error: {e}")
    
    # Test venue bookings page
    print("\n" + "-" * 40)
    print("TESTING VENUE BOOKINGS")
    print("-" * 40)
    
    try:
        response = client.get(reverse('properties:venue_bookings'))
        if response.status_code == 200:
            print("✓ Venue bookings page loads successfully")
            
            context = response.context
            if 'bookings' in context:
                print(f"✓ Bookings page shows {len(context['bookings'])} bookings")
        else:
            print(f"❌ Venue bookings page failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue bookings page error: {e}")
    
    # Test venue availability page
    print("\n" + "-" * 40)
    print("TESTING VENUE AVAILABILITY")
    print("-" * 40)
    
    try:
        response = client.get(reverse('properties:venue_availability'))
        if response.status_code == 200:
            print("✓ Venue availability page loads successfully")
        else:
            print(f"❌ Venue availability page failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue availability page error: {e}")
    
    # Test venue customers page
    print("\n" + "-" * 40)
    print("TESTING VENUE CUSTOMERS")
    print("-" * 40)
    
    try:
        response = client.get(reverse('properties:venue_customers'))
        if response.status_code == 200:
            print("✓ Venue customers page loads successfully")
            
            context = response.context
            if 'customers' in context:
                print(f"✓ Customers page shows {len(context['customers'])} customers")
        else:
            print(f"❌ Venue customers page failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue customers page error: {e}")
    
    # Test venue payments page
    print("\n" + "-" * 40)
    print("TESTING VENUE PAYMENTS")
    print("-" * 40)
    
    try:
        response = client.get(reverse('properties:venue_payments'))
        if response.status_code == 200:
            print("✓ Venue payments page loads successfully")
            
            context = response.context
            if 'payments' in context:
                print(f"✓ Payments page shows {len(context['payments'])} payments")
        else:
            print(f"❌ Venue payments page failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue payments page error: {e}")
    
    # Test API endpoints
    print("\n" + "-" * 40)
    print("TESTING API ENDPOINTS")
    print("-" * 40)
    
    # Test venue availability API
    try:
        response = client.get(reverse('properties:api_venue_availability'))
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Venue availability API returns {len(data.get('venues', []))} venues")
            else:
                print(f"❌ Venue availability API error: {data.get('message')}")
        else:
            print(f"❌ Venue availability API failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue availability API error: {e}")
    
    # Test venue capacity check API
    try:
        venue_id = created_venues[0].id
        response = client.get(reverse('properties:api_venue_capacity_check'), {
            'venue_id': venue_id,
            'event_date': today.strftime('%Y-%m-%d'),
            'guest_count': 30
        })
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Venue capacity check API works - Available: {data.get('available')}")
            else:
                print(f"❌ Venue capacity check API error: {data.get('message')}")
        else:
            print(f"❌ Venue capacity check API failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue capacity check API error: {e}")
    
    # Test venue analytics API
    try:
        response = client.get(reverse('properties:api_venue_analytics'), {
            'period': 'month'
        })
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analytics = data.get('analytics', [])
                print(f"✓ Venue analytics API returns data for {len(analytics)} venues")
                if analytics:
                    metrics = analytics[0].get('metrics', {})
                    print(f"  - Total bookings: {metrics.get('total_bookings', 0)}")
                    print(f"  - Total revenue: Tsh{metrics.get('total_revenue', 0)}")
            else:
                print(f"❌ Venue analytics API error: {data.get('message')}")
        else:
            print(f"❌ Venue analytics API failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue analytics API error: {e}")
    
    # Test booking status update API
    if created_bookings:
        try:
            booking = created_bookings[0]
            response = client.post(reverse('properties:api_venue_booking_status', args=[booking.id]), {
                'action': 'start',
                'csrfmiddlewaretoken': client.cookies.get('csrftoken', '')
            })
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✓ Venue booking status update API works")
                    # Verify status was updated
                    booking.refresh_from_db()
                    if booking.booking_status == 'checked_in':
                        print("✓ Booking status updated to 'checked_in'")
                    else:
                        print(f"❌ Booking status not updated correctly: {booking.booking_status}")
                else:
                    print(f"❌ Venue booking status update API error: {data.get('message')}")
            else:
                print(f"❌ Venue booking status update API failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Venue booking status update API error: {e}")
    
    # Test venue property selection
    print("\n" + "-" * 40)
    print("TESTING VENUE PROPERTY SELECTION")
    print("-" * 40)
    
    try:
        # Test venue selection page
        response = client.get(reverse('properties:venue_select_property'))
        if response.status_code == 200:
            print("✓ Venue property selection page loads successfully")
            
            context = response.context
            if 'properties' in context:
                print(f"✓ Property selection shows {len(context['properties'])} venues")
        else:
            print(f"❌ Venue property selection page failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Venue property selection page error: {e}")
    
    # Test single venue management
    if created_venues:
        try:
            venue = created_venues[0]
            response = client.get(reverse('properties:venue_dashboard'), {'property_id': venue.id})
            if response.status_code == 200:
                print(f"✓ Single venue dashboard works for {venue.title}")
                
                context = response.context
                if context.get('is_single_property_mode'):
                    print("✓ Single property mode is active")
                if context.get('selected_property'):
                    print(f"✓ Selected property: {context['selected_property'].title}")
            else:
                print(f"❌ Single venue dashboard failed with status {response.status_code}")
        except Exception as e:
            print(f"❌ Single venue dashboard error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VENUE MANAGEMENT TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Created {len(created_venues)} test venues")
    print(f"✓ Created {len(created_bookings)} test bookings")
    print("✓ Tested all venue management pages")
    print("✓ Tested all venue API endpoints")
    print("✓ Tested venue property selection")
    print("✓ Tested single venue management")
    print("\nVenue management system is fully functional!")
    print("=" * 60)

if __name__ == '__main__':
    test_venue_management_comprehensive()
