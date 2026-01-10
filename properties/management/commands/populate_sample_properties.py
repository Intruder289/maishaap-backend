"""
Management command to populate sample properties with images
Downloads images from Unsplash (free stock photos)
"""
import os
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.utils import timezone
from properties.models import (
    Property, PropertyType, Region, District, Amenity, PropertyImage
)
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Populate sample properties (5 houses, 5 hotels, 5 lodges, 5 venues) with images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--owner-username',
            type=str,
            default='admin',
            help='Username of the owner to assign properties to (default: admin)'
        )

    def handle(self, *args, **options):
        owner_username = options['owner_username']
        
        # Get or create owner
        owner, created = User.objects.get_or_create(
            username=owner_username,
            defaults={
                'email': f'{owner_username}@example.com',
                'first_name': 'Property',
                'last_name': 'Owner',
                'is_staff': True,
            }
        )
        if created:
            owner.set_password('admin123')
            owner.save()
            # Create profile
            Profile.objects.get_or_create(
                user=owner,
                defaults={
                    'role': 'owner',
                    'is_approved': True,
                }
            )
            self.stdout.write(self.style.SUCCESS(f'Created owner user: {owner_username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing owner: {owner_username}'))

        # Get or create property types (PropertyType saves names in lowercase)
        house_type = PropertyType.objects.filter(name='house').first()
        if not house_type:
            house_type = PropertyType.objects.create(name='House', description='Residential houses')
        
        hotel_type = PropertyType.objects.filter(name='hotel').first()
        if not hotel_type:
            hotel_type = PropertyType.objects.create(name='Hotel', description='Hotels and accommodations')
        
        lodge_type = PropertyType.objects.filter(name='lodge').first()
        if not lodge_type:
            lodge_type = PropertyType.objects.create(name='Lodge', description='Lodges and resorts')
        
        venue_type = PropertyType.objects.filter(name='venue').first()
        if not venue_type:
            venue_type = PropertyType.objects.create(name='Venue', description='Event venues')

        # Get or create region
        region, _ = Region.objects.get_or_create(
            name='Dar es Salaam',
            defaults={'description': 'Dar es Salaam Region'}
        )

        # Get or create district
        district, _ = District.objects.get_or_create(
            name='Kinondoni',
            region=region,
            defaults={'description': 'Kinondoni District'}
        )

        # Sample image URLs (using Unsplash for free high-quality images)
        # These are placeholder URLs - in production, you'd want to download actual property images
        image_urls = {
            'house': [
                'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800',
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800',
                'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800',
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800',
                'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800',
            ],
            'hotel': [
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
                'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800',
                'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
                'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800',
            ],
            'lodge': [
                'https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=800',
                'https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=800',
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
                'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800',
                'https://images.unsplash.com/photo-1551632436-cbf8dd35adfa?w=800',
            ],
            'venue': [
                'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800',
                'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800',
                'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800',
                'https://images.unsplash.com/photo-1511578314322-379afb476865?w=800',
                'https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=800',
            ],
        }

        # Sample property data
        properties_data = {
            'house': [
                {
                    'title': 'Modern 3-Bedroom House in Kinondoni',
                    'description': 'Beautiful modern house with 3 bedrooms, 2 bathrooms, fully furnished. Located in a quiet neighborhood with easy access to schools and shopping centers.',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'size_sqft': 1800,
                    'rent_amount': 800000,
                    'deposit_amount': 1600000,
                    'visit_cost': 5000,
                    'is_furnished': True,
                    'pets_allowed': True,
                },
                {
                    'title': 'Spacious 4-Bedroom Family Home',
                    'description': 'Large family home with 4 bedrooms, 3 bathrooms, and a beautiful garden. Perfect for families looking for comfort and space.',
                    'bedrooms': 4,
                    'bathrooms': 3,
                    'size_sqft': 2500,
                    'rent_amount': 1200000,
                    'deposit_amount': 2400000,
                    'visit_cost': 5000,
                    'is_furnished': True,
                    'pets_allowed': True,
                },
                {
                    'title': 'Cozy 2-Bedroom Apartment',
                    'description': 'Well-maintained 2-bedroom apartment in a secure building. Close to public transport and city center.',
                    'bedrooms': 2,
                    'bathrooms': 1,
                    'size_sqft': 1200,
                    'rent_amount': 600000,
                    'deposit_amount': 1200000,
                    'visit_cost': 5000,
                    'is_furnished': False,
                    'pets_allowed': False,
                },
                {
                    'title': 'Luxury 5-Bedroom Villa',
                    'description': 'Stunning luxury villa with 5 bedrooms, 4 bathrooms, swimming pool, and landscaped gardens. Premium location with security.',
                    'bedrooms': 5,
                    'bathrooms': 4,
                    'size_sqft': 4000,
                    'rent_amount': 2500000,
                    'deposit_amount': 5000000,
                    'visit_cost': 10000,
                    'is_furnished': True,
                    'pets_allowed': True,
                },
                {
                    'title': 'Affordable 1-Bedroom Starter Home',
                    'description': 'Perfect starter home with 1 bedroom, 1 bathroom. Ideal for young professionals or couples. Well-maintained and clean.',
                    'bedrooms': 1,
                    'bathrooms': 1,
                    'size_sqft': 800,
                    'rent_amount': 400000,
                    'deposit_amount': 800000,
                    'visit_cost': 3000,
                    'is_furnished': False,
                    'pets_allowed': False,
                },
            ],
            'hotel': [
                {
                    'title': 'Grand City Hotel',
                    'description': 'Luxury hotel in the heart of the city. Features modern rooms, restaurant, conference facilities, and excellent service.',
                    'total_rooms': 50,
                    'room_types': {'standard': 30, 'deluxe': 15, 'suite': 5},
                    'rent_amount': 150000,
                    'deposit_amount': 300000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Beachfront Paradise Hotel',
                    'description': 'Beautiful beachfront hotel with ocean views. Perfect for vacationers seeking relaxation and stunning scenery.',
                    'total_rooms': 40,
                    'room_types': {'ocean_view': 25, 'beachfront': 15},
                    'rent_amount': 200000,
                    'deposit_amount': 400000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Business Hotel Downtown',
                    'description': 'Modern business hotel with excellent facilities for corporate travelers. Conference rooms, business center, and high-speed WiFi.',
                    'total_rooms': 80,
                    'room_types': {'standard': 50, 'executive': 25, 'presidential': 5},
                    'rent_amount': 120000,
                    'deposit_amount': 240000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Boutique Heritage Hotel',
                    'description': 'Charming boutique hotel with traditional architecture and modern amenities. Unique character and personalized service.',
                    'total_rooms': 25,
                    'room_types': {'heritage': 20, 'luxury': 5},
                    'rent_amount': 180000,
                    'deposit_amount': 360000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Family-Friendly Resort Hotel',
                    'description': 'Perfect for families with kids. Features family rooms, kids club, swimming pool, and various entertainment options.',
                    'total_rooms': 60,
                    'room_types': {'family': 40, 'standard': 20},
                    'rent_amount': 170000,
                    'deposit_amount': 340000,
                    'rent_period': 'day',
                },
            ],
            'lodge': [
                {
                    'title': 'Serengeti Safari Lodge',
                    'description': 'Authentic safari lodge experience. Close to wildlife reserves with guided tours and traditional accommodations.',
                    'total_rooms': 20,
                    'room_types': {'tent': 15, 'cabin': 5},
                    'rent_amount': 250000,
                    'deposit_amount': 500000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Mountain View Lodge',
                    'description': 'Scenic mountain lodge with breathtaking views. Perfect for nature lovers and hiking enthusiasts.',
                    'total_rooms': 15,
                    'room_types': {'mountain_view': 12, 'deluxe': 3},
                    'rent_amount': 180000,
                    'deposit_amount': 360000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Lakeside Retreat Lodge',
                    'description': 'Peaceful lakeside lodge offering tranquility and natural beauty. Great for fishing, bird watching, and relaxation.',
                    'total_rooms': 18,
                    'room_types': {'lake_view': 15, 'standard': 3},
                    'rent_amount': 200000,
                    'deposit_amount': 400000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Adventure Base Camp Lodge',
                    'description': 'Adventure-focused lodge for outdoor activities. Offers guided tours, equipment rental, and expert guides.',
                    'total_rooms': 12,
                    'room_types': {'adventure': 10, 'standard': 2},
                    'rent_amount': 220000,
                    'deposit_amount': 440000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Eco-Friendly Nature Lodge',
                    'description': 'Sustainable eco-lodge with minimal environmental impact. Solar power, organic food, and nature conservation focus.',
                    'total_rooms': 16,
                    'room_types': {'eco': 14, 'deluxe': 2},
                    'rent_amount': 190000,
                    'deposit_amount': 380000,
                    'rent_period': 'day',
                },
            ],
            'venue': [
                {
                    'title': 'Grand Conference Center',
                    'description': 'State-of-the-art conference center with multiple halls, modern AV equipment, and catering services. Perfect for corporate events.',
                    'capacity': 500,
                    'venue_type': 'conference',
                    'rent_amount': 2000000,
                    'deposit_amount': 4000000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Elegant Wedding Hall',
                    'description': 'Beautiful wedding venue with elegant decor, spacious hall, and professional event planning services. Perfect for memorable celebrations.',
                    'capacity': 300,
                    'venue_type': 'wedding',
                    'rent_amount': 1500000,
                    'deposit_amount': 3000000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Modern Exhibition Space',
                    'description': 'Large exhibition space ideal for trade shows, product launches, and large gatherings. Flexible layout options available.',
                    'capacity': 800,
                    'venue_type': 'exhibition',
                    'rent_amount': 2500000,
                    'deposit_amount': 5000000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Intimate Event Venue',
                    'description': 'Cozy venue perfect for small to medium events. Intimate atmosphere with professional sound and lighting systems.',
                    'capacity': 150,
                    'venue_type': 'event',
                    'rent_amount': 800000,
                    'deposit_amount': 1600000,
                    'rent_period': 'day',
                },
                {
                    'title': 'Outdoor Garden Venue',
                    'description': 'Beautiful outdoor garden venue for ceremonies, parties, and celebrations. Natural setting with covered areas for all weather.',
                    'capacity': 400,
                    'venue_type': 'outdoor',
                    'rent_amount': 1200000,
                    'deposit_amount': 2400000,
                    'rent_period': 'day',
                },
            ],
        }

        # Create properties
        created_count = 0
        for prop_type_key, prop_list in properties_data.items():
            prop_type = {
                'house': house_type,
                'hotel': hotel_type,
                'lodge': lodge_type,
                'venue': venue_type,
            }[prop_type_key]

            for idx, prop_data in enumerate(prop_list):
                # Create property with required size_sqft field
                # Set default size_sqft based on property type
                default_size = prop_data.get('size_sqft', 1000)  # Default 1000 sqft
                if prop_type_key in ['hotel', 'lodge']:
                    # Estimate size based on number of rooms (assume 300 sqft per room)
                    default_size = prop_data.get('total_rooms', 20) * 300
                elif prop_type_key == 'venue':
                    # Estimate size based on capacity (assume 10 sqft per person)
                    default_size = prop_data.get('capacity', 200) * 10

                property_obj = Property.objects.create(
                    title=prop_data['title'],
                    description=prop_data['description'],
                    property_type=prop_type,
                    region=region,
                    district=district,
                    address=f'{prop_data["title"]}, Kinondoni, Dar es Salaam',
                    latitude=-6.7924,
                    longitude=39.2083,
                    size_sqft=default_size,
                    owner=owner,
                    status='available',
                    is_active=True,
                    is_approved=True,
                    approved_by=owner,
                    approved_at=timezone.now(),
                    rent_amount=prop_data['rent_amount'],
                    deposit_amount=prop_data.get('deposit_amount', 0),
                    rent_period=prop_data.get('rent_period', 'month'),
                    utilities_included=prop_data.get('utilities_included', False),
                    is_furnished=prop_data.get('is_furnished', False),
                    pets_allowed=prop_data.get('pets_allowed', False),
                    available_from=timezone.now().date(),
                )

                # Add type-specific fields
                if prop_type_key == 'house':
                    property_obj.bedrooms = prop_data.get('bedrooms')
                    property_obj.bathrooms = prop_data.get('bathrooms')
                    property_obj.size_sqft = prop_data.get('size_sqft', default_size)
                    property_obj.visit_cost = prop_data.get('visit_cost')
                elif prop_type_key in ['hotel', 'lodge']:
                    property_obj.total_rooms = prop_data.get('total_rooms')
                    property_obj.room_types = prop_data.get('room_types')
                elif prop_type_key == 'venue':
                    property_obj.capacity = prop_data.get('capacity')
                    property_obj.venue_type = prop_data.get('venue_type')

                property_obj.save()

                # Download and add images
                image_url = image_urls[prop_type_key][idx]
                try:
                    self.stdout.write(f'Downloading image for {property_obj.title}...')
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()
                    
                    # Create image file
                    image_file = ContentFile(response.content)
                    image_file.name = f'{prop_type_key}_{idx+1}.jpg'
                    
                    # Create PropertyImage
                    property_image = PropertyImage.objects.create(
                        property=property_obj,
                        image=image_file,
                        caption=f'{property_obj.title} - Main Image',
                        is_primary=True,
                        order=0,
                    )
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Added image to {property_obj.title}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  [WARNING] Could not download image for {property_obj.title}: {str(e)}'))
                    # Create a placeholder image entry (without actual file)
                    # In production, you might want to skip this or use a default image

                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {property_obj.title}'))

        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Successfully created {created_count} properties!'))
        self.stdout.write(self.style.SUCCESS(f'  - 5 Houses'))
        self.stdout.write(self.style.SUCCESS(f'  - 5 Hotels'))
        self.stdout.write(self.style.SUCCESS(f'  - 5 Lodges'))
        self.stdout.write(self.style.SUCCESS(f'  - 5 Venues'))

