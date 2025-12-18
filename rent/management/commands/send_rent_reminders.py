from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from rent.models import RentInvoice, RentReminder


class Command(BaseCommand):
    help = 'Send rent payment reminders to tenants'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            type=int,
            default=3,
            help='Send reminders N days before due date (default: 3)'
        )
        parser.add_argument(
            '--overdue-days',
            type=int,
            default=1,
            help='Send overdue reminders N days after due date (default: 1)'
        )
        parser.add_argument(
            '--reminder-type',
            choices=['email', 'sms', 'push'],
            default='email',
            help='Type of reminder to send (default: email)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what reminders would be sent without actually sending them.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Send reminders even if one was already sent today.'
        )
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        reminder_type = options['reminder_type']
        days_before = options['days_before']
        overdue_days = options['overdue_days']
        
        self.stdout.write(f"Processing rent payment reminders for {today}")
        self.stdout.write(f"Reminder type: {reminder_type}")
        self.stdout.write("-" * 50)
        
        # Find invoices that need reminders
        upcoming_due_date = today + timedelta(days=days_before)
        overdue_date = today - timedelta(days=overdue_days)
        
        # Upcoming due reminders
        upcoming_invoices = RentInvoice.objects.filter(
            due_date=upcoming_due_date,
            status__in=['draft', 'sent'],
            total_amount__gt=0
        ).select_related('tenant', 'lease__property_ref')
        
        # Overdue reminders
        overdue_invoices = RentInvoice.objects.filter(
            due_date=overdue_date,
            status__in=['sent', 'overdue'],
            total_amount__gt=0
        ).select_related('tenant', 'lease__property_ref')
        
        self.stdout.write(f"Found {upcoming_invoices.count()} invoices due in {days_before} days")
        self.stdout.write(f"Found {overdue_invoices.count()} invoices {overdue_days} days overdue")
        
        sent_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process upcoming due reminders
        for invoice in upcoming_invoices:
            try:
                # Check if reminder already sent today
                if not options['force']:
                    existing_reminder = RentReminder.objects.filter(
                        invoice=invoice,
                        reminder_type=reminder_type,
                        days_before_due=days_before,
                        sent_at__date=today
                    ).exists()
                    
                    if existing_reminder:
                        self.stdout.write(f"  SKIP: Reminder already sent today for {invoice.invoice_number}")
                        skipped_count += 1
                        continue
                
                if options['dry_run']:
                    self.stdout.write(f"  WOULD SEND: Due reminder to {invoice.tenant.get_full_name() or invoice.tenant.username} for {invoice.invoice_number}")
                    sent_count += 1
                    continue
                
                # Send reminder (implement your notification logic here)
                success = self.send_reminder(invoice, reminder_type, days_before, is_overdue=False)
                
                # Record the reminder
                RentReminder.objects.create(
                    invoice=invoice,
                    tenant=invoice.tenant,
                    reminder_type=reminder_type,
                    days_before_due=days_before,
                    is_successful=success
                )
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  SENT: Due reminder to {invoice.tenant.get_full_name() or invoice.tenant.username} "
                            f"for {invoice.invoice_number} (${invoice.balance_due})"
                        )
                    )
                    sent_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ERROR: Failed to send reminder to {invoice.tenant.get_full_name() or invoice.tenant.username} "
                            f"for {invoice.invoice_number}"
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR: Exception for {invoice.invoice_number}: {str(e)}")
                )
                error_count += 1
        
        # Process overdue reminders
        for invoice in overdue_invoices:
            try:
                # Check if reminder already sent today
                if not options['force']:
                    existing_reminder = RentReminder.objects.filter(
                        invoice=invoice,
                        reminder_type=reminder_type,
                        days_before_due=-overdue_days,
                        sent_at__date=today
                    ).exists()
                    
                    if existing_reminder:
                        self.stdout.write(f"  SKIP: Overdue reminder already sent today for {invoice.invoice_number}")
                        skipped_count += 1
                        continue
                
                if options['dry_run']:
                    self.stdout.write(f"  WOULD SEND: Overdue reminder to {invoice.tenant.get_full_name() or invoice.tenant.username} for {invoice.invoice_number}")
                    sent_count += 1
                    continue
                
                # Update invoice status to overdue if not already
                if invoice.status != 'overdue':
                    invoice.status = 'overdue'
                    invoice.save()
                
                # Send overdue reminder
                success = self.send_reminder(invoice, reminder_type, -overdue_days, is_overdue=True)
                
                # Record the reminder
                RentReminder.objects.create(
                    invoice=invoice,
                    tenant=invoice.tenant,
                    reminder_type=reminder_type,
                    days_before_due=-overdue_days,
                    is_successful=success
                )
                
                if success:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  SENT: Overdue reminder to {invoice.tenant.get_full_name() or invoice.tenant.username} "
                            f"for {invoice.invoice_number} (${invoice.balance_due}) - {invoice.days_overdue} days overdue"
                        )
                    )
                    sent_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ERROR: Failed to send overdue reminder to {invoice.tenant.get_full_name() or invoice.tenant.username} "
                            f"for {invoice.invoice_number}"
                        )
                    )
                    error_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR: Exception for {invoice.invoice_number}: {str(e)}")
                )
                error_count += 1
        
        # Summary
        self.stdout.write("-" * 50)
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN COMPLETE: Would send {sent_count} reminders, "
                    f"{skipped_count} skipped"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"COMPLETE: Sent {sent_count} reminders, "
                    f"{skipped_count} skipped, {error_count} errors"
                )
            )
    
    def send_reminder(self, invoice, reminder_type, days_before_due, is_overdue=False):
        """
        Send a rent payment reminder to the tenant.
        This is a placeholder - implement your actual notification logic here.
        """
        tenant = invoice.tenant
        
        try:
            if reminder_type == 'email':
                return self.send_email_reminder(invoice, is_overdue)
            elif reminder_type == 'sms':
                return self.send_sms_reminder(invoice, is_overdue)
            elif reminder_type == 'push':
                return self.send_push_reminder(invoice, is_overdue)
            else:
                return False
        except Exception as e:
            self.stdout.write(f"Error sending {reminder_type} reminder: {str(e)}")
            return False
    
    def send_email_reminder(self, invoice, is_overdue):
        """Send email reminder - implement with your email service"""
        # Placeholder for email implementation
        # from django.core.mail import send_mail
        # from django.template.loader import render_to_string
        
        self.stdout.write(f"    EMAIL: Would send email to {invoice.tenant.email}")
        return True  # Return True for successful send, False for failure
    
    def send_sms_reminder(self, invoice, is_overdue):
        """Send SMS reminder - implement with your SMS service"""
        # Placeholder for SMS implementation
        # phone = getattr(invoice.tenant.profile, 'phone', None)
        
        self.stdout.write(f"    SMS: Would send SMS to tenant")
        return True
    
    def send_push_reminder(self, invoice, is_overdue):
        """Send push notification - implement with your push service"""
        # Placeholder for push notification implementation
        
        self.stdout.write(f"    PUSH: Would send push notification to tenant")
        return True