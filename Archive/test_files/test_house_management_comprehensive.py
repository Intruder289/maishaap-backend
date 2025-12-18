#!/usr/bin/env python
"""
Comprehensive House Management Test Script
Creates sample data for testing all House Management features
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from properties.models import Property, PropertyType, Region, Booking, Customer, Payment
# from accounts.models import UserProfile  # Not needed for this test

def create_test_data():
    print("🏠 Creating comprehensive House Management test data...")
    
    # Create or get admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@maisha.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Created admin user")
    else:
        print("✅ Admin user already exists")
    
    # Create Property Type
    house_type, created = PropertyType.objects.get_or_create(
        name='house',
        defaults={'description': 'Residential house properties'}
    )
    if created:
        print("✅ Created house property type")
    
    # Create Regions
    regions_data = [
        {'name': 'Dar es Salaam', 'description': 'Commercial capital'},
        {'name': 'Arusha', 'description': 'Northern region'},
        {'name': 'Mwanza', 'description': 'Lake region'},
        {'name': 'Dodoma', 'description': 'Capital city'},
        {'name': 'Tanga', 'description': 'Coastal region'},
    ]
    
    regions = {}
    for region_data in regions_data:
        region, created = Region.objects.get_or_create(
            name=region_data['name'],
            defaults={'description': region_data['description']}
        )
        regions[region_data['name']] = region
        if created:
            print(f"✅ Created region: {region_data['name']}")
    
    # Create House Properties with different characteristics
    houses_data = [
        {
            'title': 'Luxury Villa - Oyster Bay',
            'address': 'Oyster Bay, Dar es Salaam',
            'region': regions['Dar es Salaam'],
            'rent_amount': 2500000,
            'bedrooms': 4,
            'bathrooms': 3,
            'size_sqft': 2500,
            'description': 'Modern luxury villa with ocean view',
            'status': 'available'
        },
        {
            'title': 'Family House - Kinondoni',
            'address': 'Kinondoni, Dar es Salaam',
            'region': regions['Dar es Salaam'],
            'rent_amount': 1200000,
            'bedrooms': 3,
            'bathrooms': 2,
            'size_sqft': 1800,
            'description': 'Spacious family home in quiet neighborhood',
            'status': 'occupied'
        },
        {
            'title': 'Budget Apartment - Temeke',
            'address': 'Temeke, Dar es Salaam',
            'region': regions['Dar es Salaam'],
            'rent_amount': 600000,
            'bedrooms': 2,
            'bathrooms': 1,
            'size_sqft': 800,
            'description': 'Affordable apartment for young professionals',
            'status': 'occupied'
        },
        {
            'title': 'Executive House - Arusha CBD',
            'address': 'Central Business District, Arusha',
            'region': regions['Arusha'],
            'rent_amount': 1800000,
            'bedrooms': 3,
            'bathrooms': 2,
            'size_sqft': 2000,
            'description': 'Executive house near business district',
            'status': 'available'
        },
        {
            'title': 'Student House - Mwanza',
            'address': 'Nyamagana, Mwanza',
            'region': regions['Mwanza'],
            'rent_amount': 400000,
            'bedrooms': 2,
            'bathrooms': 1,
            'size_sqft': 600,
            'description': 'Student-friendly house near university',
            'status': 'occupied'
        },
        {
            'title': 'Government House - Dodoma',
            'address': 'Dodoma City Center',
            'region': regions['Dodoma'],
            'rent_amount': 800000,
            'bedrooms': 3,
            'bathrooms': 2,
            'size_sqft': 1500,
            'description': 'Government employee housing',
            'status': 'available'
        },
        {
            'title': 'Beach House - Tanga',
            'address': 'Tanga Beachfront',
            'region': regions['Tanga'],
            'rent_amount': 1500000,
            'bedrooms': 3,
            'bathrooms': 2,
            'size_sqft': 2200,
            'description': 'Beachfront property with garden',
            'status': 'occupied'
        },
        {
            'title': 'Modern Duplex - Masaki',
            'address': 'Masaki, Dar es Salaam',
            'region': regions['Dar es Salaam'],
            'rent_amount': 2000000,
            'bedrooms': 4,
            'bathrooms': 3,
            'size_sqft': 2800,
            'description': 'Modern duplex with swimming pool',
            'status': 'available'
        }
    ]
    
    houses = []
    for house_data in houses_data:
        house, created = Property.objects.get_or_create(
            title=house_data['title'],
            defaults={
                'address': house_data['address'],
                'property_type': house_type,
                'region': house_data['region'],
                'rent_amount': house_data['rent_amount'],
                'bedrooms': house_data['bedrooms'],
                'bathrooms': house_data['bathrooms'],
                'size_sqft': house_data['size_sqft'],
                'description': house_data['description'],
                'status': house_data['status'],
                'owner': admin_user
            }
        )
        houses.append(house)
        if created:
            print(f"✅ Created house: {house_data['title']}")
    
    # Create Customers/Tenants with different characteristics
    tenants_data = [
        {
            'first_name': 'John',
            'last_name': 'Mwalimu',
            'email': 'john.mwalimu@email.com',
            'phone': '+255712345678',
            'type': 'employed',
            'income_level': 'high'
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Kimaro',
            'email': 'sarah.kimaro@email.com',
            'phone': '+255723456789',
            'type': 'family',
            'income_level': 'medium'
        },
        {
            'first_name': 'Ahmed',
            'last_name': 'Hassan',
            'email': 'ahmed.hassan@email.com',
            'phone': '+255734567890',
            'type': 'student',
            'income_level': 'low'
        },
        {
            'first_name': 'Grace',
            'last_name': 'Mwangi',
            'email': 'grace.mwangi@email.com',
            'phone': '+255745678901',
            'type': 'employed',
            'income_level': 'high'
        },
        {
            'first_name': 'Peter',
            'last_name': 'Mwamba',
            'email': 'peter.mwamba@email.com',
            'phone': '+255756789012',
            'type': 'family',
            'income_level': 'medium'
        },
        {
            'first_name': 'Fatuma',
            'last_name': 'Ali',
            'email': 'fatuma.ali@email.com',
            'phone': '+255767890123',
            'type': 'employed',
            'income_level': 'medium'
        },
        {
            'first_name': 'David',
            'last_name': 'Mwangi',
            'email': 'david.mwangi@email.com',
            'phone': '+255778901234',
            'type': 'family',
            'income_level': 'high'
        }
    ]
    
    tenants = []
    for tenant_data in tenants_data:
        tenant, created = Customer.objects.get_or_create(
            email=tenant_data['email'],
            defaults={
                'first_name': tenant_data['first_name'],
                'last_name': tenant_data['last_name'],
                'phone': tenant_data['phone']
            }
        )
        tenants.append(tenant)
        if created:
            print(f"✅ Created tenant: {tenant_data['first_name']} {tenant_data['last_name']}")
    
    # Create Bookings with different statuses and characteristics
    bookings_data = [
        {
            'customer': tenants[0],  # John Mwalimu
            'property': houses[1],   # Family House - Kinondoni
            'check_in_date': datetime.now() - timedelta(days=30),
            'check_out_date': datetime.now() + timedelta(days=335),
            'booking_status': 'checked_in',
            'payment_status': 'paid',
            'total_amount': 1200000,
            'duration_days': 365
        },
        {
            'customer': tenants[1],  # Sarah Kimaro
            'property': houses[2],   # Budget Apartment - Temeke
            'check_in_date': datetime.now() - timedelta(days=15),
            'check_out_date': datetime.now() + timedelta(days=350),
            'booking_status': 'confirmed',
            'payment_status': 'partial',
            'total_amount': 600000,
            'duration_days': 365
        },
        {
            'customer': tenants[2],  # Ahmed Hassan
            'property': houses[4],   # Student House - Mwanza
            'check_in_date': datetime.now() - timedelta(days=60),
            'check_out_date': datetime.now() + timedelta(days=305),
            'booking_status': 'checked_in',
            'payment_status': 'overdue',
            'total_amount': 400000,
            'duration_days': 365
        },
        {
            'customer': tenants[3],  # Grace Mwangi
            'property': houses[6],   # Beach House - Tanga
            'check_in_date': datetime.now() - timedelta(days=45),
            'check_out_date': datetime.now() + timedelta(days=320),
            'booking_status': 'checked_in',
            'payment_status': 'paid',
            'total_amount': 1500000,
            'duration_days': 365
        },
        {
            'customer': tenants[4],  # Peter Mwamba
            'property': houses[1],   # Family House - Kinondoni (previous booking ended)
            'check_in_date': datetime.now() - timedelta(days=5),
            'check_out_date': datetime.now() + timedelta(days=360),
            'booking_status': 'pending',
            'payment_status': 'pending',
            'total_amount': 1200000,
            'duration_days': 365
        },
        {
            'customer': tenants[5],  # Fatuma Ali
            'property': houses[2],   # Budget Apartment - Temeke (previous booking ended)
            'check_in_date': datetime.now() - timedelta(days=10),
            'check_out_date': datetime.now() + timedelta(days=355),
            'booking_status': 'confirmed',
            'payment_status': 'paid',
            'total_amount': 600000,
            'duration_days': 365
        },
        {
            'customer': tenants[6],  # David Mwangi
            'property': houses[4],   # Student House - Mwanza (previous booking ended)
            'check_in_date': datetime.now() - timedelta(days=20),
            'check_out_date': datetime.now() + timedelta(days=345),
            'booking_status': 'checked_out',
            'payment_status': 'paid',
            'total_amount': 400000,
            'duration_days': 365
        }
    ]
    
    bookings = []
    for booking_data in bookings_data:
        booking, created = Booking.objects.get_or_create(
            customer=booking_data['customer'],
            property_obj=booking_data['property'],
            check_in_date=booking_data['check_in_date'],
            defaults={
                'booking_reference': f"BK{booking_data['customer'].id:03d}{booking_data['property'].id:03d}",
                'check_out_date': booking_data['check_out_date'],
                'booking_status': booking_data['booking_status'],
                'payment_status': booking_data['payment_status'],
                'total_amount': booking_data['total_amount'],
                'created_by': admin_user
            }
        )
        bookings.append(booking)
        if created:
            print(f"✅ Created booking for {booking_data['customer'].first_name} {booking_data['customer'].last_name}")
    
    # Create Payments with different statuses and amounts
    payments_data = [
        # John Mwalimu - Paid tenant
        {
            'booking': bookings[0],
            'amount': 1200000,
            'payment_type': 'rent',
            'payment_method': 'bank_transfer',
            'payment_date': datetime.now() - timedelta(days=25),
            'status': 'completed',
            'description': 'Monthly rent payment'
        },
        {
            'booking': bookings[0],
            'amount': 2400000,
            'payment_type': 'deposit',
            'payment_method': 'bank_transfer',
            'payment_date': datetime.now() - timedelta(days=30),
            'status': 'completed',
            'description': 'Security deposit'
        },
        
        # Sarah Kimaro - Partial payment
        {
            'booking': bookings[1],
            'amount': 300000,
            'payment_type': 'rent',
            'payment_method': 'mobile_money',
            'payment_date': datetime.now() - timedelta(days=10),
            'status': 'completed',
            'description': 'Partial rent payment'
        },
        {
            'booking': bookings[1],
            'amount': 1200000,
            'payment_type': 'deposit',
            'payment_method': 'cash',
            'payment_date': datetime.now() - timedelta(days=15),
            'status': 'completed',
            'description': 'Security deposit'
        },
        
        # Ahmed Hassan - Overdue payments
        {
            'booking': bookings[2],
            'amount': 400000,
            'payment_type': 'rent',
            'payment_method': 'mobile_money',
            'payment_date': datetime.now() - timedelta(days=45),
            'status': 'completed',
            'description': 'Last month rent'
        },
        {
            'booking': bookings[2],
            'amount': 50000,
            'payment_type': 'late_fee',
            'payment_method': 'cash',
            'payment_date': None,
            'status': 'overdue',
            'description': 'Late payment fee'
        },
        
        # Grace Mwangi - Paid tenant
        {
            'booking': bookings[3],
            'amount': 1500000,
            'payment_type': 'rent',
            'payment_method': 'bank_transfer',
            'payment_date': datetime.now() - timedelta(days=20),
            'status': 'completed',
            'description': 'Monthly rent payment'
        },
        {
            'booking': bookings[3],
            'amount': 3000000,
            'payment_type': 'deposit',
            'payment_method': 'bank_transfer',
            'payment_date': datetime.now() - timedelta(days=45),
            'status': 'completed',
            'description': 'Security deposit'
        },
        
        # Peter Mwamba - Pending payment
        {
            'booking': bookings[4],
            'amount': 1200000,
            'payment_type': 'rent',
            'payment_method': 'bank_transfer',
            'payment_date': None,
            'status': 'pending',
            'description': 'Monthly rent payment'
        },
        
        # Fatuma Ali - Paid tenant
        {
            'booking': bookings[5],
            'amount': 600000,
            'payment_type': 'rent',
            'payment_method': 'mobile_money',
            'payment_date': datetime.now() - timedelta(days=5),
            'status': 'completed',
            'description': 'Monthly rent payment'
        },
        {
            'booking': bookings[5],
            'amount': 1200000,
            'payment_type': 'deposit',
            'payment_method': 'cash',
            'payment_date': datetime.now() - timedelta(days=10),
            'status': 'completed',
            'description': 'Security deposit'
        },
        
        # David Mwangi - Completed payments (checked out)
        {
            'booking': bookings[6],
            'amount': 400000,
            'payment_type': 'rent',
            'payment_method': 'mobile_money',
            'payment_date': datetime.now() - timedelta(days=30),
            'status': 'completed',
            'description': 'Final rent payment'
        },
        {
            'booking': bookings[6],
            'amount': 800000,
            'payment_type': 'deposit',
            'payment_method': 'cash',
            'payment_date': datetime.now() - timedelta(days=20),
            'status': 'completed',
            'description': 'Security deposit refund'
        }
    ]
    
    payments = []
    for payment_data in payments_data:
        payment, created = Payment.objects.get_or_create(
            booking=payment_data['booking'],
            payment_type=payment_data['payment_type'],
            amount=payment_data['amount'],
            defaults={
                'payment_method': payment_data['payment_method'],
                'payment_date': payment_data['payment_date'] or datetime.now(),
                'status': payment_data['status'],
                'notes': payment_data['description'],
                'recorded_by': admin_user
            }
        )
        payments.append(payment)
        if created:
            print(f"✅ Created payment: {payment_data['amount']} Tsh for {payment_data['booking'].customer.first_name} {payment_data['booking'].customer.last_name}")
    
    print("\n🎉 Test data creation completed!")
    print(f"📊 Summary:")
    print(f"   • Houses: {len(houses)}")
    print(f"   • Tenants: {len(tenants)}")
    print(f"   • Bookings: {len(bookings)}")
    print(f"   • Payments: {len(payments)}")
    
    return {
        'houses': houses,
        'tenants': tenants,
        'bookings': bookings,
        'payments': payments
    }

def test_house_management_features():
    """Test all House Management features"""
    print("\n🧪 Testing House Management Features...")
    
    # Test Dashboard
    print("\n1️⃣ Testing Dashboard...")
    from properties.views import house_dashboard
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get('/properties/house/dashboard/')
    request.user = User.objects.get(username='admin')
    
    try:
        response = house_dashboard(request)
        print("✅ Dashboard view works")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # Test Bookings
    print("\n2️⃣ Testing Bookings...")
    from properties.views import house_bookings
    
    request = factory.get('/properties/house/bookings/')
    request.user = User.objects.get(username='admin')
    
    try:
        response = house_bookings(request)
        print("✅ Bookings view works")
    except Exception as e:
        print(f"❌ Bookings error: {e}")
    
    # Test Tenants
    print("\n3️⃣ Testing Tenants...")
    from properties.views import house_tenants
    
    request = factory.get('/properties/house/tenants/')
    request.user = User.objects.get(username='admin')
    
    try:
        response = house_tenants(request)
        print("✅ Tenants view works")
    except Exception as e:
        print(f"❌ Tenants error: {e}")
    
    # Test Payments
    print("\n4️⃣ Testing Payments...")
    from properties.views import house_payments
    
    request = factory.get('/properties/house/payments/')
    request.user = User.objects.get(username='admin')
    
    try:
        response = house_payments(request)
        print("✅ Payments view works")
    except Exception as e:
        print(f"❌ Payments error: {e}")
    
    # Test Reports
    print("\n5️⃣ Testing Reports...")
    from properties.views import house_reports
    
    request = factory.get('/properties/house/reports/')
    request.user = User.objects.get(username='admin')
    
    try:
        response = house_reports(request)
        print("✅ Reports view works")
    except Exception as e:
        print(f"❌ Reports error: {e}")
    
    print("\n🎯 All House Management features tested!")

if __name__ == '__main__':
    # Create test data
    test_data = create_test_data()
    
    # Test all features
    test_house_management_features()
    
    print("\n🚀 Ready to test House Management!")
    print("Visit: http://127.0.0.1:8001/properties/house/dashboard/")
    print("Login with: admin / admin123")
