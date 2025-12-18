#!/usr/bin/env python
"""
Enhanced Automated Rent Reminder System for House Properties
This command extends the existing rent reminder system with house-specific features
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta, datetime
import logging

from properties.models import Property, Booking, Customer, HouseRentReminderSettings, HouseRentReminder, HouseRentReminderTemplate, HouseRentReminderLog, HouseRentReminderSchedule

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Enhanced automated rent payment reminders for house properties'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--property-id',
            type=int,
            help='Process reminders for specific property only'
        )
        parser.add_argument(
            '--reminder-type',
            choices=['email', 'sms', 'push', 'all'],
            default='email',
            help='Type of reminder to send (default: email)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what reminders would be sent without actually sending them'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send reminders even if one was already sent today'
        )
        parser.add_argument(
            '--create-schedules',
            action='store_true',
            help='Create default reminder schedules for all house properties'
        )
        parser.add_argument(
            '--create-templates',
            action='store_true',
            help='Create default reminder templates'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏠 Enhanced House Rent Reminder System')
        )
        self.stdout.write("=" * 60)
        
        # Handle special setup commands
        if options['create_schedules']:
            self.create_default_schedules()
            return
        
        if options['create_templates']:
            self.create_default_templates()
            return
        
        # Main reminder processing
        self.process_rent_reminders(options)
    
    def create_default_schedules(self):
        """Create default reminder schedules for all house properties"""
        self.stdout.write("Creating default reminder schedules...")
        
        house_properties = Property.objects.filter(
            property_type__name__iexact='house'
        )
        
        created_count = 0
        for property_obj in house_properties:
            schedule, created = HouseRentReminderSchedule.objects.get_or_create(
                property_obj=property_obj,
                schedule_name=f"Default Schedule - {property_obj.title}",
                defaults={
                    'schedule_type': 'monthly',
                    'days_before_due': 7,
                    'overdue_interval_days': 3,
                    'max_reminders': 5,
                    'email_enabled': True,
                    'sms_enabled': False,
                    'push_enabled': False,
                    'send_time': datetime.now().time().replace(hour=9, minute=0),
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created schedule for {property_obj.title}")
            else:
                self.stdout.write(f"  - Schedule already exists for {property_obj.title}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} new reminder schedules")
        )
    
    def create_default_templates(self):
        """Create default reminder templates"""
        self.stdout.write("Creating default reminder templates...")
        
        templates = [
            {
                'name': 'Upcoming Payment Email',
                'template_type': 'email',
                'category': 'upcoming',
                'subject': 'Rent Payment Reminder - {{property_title}}',
                'content': '''Dear {{tenant_name}},

This is a friendly reminder that your rent payment for {{property_title}} is due on {{due_date}}.

Payment Details:
- Property: {{property_title}}
- Amount Due: TZS {{amount:,.0f}}
- Due Date: {{due_date}}
- Payment Method: {{payment_method}}

Please ensure your payment is made on time to avoid any late fees.

If you have already made the payment, please disregard this reminder.

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

Payment Details:
- Property: {{property_title}}
- Amount Due: TZS {{amount:,.0f}}
- Due Date: {{due_date}}
- Days Overdue: {{days_overdue}}
- Late Fee: TZS {{late_fee:,.0f}}

Please make your payment as soon as possible to avoid additional late fees.

If you are experiencing financial difficulties, please contact us immediately to discuss payment arrangements.

Best regards,
Property Management Team''',
                'is_default': True,
            },
            {
                'name': 'Final Notice Email',
                'template_type': 'email',
                'category': 'final_notice',
                'subject': 'FINAL NOTICE - Overdue Rent Payment - {{property_title}}',
                'content': '''Dear {{tenant_name}},

This is your FINAL NOTICE regarding your overdue rent payment for {{property_title}}.

Payment Details:
- Property: {{property_title}}
- Amount Due: TZS {{amount:,.0f}}
- Due Date: {{due_date}}
- Days Overdue: {{days_overdue}}
- Late Fee: TZS {{late_fee:,.0f}}
- Total Amount: TZS {{total_amount:,.0f}}

This is your final opportunity to make payment before we proceed with further action.

Please contact us immediately to resolve this matter.

Best regards,
Property Management Team''',
                'is_default': True,
            },
            {
                'name': 'SMS Reminder',
                'template_type': 'sms',
                'category': 'upcoming',
                'subject': '',
                'content': 'Hi {{tenant_name}}, rent for {{property_title}} (TZS {{amount:,.0f}}) due {{due_date}}. Please pay on time to avoid late fees.',
                'is_default': True,
            },
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = HouseRentReminderTemplate.objects.get_or_create(
                template_type=template_data['template_type'],
                category=template_data['category'],
                is_default=True,
                defaults=template_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f"  ✓ Created {template.name}")
            else:
                self.stdout.write(f"  - Template already exists: {template.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} new reminder templates")
        )
    
    def process_rent_reminders(self, options):
        """Main reminder processing logic"""
        today = timezone.now().date()
        reminder_type = options['reminder_type']
        property_id = options.get('property_id')
        
        self.stdout.write(f"Processing rent reminders for {today}")
        self.stdout.write(f"Reminder type: {reminder_type}")
        self.stdout.write("-" * 60)
        
        # Get house properties to process
        if property_id:
            try:
                house_properties = Property.objects.filter(
                    id=property_id,
                    property_type__name__iexact='house'
                )
                if not house_properties.exists():
                    self.stdout.write(
                        self.style.ERROR(f"Property {property_id} not found or not a house")
                    )
                    return
            except Property.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Property {property_id} not found")
                )
                return
        else:
            house_properties = Property.objects.filter(
                property_type__name__iexact='house'
            )
        
        total_processed = 0
        total_sent = 0
        total_failed = 0
        
        for property_obj in house_properties:
            self.stdout.write(f"\nProcessing: {property_obj.title}")
            
            # Get or create reminder settings
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
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(f"  ✓ Created default settings for {property_obj.title}")
            
            # Process reminders for this property
            processed, sent, failed = self.process_property_reminders(
                property_obj, settings_obj, options
            )
            
            total_processed += processed
            total_sent += sent
            total_failed += failed
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN COMPLETE: Would process {total_processed} reminders, "
                    f"{total_sent} would be sent, {total_failed} would fail"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"COMPLETE: Processed {total_processed} reminders, "
                    f"{total_sent} sent, {total_failed} failed"
                )
            )
    
    def process_property_reminders(self, property_obj, settings_obj, options):
        """Process reminders for a specific property"""
        today = timezone.now().date()
        reminder_type = options['reminder_type']
        
        # Get active bookings for this property
        active_bookings = Booking.objects.filter(
            property_obj=property_obj,
            booking_status__in=['confirmed', 'checked_in'],
            payment_status__in=['pending', 'partial']
        ).select_related('customer')
        
        processed = 0
        sent = 0
        failed = 0
        
        for booking in active_bookings:
            # Calculate due date (assuming monthly rent)
            # This is simplified - you'd want more sophisticated logic
            due_date = booking.check_in_date + timedelta(days=30)
            
            # Check if we need to send reminders
            if self.should_send_reminder(booking, due_date, settings_obj, options):
                processed += 1
                
                if options['dry_run']:
                    self.stdout.write(
                        f"  WOULD SEND: Reminder for {booking.customer.first_name} "
                        f"({booking.booking_reference})"
                    )
                    sent += 1
                else:
                    success = self.send_booking_reminder(
                        booking, due_date, settings_obj, reminder_type
                    )
                    if success:
                        sent += 1
                    else:
                        failed += 1
        
        return processed, sent, failed
    
    def should_send_reminder(self, booking, due_date, settings_obj, options):
        """Determine if a reminder should be sent"""
        today = timezone.now().date()
        
        # Check if payment is already complete
        if booking.payment_status == 'paid':
            return False
        
        # Check if we're within reminder window
        days_until_due = (due_date - today).days
        
        # Upcoming reminder
        if days_until_due == settings_obj.days_before_due:
            return True
        
        # Overdue reminders
        if days_until_due < 0:
            days_overdue = abs(days_until_due)
            # Check if we should send overdue reminder
            if days_overdue % settings_obj.overdue_reminder_interval == 0:
                # Check if we haven't exceeded max reminders
                existing_reminders = HouseRentReminder.objects.filter(
                    booking=booking,
                    is_overdue=True
                ).count()
                
                if existing_reminders < settings_obj.max_overdue_reminders:
                    return True
        
        return False
    
    def send_booking_reminder(self, booking, due_date, settings_obj, reminder_type):
        """Send reminder for a specific booking"""
        try:
            # Determine reminder category
            today = timezone.now().date()
            days_until_due = (due_date - today).days
            
            if days_until_due > 0:
                category = 'upcoming'
                is_overdue = False
            elif days_until_due == 0:
                category = 'overdue_1'
                is_overdue = True
            else:
                days_overdue = abs(days_until_due)
                if days_overdue <= 7:
                    category = 'overdue_1'
                elif days_overdue <= 14:
                    category = 'overdue_2'
                else:
                    category = 'final_notice'
                is_overdue = True
            
            # Get template
            template = HouseRentReminderTemplate.objects.filter(
                template_type=reminder_type,
                category=category,
                is_default=True,
                is_active=True
            ).first()
            
            if not template:
                self.stdout.write(
                    f"    ERROR: No template found for {reminder_type} {category}"
                )
                return False
            
            # Prepare context
            context = {
                'tenant_name': booking.customer.first_name or booking.customer.email,
                'property_title': booking.property_obj.title,
                'due_date': due_date.strftime('%B %d, %Y'),
                'amount': booking.total_amount,
                'days_overdue': abs(days_until_due) if is_overdue else 0,
                'late_fee': 0,  # Calculate based on your late fee logic
                'total_amount': booking.total_amount,
                'payment_method': 'Bank Transfer',  # Default or from settings
                'booking_reference': booking.booking_reference,
            }
            
            # Create reminder record
            reminder = HouseRentReminder.objects.create(
                booking=booking,
                customer=booking.customer,
                property_obj=booking.property_obj,
                reminder_type=reminder_type,
                scheduled_date=timezone.now(),
                due_date=due_date,
                days_before_due=days_until_due,
                subject=template.subject,
                message_content=template.render_template(context),
                reminder_sequence=self.get_next_reminder_sequence(booking),
                is_overdue=is_overdue,
                created_by=None,  # System generated
            )
            
            # Send the actual reminder
            success = self.send_reminder_notification(reminder, template, context)
            
            if success:
                reminder.mark_as_sent()
                self.log_reminder_action(reminder, 'sent', 'Reminder sent successfully')
                self.stdout.write(
                    f"    ✓ Sent {reminder_type} reminder to {booking.customer.first_name}"
                )
            else:
                reminder.mark_as_failed('Failed to send notification')
                self.log_reminder_action(reminder, 'failed', 'Failed to send notification')
                self.stdout.write(
                    f"    ✗ Failed to send {reminder_type} reminder to {booking.customer.first_name}"
                )
            
            return success
            
        except Exception as e:
            self.stdout.write(f"    ERROR: Exception sending reminder: {str(e)}")
            logger.error(f"Error sending reminder for booking {booking.id}: {str(e)}")
            return False
    
    def send_reminder_notification(self, reminder, template, context):
        """Send the actual notification"""
        try:
            if reminder.reminder_type == 'email':
                return self.send_email_reminder(reminder, template, context)
            elif reminder.reminder_type == 'sms':
                return self.send_sms_reminder(reminder, template, context)
            elif reminder.reminder_type == 'push':
                return self.send_push_reminder(reminder, template, context)
            else:
                return False
        except Exception as e:
            logger.error(f"Error sending {reminder.reminder_type} reminder: {str(e)}")
            return False
    
    def send_email_reminder(self, reminder, template, context):
        """Send email reminder"""
        try:
            # Check if email is configured
            if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
                self.stdout.write("    WARNING: Email not configured, skipping email reminder")
                return False
            
            subject = template.render_template(context)
            message = reminder.message_content
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reminder.customer.email],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            return False
    
    def send_sms_reminder(self, reminder, template, context):
        """Send SMS reminder"""
        try:
            # This is a placeholder - implement with your SMS service
            # Examples: Twilio, AWS SNS, local SMS gateway, etc.
            
            phone_number = getattr(reminder.customer, 'phone', None)
            if not phone_number:
                self.stdout.write("    WARNING: No phone number for SMS reminder")
                return False
            
            message = template.render_template(context)
            
            # Placeholder SMS sending logic
            self.stdout.write(f"    SMS: Would send to {phone_number}: {message[:50]}...")
            
            # Implement actual SMS sending here
            # sms_service.send_sms(phone_number, message)
            
            return True
            
        except Exception as e:
            logger.error(f"SMS sending error: {str(e)}")
            return False
    
    def send_push_reminder(self, reminder, template, context):
        """Send push notification"""
        try:
            # This is a placeholder - implement with your push notification service
            # Examples: Firebase, OneSignal, etc.
            
            message = template.render_template(context)
            
            # Placeholder push notification logic
            self.stdout.write(f"    PUSH: Would send push notification: {message[:50]}...")
            
            # Implement actual push notification sending here
            # push_service.send_notification(reminder.customer, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Push notification error: {str(e)}")
            return False
    
    def get_next_reminder_sequence(self, booking):
        """Get next reminder sequence number for a booking"""
        last_reminder = HouseRentReminder.objects.filter(
            booking=booking
        ).order_by('-reminder_sequence').first()
        
        if last_reminder:
            return last_reminder.reminder_sequence + 1
        return 1
    
    def log_reminder_action(self, reminder, action, description):
        """Log reminder action"""
        HouseRentReminderLog.objects.create(
            reminder=reminder,
            action=action,
            description=description,
            performed_by=None,  # System action
        )
