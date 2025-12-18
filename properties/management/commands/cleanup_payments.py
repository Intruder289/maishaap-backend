from django.core.management.base import BaseCommand
from properties.models import Payment, Booking


class Command(BaseCommand):
    help = 'Clean up duplicate payments and reset booking payment status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--booking-id',
            type=int,
            help='Clean payments for specific booking ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clean all payments (use with caution)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        booking_id = options.get('booking_id')
        clean_all = options.get('all')
        dry_run = options.get('dry_run')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        if booking_id:
            # Clean specific booking
            try:
                booking = Booking.objects.get(id=booking_id)
                payments = Payment.objects.filter(booking=booking)
                
                self.stdout.write(f'Found {payments.count()} payments for booking {booking.booking_reference}')
                
                if dry_run:
                    for payment in payments:
                        self.stdout.write(f'Would delete: Payment #{payment.id} - Tsh{payment.amount} ({payment.payment_type})')
                else:
                    payments.delete()
                    booking.paid_amount = 0
                    booking.update_payment_status()
                    booking.save()
                    self.stdout.write(self.style.SUCCESS(f'Cleaned up payments for booking {booking.booking_reference}'))
                    
            except Booking.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Booking with ID {booking_id} not found'))
                
        elif clean_all:
            # Clean all payments
            payments = Payment.objects.all()
            bookings = Booking.objects.all()
            
            self.stdout.write(f'Found {payments.count()} payments across {bookings.count()} bookings')
            
            if dry_run:
                for payment in payments:
                    self.stdout.write(f'Would delete: Payment #{payment.id} - {payment.booking.booking_reference} - Tsh{payment.amount}')
            else:
                payments.delete()
                for booking in bookings:
                    booking.paid_amount = 0
                    booking.update_payment_status()
                    booking.save()
                self.stdout.write(self.style.SUCCESS('Cleaned up all payments'))
                
        else:
            # Show help
            self.stdout.write('Usage:')
            self.stdout.write('  python manage.py cleanup_payments --booking-id 1  # Clean specific booking')
            self.stdout.write('  python manage.py cleanup_payments --all            # Clean all payments')
            self.stdout.write('  python manage.py cleanup_payments --dry-run        # Show what would be deleted')
            self.stdout.write('')
            self.stdout.write('Current payments:')
            for payment in Payment.objects.all()[:10]:  # Show first 10
                self.stdout.write(f'  Payment #{payment.id}: {payment.booking.booking_reference} - Tsh{payment.amount} ({payment.payment_type})')
            
            if Payment.objects.count() > 10:
                self.stdout.write(f'  ... and {Payment.objects.count() - 10} more')
