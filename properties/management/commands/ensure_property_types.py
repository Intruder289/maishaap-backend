from django.core.management.base import BaseCommand
from properties.models import PropertyType


class Command(BaseCommand):
    help = 'Ensure required property types (House, Hotel, Lodge, Venue) exist in the database'

    def handle(self, *args, **options):
        self.stdout.write('Ensuring required property types exist...')
        
        # Required property types for the mobile app
        # Note: PropertyType.save() normalizes names to lowercase, so we check for lowercase
        property_types_data = [
            {'name': 'house', 'display_name': 'House', 'description': 'Residential properties for rent'},
            {'name': 'hotel', 'display_name': 'Hotel', 'description': 'Commercial hotel properties with rooms'},
            {'name': 'lodge', 'display_name': 'Lodge', 'description': 'Lodge/accommodation facilities'},
            {'name': 'venue', 'display_name': 'Venue', 'description': 'Event venues and spaces'},
        ]
        
        created_count = 0
        for prop_type_data in property_types_data:
            # Check if it exists (using lowercase name since save() normalizes it)
            try:
                prop_type = PropertyType.objects.get(name=prop_type_data['name'])
                self.stdout.write(f'  Property type already exists: {prop_type.name.title()}')
            except PropertyType.DoesNotExist:
                # Create new property type
                prop_type = PropertyType.objects.create(
                    name=prop_type_data['name'],
                    description=prop_type_data['description']
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created property type: {prop_type_data["display_name"]}')
                )
                created_count += 1
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} property type(s)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll required property types already exist')
            )

