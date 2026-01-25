"""
Management command to sync room status for all hotel/lodge rooms.
This ensures rooms automatically become available when bookings end.

Run this daily via cron or scheduled task to keep room statuses up-to-date.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from properties.models import Room, Property


class Command(BaseCommand):
    help = 'Sync room status for all hotel/lodge rooms based on active bookings. Ensures rooms become available when bookings end.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--property-id',
            type=int,
            help='Sync rooms for a specific property ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        property_id = options.get('property_id')
        
        today = timezone.now().date()
        self.stdout.write(f'Syncing room statuses (Today: {today})...')
        
        # Get all hotel/lodge properties
        properties_query = Property.objects.filter(
            property_type__name__in=['hotel', 'lodge']
        )
        
        if property_id:
            properties_query = properties_query.filter(id=property_id)
            self.stdout.write(f'Filtering by property ID: {property_id}')
        
        properties = properties_query.select_related('property_type')
        total_properties = properties.count()
        
        if total_properties == 0:
            self.stdout.write(self.style.WARNING('No hotel/lodge properties found.'))
            return
        
        self.stdout.write(f'Found {total_properties} hotel/lodge properties')
        
        synced_count = 0
        available_count = 0
        occupied_count = 0
        
        for property_obj in properties:
            rooms = Room.objects.filter(
                property_obj=property_obj,
                is_active=True
            )
            
            for room in rooms:
                # Get current status before sync
                old_status = room.status
                
                if dry_run:
                    # Check what the status would be
                    from properties.models import Booking
                    active_bookings = Booking.objects.filter(
                        property_obj=property_obj,
                        room_number=room.room_number,
                        booking_status__in=['pending', 'confirmed', 'checked_in'],
                        check_out_date__gt=today
                    ).exclude(
                        booking_status__in=['cancelled', 'checked_out', 'no_show']
                    )
                    
                    has_active = active_bookings.exists()
                    new_status = 'occupied' if has_active else 'available'
                    
                    if old_status != new_status:
                        self.stdout.write(
                            f'  Would update Room {room.room_number} ({property_obj.title}): '
                            f'{old_status} -> {new_status}'
                        )
                else:
                    # Actually sync the room status
                    room.sync_status_from_bookings()
                    
                    if room.status != old_status:
                        synced_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  Updated Room {room.room_number} ({property_obj.title}): '
                                f'{old_status} -> {room.status}'
                            )
                        )
                
                # Count current status
                if room.status == 'available':
                    available_count += 1
                elif room.status == 'occupied':
                    occupied_count += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run completed. No changes made.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSync completed!\n'
                    f'  Rooms synced: {synced_count}\n'
                    f'  Available rooms: {available_count}\n'
                    f'  Occupied rooms: {occupied_count}'
                )
            )
