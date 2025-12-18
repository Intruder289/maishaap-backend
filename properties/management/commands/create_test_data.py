from django.core.management.base import BaseCommand
from properties.models import Payment, Booking, Customer, Property, PropertyType
from django.contrib.auth.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test data for payment system testing'

    def handle(self, *args, **options):
        # Get or create test data
        try:
            # Get hotel property type
            hotel_type, created = PropertyType.objects.get_or_create(
                name='hotel',
                defaults={'description': 'Hotel accommodation'}
            )
            
            # Get or create test property
            property_obj, created = Property.objects.get_or_create(
                title='Test Hotel',
                defaults={
                    'property_type': hotel_type,
                    'address': 'Test Address',
                    'rent_amount': Decimal('50.00'),  # Tsh50 per day
                    'description': 'Test hotel for payment testing'
                }
            )
            
            # Get or create test customer
            customer, created = Customer.objects.get_or_create(
                email='john.doe@example.com',
                defaults={
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'phone': '+255123456789'
                }
            )
            
            # Get admin user
            admin_user = User.objects.filter(is_staff=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('No admin user found. Please create an admin user first.'))
                return
            
            # Create test booking
            booking, created = Booking.objects.get_or_create(
                booking_reference='HTL-000001',
                defaults={
                    'property_obj': property_obj,
                    'customer': customer,
                    'check_in_date': '2025-10-24',
                    'check_out_date': '2025-10-26',  # 2 days
                    'number_of_guests': 2,
                    'room_number': '101',
                    'total_amount': Decimal('100.00'),  # 2 days × Tsh50
                    'paid_amount': Decimal('0.00'),
                    'booking_status': 'confirmed',
                    'payment_status': 'pending',
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created test booking: {booking.booking_reference}'))
            else:
                self.stdout.write(f'Test booking already exists: {booking.booking_reference}')
            
            # Show current status
            self.stdout.write('')
            self.stdout.write('Current Test Data:')
            self.stdout.write(f'  Property: {property_obj.title}')
            self.stdout.write(f'  Customer: {customer.full_name} ({customer.email})')
            self.stdout.write(f'  Booking: {booking.booking_reference}')
            self.stdout.write(f'  Total Amount: Tsh{booking.total_amount}')
            self.stdout.write(f'  Paid Amount: Tsh{booking.paid_amount}')
            self.stdout.write(f'  Payment Status: {booking.get_payment_status_display()}')
            self.stdout.write(f'  Current Payments: {Payment.objects.filter(booking=booking).count()}')
            
            self.stdout.write('')
            self.stdout.write('You can now test the payment system with this clean data.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test data: {str(e)}'))
