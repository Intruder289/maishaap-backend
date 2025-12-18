"""
Management command to create sample data for rent reminder system
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from properties.models import (
    Property, PropertyType, Region, Booking, Customer, 
    HouseRentReminderSettings, HouseRentReminderTemplate, HouseRentReminder
)


class Command(BaseCommand):
    help = 'Create sample data for rent reminder system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing sample data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Clearing existing sample data...")
            HouseRentReminder.objects.all().delete()
            HouseRentReminderSettings.objects.all().delete()
            HouseRentReminderTemplate.objects.all().delete()

        self.stdout.write("Creating sample data for rent reminder system...")

        # Create sample templates
        self.create_templates()
        
        # Create sample settings
        self.create_settings()
        
        # Create sample reminders
        self.create_reminders()

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_templates(self):
        """Create sample reminder templates"""
        templates_data = [
            {
                'name': 'Upcoming Payment Email',
                'template_type': 'email',
                'category': 'upcoming',
                'subject': 'Rent Payment Reminder - {{property_title}}',
                'content': '''Dear {{tenant_name}},

This is a friendly reminder that your rent payment for {{property_title}} is due on {{due_date}}.

Amount Due: Tsh {{amount}}
Due Date: {{due_date}}

Please ensure your payment is made on time to avoid any late fees.

Thank you for your prompt attention to this matter.

Best regards,
Property Management Team''',
                'is_default': True,
            },
            {
                'name': 'First Overdue Email',
                'template_type': 'email',
                'category': 'overdue_1',
                'subject': 'Overdue Rent Payment - {{property_title}}',
                'content': '''Dear {{tenant_name}},

We notice that your rent payment for {{property_title}} is now overdue.

Amount Due: Tsh {{amount}}
Original Due Date: {{due_date}}
Days Overdue: {{days_overdue}}

Please make your payment as soon as possible to avoid additional late fees.

If you have any questions or concerns, please contact us immediately.

Best regards,
Property Management Team''',
                'is_default': True,
            },
            {
                'name': 'SMS Reminder',
                'template_type': 'sms',
                'category': 'upcoming',
                'subject': 'Rent Reminder',
                'content': 'Hi {{tenant_name}}, rent for {{property_title}} (Tsh {{amount}}) is due {{due_date}}. Please pay on time.',
                'is_default': True,
            },
        ]

        for template_data in templates_data:
            template, created = HouseRentReminderTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f"Created template: {template.name}")

    def create_settings(self):
        """Create sample reminder settings for house properties"""
        house_properties = Property.objects.filter(property_type__name__iexact='house')
        
        if not house_properties.exists():
            self.stdout.write(self.style.WARNING("No house properties found. Creating sample house property..."))
            self.create_sample_house_property()
            house_properties = Property.objects.filter(property_type__name__iexact='house')

        for property_obj in house_properties[:3]:  # Limit to first 3 houses
            settings_obj, created = HouseRentReminderSettings.objects.get_or_create(
                property_obj=property_obj,
                defaults={
                    'days_before_due': 7,
                    'overdue_reminder_interval': 3,
                    'max_overdue_reminders': 5,
                    'email_enabled': True,
                    'sms_enabled': False,
                    'push_enabled': False,
                    'grace_period_days': 5,
                    'auto_escalate_enabled': True,
                    'escalation_email': 'manager@example.com',
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f"Created settings for: {property_obj.title}")

    def create_sample_house_property(self):
        """Create a sample house property if none exist"""
        # Get or create property type
        house_type, _ = PropertyType.objects.get_or_create(
            name='House',
            defaults={'description': 'Residential house property'}
        )
        
        # Get or create region
        region, _ = Region.objects.get_or_create(
            name='Dar es Salaam',
            defaults={'description': 'Dar es Salaam region'}
        )
        
        # Create sample house property
        property_obj, created = Property.objects.get_or_create(
            title='Sample House Property',
            defaults={
                'description': 'A sample house property for testing rent reminders',
                'property_type': house_type,
                'region': region,
                'address': '123 Sample Street, Dar es Salaam',
                'rent_amount': Decimal('500000.00'),
                'deposit_amount': Decimal('100000.00'),
                'bedrooms': 3,
                'bathrooms': 2,
                'size_sqft': 1200,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f"Created sample property: {property_obj.title}")

    def create_reminders(self):
        """Create sample reminders"""
        house_properties = Property.objects.filter(property_type__name__iexact='house')
        
        if not house_properties.exists():
            self.stdout.write(self.style.WARNING("No house properties found for creating reminders"))
            return

        # Get or create sample customer
        customer, created = Customer.objects.get_or_create(
            email='tenant@example.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+255123456789',
            }
        )
        
        if created:
            self.stdout.write(f"Created sample customer: {customer.full_name}")

        # Create sample bookings
        for property_obj in house_properties[:2]:  # Limit to first 2 houses
            booking, created = Booking.objects.get_or_create(
                property_obj=property_obj,
                customer=customer,
                defaults={
                    'check_in_date': date.today() - timedelta(days=30),
                    'check_out_date': date.today() + timedelta(days=335),  # 1 year lease
                    'total_amount': property_obj.rent_amount * 12,
                    'status': 'confirmed',
                }
            )
            
            if created:
                self.stdout.write(f"Created sample booking for: {property_obj.title}")

        # Create sample reminders
        today = timezone.now().date()
        
        reminder_data = [
            {
                'booking': Booking.objects.filter(property_obj__property_type__name__iexact='house').first(),
                'customer': customer,
                'property_obj': house_properties.first(),
                'reminder_type': 'email',
                'reminder_status': 'sent',
                'scheduled_date': timezone.now() - timedelta(days=1),
                'sent_date': timezone.now() - timedelta(days=1),
                'due_date': today + timedelta(days=5),
                'days_before_due': 7,
                'subject': 'Rent Payment Reminder - Sample House Property',
                'message_content': 'Your rent payment is due in 5 days.',
                'reminder_sequence': 1,
                'is_overdue': False,
                'delivery_status': 'delivered',
            },
            {
                'booking': Booking.objects.filter(property_obj__property_type__name__iexact='house').first(),
                'customer': customer,
                'property_obj': house_properties.first(),
                'reminder_type': 'email',
                'reminder_status': 'scheduled',
                'scheduled_date': timezone.now() + timedelta(hours=2),
                'due_date': today + timedelta(days=3),
                'days_before_due': 7,
                'subject': 'Rent Payment Reminder - Sample House Property',
                'message_content': 'Your rent payment is due in 3 days.',
                'reminder_sequence': 1,
                'is_overdue': False,
            },
            {
                'booking': Booking.objects.filter(property_obj__property_type__name__iexact='house').first(),
                'customer': customer,
                'property_obj': house_properties.first(),
                'reminder_type': 'email',
                'reminder_status': 'sent',
                'scheduled_date': timezone.now() - timedelta(days=3),
                'sent_date': timezone.now() - timedelta(days=3),
                'due_date': today - timedelta(days=2),
                'days_before_due': -2,
                'subject': 'Overdue Rent Payment - Sample House Property',
                'message_content': 'Your rent payment is 2 days overdue.',
                'reminder_sequence': 1,
                'is_overdue': True,
                'delivery_status': 'delivered',
            },
        ]

        for reminder_info in reminder_data:
            if reminder_info['booking']:  # Only create if booking exists
                reminder, created = HouseRentReminder.objects.get_or_create(
                    booking=reminder_info['booking'],
                    reminder_sequence=reminder_info['reminder_sequence'],
                    defaults=reminder_info
                )
                if created:
                    self.stdout.write(f"Created reminder: {reminder.subject}")

        self.stdout.write("Sample data creation completed!")
