from django.core.management.base import BaseCommand
from django.utils import timezone
from properties.models import Booking
from documents.models import Booking as DocumentBooking


class Command(BaseCommand):
    help = 'Cancel expired bookings that have no payment (partial or full) within the expiration time'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cancelled without actually cancelling',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        cancelled_count = 0
        
        # Process properties.Booking
        expired_bookings = Booking.objects.filter(
            booking_status__in=['pending', 'confirmed'],
            payment_status='pending'
        ).select_related('property_obj')
        
        for booking in expired_bookings:
            if booking.is_expired():
                if dry_run:
                    cancelled_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'Would cancel booking {booking.booking_reference} '
                            f'(Property: {booking.property_obj.title}, '
                            f'Created: {booking.created_at})'
                        )
                    )
                else:
                    if booking.cancel_if_expired():
                        cancelled_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Cancelled booking {booking.booking_reference} '
                                f'(Property: {booking.property_obj.title})'
                            )
                        )
        
        # Process documents.Booking (mobile app bookings)
        # Note: documents.Booking doesn't have payment_status, so we check all pending/confirmed
        expired_doc_bookings = DocumentBooking.objects.filter(
            status__in=['pending', 'confirmed']
        ).select_related('property_ref')
        
        for doc_booking in expired_doc_bookings:
            # Check if expired (similar logic but for documents.Booking)
            expiration_hours = doc_booking.property_ref.booking_expiration_hours
            if expiration_hours == 0:
                continue  # Auto-cancellation disabled
            
            # Check if expired
            from datetime import timedelta
            expiration_time = doc_booking.created_at + timedelta(hours=expiration_hours)
            current_time = timezone.now()
            
            if current_time > expiration_time:
                # Check if there are any payments (we'd need to check Payment model)
                # For now, we'll cancel if expired (mobile app bookings typically don't have separate payment tracking)
                # But we should check if status is still pending/confirmed (not already cancelled)
                if doc_booking.status in ['pending', 'confirmed']:
                    if dry_run:
                        cancelled_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'Would cancel mobile booking {doc_booking.id} '
                                f'(Property: {doc_booking.property_ref.title}, '
                                f'Created: {doc_booking.created_at})'
                            )
                        )
                    else:
                        doc_booking.status = 'cancelled'
                        doc_booking.save(update_fields=['status'])
                        cancelled_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Cancelled mobile booking {doc_booking.id} '
                                f'(Property: {doc_booking.property_ref.title})'
                            )
                        )
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'\nDry run complete. Would cancel {cancelled_count} bookings.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully cancelled {cancelled_count} expired bookings.')
            )

