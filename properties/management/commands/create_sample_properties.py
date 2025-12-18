from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from properties.models import Region, PropertyType, Amenity, Property
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Create sample data for testing the Properties module'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data for Properties module...'))
        
        # Create sample users if they don't exist
        if not User.objects.filter(username='owner1').exists():
            owner1 = User.objects.create_user(
                username='owner1',
                email='owner1@example.com',
                password='testpass123',
                first_name='John',
                last_name='Doe'
            )
            Profile.objects.update_or_create(
                user=owner1,
                defaults={
                    'role': 'owner',
                    'is_approved': True
                }
            )
            self.stdout.write(f'Created owner user: {owner1.username}')
        
        if not User.objects.filter(username='owner2').exists():
            owner2 = User.objects.create_user(
                username='owner2',
                email='owner2@example.com',
                password='testpass123',
                first_name='Jane',
                last_name='Smith'
            )
            Profile.objects.update_or_create(
                user=owner2,
                defaults={
                    'role': 'owner',
                    'is_approved': True
                }
            )
            self.stdout.write(f'Created owner user: {owner2.username}')
        
        # Create regions
        regions_data = [
            {'name': 'Nairobi CBD', 'description': 'Central Business District of Nairobi'},
            {'name': 'Westlands', 'description': 'Upmarket residential and commercial area'},
            {'name': 'Karen', 'description': 'Leafy suburb with luxury homes'},
            {'name': 'Kilimani', 'description': 'Mixed residential and commercial area'},
            {'name': 'Lavington', 'description': 'Upmarket residential area'},
            {'name': 'Kileleshwa', 'description': 'Residential area near the city center'},
        ]
        
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults={'description': region_data['description']}
            )
            if created:
                self.stdout.write(f'Created region: {region.name}')
        
        # Create property types
        property_types_data = [
            {'name': 'Apartment', 'description': 'Multi-story residential building units'},
            {'name': 'House', 'description': 'Single-family detached homes'},
            {'name': 'Studio', 'description': 'Single room living spaces'},
            {'name': 'Townhouse', 'description': 'Multi-story attached homes'},
            {'name': 'Penthouse', 'description': 'Luxury top-floor apartments'},
            {'name': 'Villa', 'description': 'Luxury standalone homes'},
        ]
        
        for prop_type_data in property_types_data:
            prop_type, created = PropertyType.objects.get_or_create(
                name=prop_type_data['name'],
                defaults={'description': prop_type_data['description']}
            )
            if created:
                self.stdout.write(f'Created property type: {prop_type.name}')
        
        # Create amenities
        amenities_data = [
            {'name': 'WiFi', 'description': 'High-speed internet connection', 'icon': 'wifi'},
            {'name': 'Parking', 'description': 'Dedicated parking space', 'icon': 'car'},
            {'name': 'Swimming Pool', 'description': 'Shared or private pool', 'icon': 'pool'},
            {'name': 'Gym', 'description': 'Fitness center access', 'icon': 'fitness'},
            {'name': 'Security', 'description': '24/7 security service', 'icon': 'security'},
            {'name': 'Garden', 'description': 'Private or shared garden space', 'icon': 'garden'},
            {'name': 'Balcony', 'description': 'Private outdoor space', 'icon': 'balcony'},
            {'name': 'Air Conditioning', 'description': 'Climate control system', 'icon': 'ac'},
            {'name': 'Furnished', 'description': 'Fully furnished unit', 'icon': 'furniture'},
            {'name': 'Laundry', 'description': 'Washing machine access', 'icon': 'laundry'},
        ]
        
        for amenity_data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_data['name'],
                defaults={
                    'description': amenity_data['description'],
                    'icon': amenity_data['icon']
                }
            )
            if created:
                self.stdout.write(f'Created amenity: {amenity.name}')
        
        # Create sample properties
        owner1 = User.objects.get(username='owner1')
        owner2 = User.objects.get(username='owner2')
        
        properties_data = [
            {
                'title': 'Modern 2BR Apartment in Westlands',
                'description': 'Beautiful modern apartment with great city views. Located in the heart of Westlands with easy access to shopping malls and restaurants.',
                'property_type': 'Apartment',
                'region': 'Westlands',
                'address': '123 Westlands Avenue, Westlands, Nairobi',
                'bedrooms': 2,
                'bathrooms': 2,
                'size_sqft': 1200,
                'rent_amount': 80000,
                'deposit_amount': 160000,
                'owner': owner1,
                'status': 'available',
                'is_featured': True,
                'is_furnished': True,
                'pets_allowed': False,
                'amenities': ['WiFi', 'Parking', 'Security', 'Balcony', 'Furnished']
            },
            {
                'title': 'Luxury 3BR House in Karen',
                'description': 'Spacious family home in the prestigious Karen area. Features a large garden and swimming pool.',
                'property_type': 'House',
                'region': 'Karen',
                'address': '456 Karen Road, Karen, Nairobi',
                'bedrooms': 3,
                'bathrooms': 3,
                'size_sqft': 2500,
                'rent_amount': 150000,
                'deposit_amount': 300000,
                'owner': owner1,
                'status': 'available',
                'is_featured': True,
                'is_furnished': False,
                'pets_allowed': True,
                'amenities': ['WiFi', 'Parking', 'Swimming Pool', 'Security', 'Garden']
            },
            {
                'title': 'Cozy Studio in Kilimani',
                'description': 'Perfect for young professionals. Compact but well-designed studio apartment.',
                'property_type': 'Studio',
                'region': 'Kilimani',
                'address': '789 Kilimani Street, Kilimani, Nairobi',
                'bedrooms': 1,
                'bathrooms': 1,
                'size_sqft': 500,
                'rent_amount': 35000,
                'deposit_amount': 70000,
                'owner': owner2,
                'status': 'available',
                'is_featured': False,
                'is_furnished': True,
                'pets_allowed': False,
                'amenities': ['WiFi', 'Security', 'Furnished', 'Laundry']
            },
            {
                'title': 'Executive 4BR Townhouse in Lavington',
                'description': 'Premium townhouse perfect for executives and families. Modern amenities and excellent location.',
                'property_type': 'Townhouse',
                'region': 'Lavington',
                'address': '321 Lavington Gardens, Lavington, Nairobi',
                'bedrooms': 4,
                'bathrooms': 4,
                'size_sqft': 3000,
                'rent_amount': 200000,
                'deposit_amount': 400000,
                'owner': owner2,
                'status': 'rented',
                'is_featured': True,
                'is_furnished': False,
                'pets_allowed': True,
                'amenities': ['WiFi', 'Parking', 'Security', 'Garden', 'Gym', 'Air Conditioning']
            },
            {
                'title': 'Penthouse in Nairobi CBD',
                'description': 'Luxury penthouse with panoramic city views. Located in the heart of the business district.',
                'property_type': 'Penthouse',
                'region': 'Nairobi CBD',
                'address': '100 Kenyatta Avenue, Nairobi CBD',
                'bedrooms': 3,
                'bathrooms': 3,
                'size_sqft': 2000,
                'rent_amount': 250000,
                'deposit_amount': 500000,
                'owner': owner1,
                'status': 'available',
                'is_featured': True,
                'is_furnished': True,
                'pets_allowed': False,
                'amenities': ['WiFi', 'Parking', 'Swimming Pool', 'Gym', 'Security', 'Air Conditioning', 'Balcony', 'Furnished']
            }
        ]
        
        for prop_data in properties_data:
            # Check if property already exists
            if Property.objects.filter(title=prop_data['title']).exists():
                continue
                
            property_obj = Property.objects.create(
                title=prop_data['title'],
                description=prop_data['description'],
                property_type=PropertyType.objects.get(name=prop_data['property_type']),
                region=Region.objects.get(name=prop_data['region']),
                address=prop_data['address'],
                bedrooms=prop_data['bedrooms'],
                bathrooms=prop_data['bathrooms'],
                size_sqft=prop_data['size_sqft'],
                rent_amount=prop_data['rent_amount'],
                deposit_amount=prop_data['deposit_amount'],
                owner=prop_data['owner'],
                status=prop_data['status'],
                is_featured=prop_data['is_featured'],
                is_furnished=prop_data['is_furnished'],
                pets_allowed=prop_data['pets_allowed']
            )
            
            # Add amenities
            amenities = Amenity.objects.filter(name__in=prop_data['amenities'])
            property_obj.amenities.set(amenities)
            
            self.stdout.write(f'Created property: {property_obj.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data for Properties module!')
        )
        self.stdout.write(
            self.style.WARNING('You can now test the Properties API endpoints in Swagger UI at: http://127.0.0.1:8000/swagger/')
        )