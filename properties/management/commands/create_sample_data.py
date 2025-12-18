from django.core.management.base import BaseCommand
from properties.models import PropertyType, Region, Amenity

class Command(BaseCommand):
    help = 'Create sample data for properties'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Property Types
        property_types_data = [
            'Apartment',
            'House',
            'Studio',
            'Condo',
            'Townhouse',
            'Villa'
        ]

        for pt_name in property_types_data:
            pt, created = PropertyType.objects.get_or_create(name=pt_name)
            if created:
                self.stdout.write(f'Created property type: {pt_name}')
            else:
                self.stdout.write(f'Property type already exists: {pt_name}')

        # Create Regions
        regions_data = [
            'Dar es Salaam',
            'Arusha',
            'Mwanza',
            'Dodoma',
            'Tanga',
            'Morogoro',
            'Mbeya',
            'Kilimanjaro'
        ]

        for region_name in regions_data:
            region, created = Region.objects.get_or_create(name=region_name)
            if created:
                self.stdout.write(f'Created region: {region_name}')
            else:
                self.stdout.write(f'Region already exists: {region_name}')

        # Create Amenities
        amenities_data = [
            'WiFi',
            'Parking',
            'Swimming Pool',
            'Gym',
            'Air Conditioning',
            'Balcony',
            'Garden',
            'Security',
            'Elevator',
            'Pet Friendly',
            'Furnished',
            'Utilities Included'
        ]

        for amenity_name in amenities_data:
            amenity, created = Amenity.objects.get_or_create(name=amenity_name)
            if created:
                self.stdout.write(f'Created amenity: {amenity_name}')
            else:
                self.stdout.write(f'Amenity already exists: {amenity_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data created successfully!\n'
                f'Property Types: {PropertyType.objects.count()}\n'
                f'Regions: {Region.objects.count()}\n'
                f'Amenities: {Amenity.objects.count()}'
            )
        )
