from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date


class Command(BaseCommand):
    help = 'Populate sample data for dashboard testing'

    def handle(self, *args, **options):
        # Create test users if they don't exist
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created admin user')

        try:
            test_user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            test_user = User.objects.create_user('testuser', 'test@example.com', 'test123')
            self.stdout.write('Created test user')

        # Create sample data
        sample_count = 0

        try:
            from properties.models import Property, Region, PropertyType
            
            # Create region if needed
            region, created = Region.objects.get_or_create(
                name='Dar es Salaam',
                defaults={'description': 'Main city region'}
            )
            
            # Create property type if needed
            property_type, created = PropertyType.objects.get_or_create(
                name='Apartment',
                defaults={'description': 'Residential apartment'}
            )
            
            # Create sample properties
            if Property.objects.count() < 5:
                for i in range(3):
                    Property.objects.create(
                        title=f'Sample Property {i+1}',
                        description=f'Beautiful property in Dar es Salaam {i+1}',
                        property_type=property_type,
                        region=region,
                        address=f'Sample Address {i+1}',
                        bedrooms=2 + i,
                        bathrooms=1 + i,
                        size_sqft=800 + (i * 200),
                        rent_amount=Decimal('1200000.00') + (Decimal('200000.00') * i),
                        deposit_amount=Decimal('600000.00') + (Decimal('100000.00') * i),
                        owner=admin_user,
                        status='available'
                    )
                    sample_count += 1
                self.stdout.write(f'Created {sample_count} sample properties')
        except ImportError:
            pass

        try:
            from documents.models import Lease
            from properties.models import Property
            
            properties = Property.objects.all()[:2]
            
            # Create sample leases
            if Lease.objects.count() < 2 and properties:
                for i, prop in enumerate(properties):
                    Lease.objects.create(
                        property_ref=prop,
                        tenant=test_user,
                        start_date=date.today() - timedelta(days=30),
                        end_date=date.today() + timedelta(days=335),
                        rent_amount=prop.rent_amount,
                        status='active'
                    )
                    sample_count += 1
                self.stdout.write(f'Created {len(properties)} sample leases')
        except ImportError:
            pass

        try:
            from documents.models import Booking
            from properties.models import Property
            
            properties = Property.objects.all()[:1]
            
            # Create sample bookings
            if Booking.objects.count() < 2 and properties:
                prop = properties[0]
                Booking.objects.create(
                    property_ref=prop,
                    tenant=test_user,
                    check_in=date.today() + timedelta(days=7),
                    check_out=date.today() + timedelta(days=10),
                    total_amount=Decimal('450000.00'),
                    status='pending'
                )
                sample_count += 1
                self.stdout.write('Created 1 sample booking')
        except ImportError:
            pass

        try:
            from payments.models import Invoice, Payment
            
            # Create sample invoices
            if Invoice.objects.count() < 3:
                for i in range(2):
                    invoice = Invoice.objects.create(
                        tenant=test_user,
                        amount=Decimal('1200000.00') + (Decimal('100000.00') * i),
                        due_date=date.today() + timedelta(days=30 + i*7),
                        status='unpaid' if i == 0 else 'paid'
                    )
                    
                    # Create payment for paid invoice
                    if invoice.status == 'paid':
                        Payment.objects.create(
                            invoice=invoice,
                            tenant=test_user,
                            amount=invoice.amount,
                            paid_date=date.today() - timedelta(days=5),
                            status='successful'
                        )
                    sample_count += 1
                self.stdout.write('Created sample invoices and payments')
        except ImportError:
            pass

        try:
            from maintenance.models import MaintenanceRequest
            from properties.models import Property
            
            properties = Property.objects.all()[:1]
            
            # Create sample maintenance requests
            if MaintenanceRequest.objects.count() < 2 and properties:
                MaintenanceRequest.objects.create(
                    property=properties[0],
                    tenant=test_user,
                    title='Kitchen faucet leak',
                    description='The kitchen faucet is leaking and needs repair'
                )
                sample_count += 1
                self.stdout.write('Created 1 sample maintenance request')
        except ImportError:
            pass

        try:
            from complaints.models import Complaint
            
            # Create sample complaints (use model fields: title, description, status)
            if Complaint.objects.count() < 2:
                Complaint.objects.create(
                    user=test_user,
                    title='Noise complaint',
                    description='Too much noise from neighbors',
                    priority='medium',
                    # Complaint model uses 'pending', 'in_progress', 'resolved', 'closed', 'rejected'
                    status='pending'
                )
                sample_count += 1
                self.stdout.write('Created 1 sample complaint')
        except ImportError:
            pass

        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated sample data! Created {sample_count} items.')
        )
        self.stdout.write('Dashboard should now show realistic data.')
        self.stdout.write('Test credentials: admin/admin123 or testuser/test123')