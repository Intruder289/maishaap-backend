from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from properties.models import Property, PropertyType, Region
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with test properties for pagination testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of properties to create (default: 20)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing properties before creating new ones',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            Property.objects.all().delete()
            self.stdout.write(
                self.style.WARNING('Cleared all existing properties')
            )

        # Get required data
        users = list(User.objects.all())
        property_types = list(PropertyType.objects.all())
        regions = list(Region.objects.all())

        if not users or not property_types or not regions:
            self.stdout.write(
                self.style.ERROR(
                    'Please ensure you have users, property types, and regions in the database'
                )
            )
            return

        # Property templates
        property_templates = [
            {
                'title_templates': ['Modern Apartment', 'Luxury Condo', 'City View Apartment', 'Downtown Loft'],
                'descriptions': [
                    'Beautiful modern apartment with stunning city views',
                    'Luxury living in the heart of the city',
                    'Contemporary apartment with premium finishes',
                    'Urban living at its finest'
                ]
            },
            {
                'title_templates': ['Family House', 'Suburban Home', 'Spacious Villa', 'Garden House'],
                'descriptions': [
                    'Perfect family home in quiet neighborhood',
                    'Spacious house with beautiful garden',
                    'Ideal for families with children',
                    'Comfortable living with outdoor space'
                ]
            },
            {
                'title_templates': ['Studio Apartment', 'Cozy Studio', 'Compact Living', 'Efficient Studio'],
                'descriptions': [
                    'Perfect for students and young professionals',
                    'Efficient use of space with modern amenities',
                    'Ideal starter home in great location',
                    'Affordable living without compromising style'
                ]
            }
        ]

        created_count = 0
        for i in range(count):
            template = random.choice(property_templates)
            
            # Generate property data
            title_base = random.choice(template['title_templates'])
            title = f"{title_base} #{i+1}"
            description = random.choice(template['descriptions'])
            
            property_data = {
                'title': title,
                'description': description,
                'property_type': random.choice(property_types),
                'region': random.choice(regions),
                'address': f"{random.randint(100, 999)} {random.choice(['Main St', 'Oak Ave', 'Park Blvd', 'Garden Rd', 'View Ct'])}, Zone {i+1}",
                'bedrooms': random.randint(1, 5),
                'bathrooms': random.randint(1, 4),
                'size_sqft': random.randint(400, 3000),
                'rent_amount': random.randint(20000, 150000),
                'deposit_amount': random.randint(10000, 50000),
                'status': random.choice(['available', 'rented', 'under_maintenance']),
                'is_furnished': random.choice([True, False]),
                'pets_allowed': random.choice([True, False]),
                'smoking_allowed': random.choice([True, False]),
                'utilities_included': random.choice([True, False]),
                'owner': random.choice(users),
            }
            
            # Check if property with this title already exists
            if not Property.objects.filter(title=title).exists():
                Property.objects.create(**property_data)
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} properties'
            )
        )
        
        total_properties = Property.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Total properties in database: {total_properties}'
            )
        )