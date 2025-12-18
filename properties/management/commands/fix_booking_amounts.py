"""
Management command to fix booking total amounts that don't match calculated amounts.
This updates house bookings where total_amount != calculated_total_amount.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from properties.models import Booking
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fix booking total amounts that don\'t match calculated amounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all house bookings
        bookings = Booking.objects.filter(
            property_obj__property_type__name__iexact='house'
        ).select_related('property_obj')
        
        fixes_needed = []
        
        for booking in bookings:
            calculated = booking.calculated_total_amount
            stored = booking.total_amount
            
            if calculated != stored:
                fixes_needed.append({
                    'booking': booking,
                    'booking_ref': booking.booking_reference,
                    'customer': booking.customer.full_name,
                    'property': booking.property_obj.title,
                    'old_total': stored,
                    'new_total': calculated,
                    'diff': calculated - stored
                })
        
        if not fixes_needed:
            self.stdout.write(self.style.SUCCESS('No bookings need fixing. All amounts are correct!'))
            return
        
        self.stdout.write(self.style.WARNING(f'\nFound {len(fixes_needed)} bookings that need fixing:\n'))
        
        for fix in fixes_needed:
            self.stdout.write(f"Booking: {fix['booking_ref']}")
            self.stdout.write(f"Customer: {fix['customer']}")
            self.stdout.write(f"Property: {fix['property']}")
            self.stdout.write(f"Old Total: Tsh {fix['old_total']:,.0f}")
            self.stdout.write(f"New Total: Tsh {fix['new_total']:,.0f}")
            self.stdout.write(f"Difference: Tsh {fix['diff']:,.0f}")
            self.stdout.write('-' * 50)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes made. Remove --dry-run to apply fixes.'))
            return
        
        # Apply fixes
        self.stdout.write(self.style.WARNING(f'\nApplying fixes to {len(fixes_needed)} bookings...\n'))
        
        fixed_count = 0
        with transaction.atomic():
            for fix in fixes_needed:
                booking = fix['booking']
                
                # Update the total amount
                old_payment_status = booking.payment_status
                booking.calculate_and_update_total()
                
                # Update payment status based on new total
                booking.update_payment_status()
                
                fixed_count += 1
                
                status_msg = ''
                if old_payment_status != booking.payment_status:
                    status_msg = f" | Status: {old_payment_status} -> {booking.payment_status}"
                
                self.stdout.write(
                    f"Fixed: {booking.booking_reference} - "
                    f"Tsh {fix['old_total']:,.0f} -> Tsh {fix['new_total']:,.0f}"
                    f"{status_msg}"
                )
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully fixed {fixed_count} bookings!'))
