from django.core.management.base import BaseCommand
from accounts.models import NavigationItem


class Command(BaseCommand):
    help = 'Populate initial navigation items for role-based sidebar access control'

    def handle(self, *args, **options):
        self.stdout.write('Creating initial navigation items...')
        
        # Create navigation items based on existing sidebar in base.html
        navigation_items = [
            # Main level navigation items
            {
                'name': 'dashboard',
                'display_name': 'Dashboard',
                'url_name': 'accounts:dashboard',
                'icon': '<i class="fas fa-tachometer-alt"></i>',
                'order': 1,
                'parent': None
            },
            {
                'name': 'properties',
                'display_name': 'Properties',
                'url_name': '#',
                'icon': '<i class="fas fa-home"></i>',
                'order': 2,
                'parent': None
            },
            {
                'name': 'manage_properties',
                'display_name': 'Manage Properties',
                'url_name': '#',
                'icon': '<i class="fas fa-cogs"></i>',
                'order': 3,
                'parent': None
            },
            {
                'name': 'user_management',
                'display_name': 'User Management',
                'url_name': '#',
                'icon': '<i class="fas fa-users"></i>',
                'order': 4,
                'parent': None
            },
            {
                'name': 'maintenance',
                'display_name': 'Maintenance',
                'url_name': '#',
                'icon': '<i class="fas fa-tools"></i>',
                'order': 5,
                'parent': None
            },
            {
                'name': 'complaints',
                'display_name': 'Complaints',
                'url_name': '#',
                'icon': '<i class="fas fa-exclamation-triangle"></i>',
                'order': 6,
                'parent': None
            },
            
            # Properties submenu items
            {
                'name': 'property_list',
                'display_name': 'All Properties',
                'url_name': 'properties:property_list',
                'icon': '',
                'order': 1,
                'parent': 'properties'
            },
            {
                'name': 'configure_property',
                'display_name': 'Configure Property',
                'url_name': '#',
                'icon': '',
                'order': 2,
                'parent': 'properties'
            },
            {
                'name': 'manage_property_types',
                'display_name': 'Property Types',
                'url_name': 'properties:manage_property_types',
                'icon': '',
                'order': 1,
                'parent': 'configure_property'
            },
            {
                'name': 'manage_regions',
                'display_name': 'Regions',
                'url_name': 'properties:manage_regions',
                'icon': '',
                'order': 2,
                'parent': 'configure_property'
            },
            {
                'name': 'manage_amenities',
                'display_name': 'Amenities',
                'url_name': 'properties:manage_amenities',
                'icon': '',
                'order': 3,
                'parent': 'configure_property'
            },
            {
                'name': 'house_rent_reminder_settings',
                'display_name': 'Reminder Settings',
                'url_name': 'properties:house_rent_reminder_settings',
                'icon': '<i class="fas fa-bell"></i>',
                'order': 3,
                'parent': 'properties'
            },
            
            # Manage Properties submenu items
            {
                'name': 'hotel_management',
                'display_name': 'Hotel Management',
                'url_name': '#',
                'icon': '',
                'order': 1,
                'parent': 'manage_properties'
            },
            {
                'name': 'hotel_dashboard',
                'display_name': 'Dashboard',
                'url_name': 'properties:hotel_dashboard',
                'icon': '',
                'order': 1,
                'parent': 'hotel_management'
            },
            {
                'name': 'hotel_bookings',
                'display_name': 'Bookings',
                'url_name': 'properties:hotel_bookings',
                'icon': '',
                'order': 2,
                'parent': 'hotel_management'
            },
            {
                'name': 'hotel_rooms',
                'display_name': 'Room Status',
                'url_name': 'properties:hotel_rooms',
                'icon': '',
                'order': 3,
                'parent': 'hotel_management'
            },
            {
                'name': 'hotel_customers',
                'display_name': 'Customers',
                'url_name': 'properties:hotel_customers',
                'icon': '',
                'order': 4,
                'parent': 'hotel_management'
            },
            {
                'name': 'hotel_payments',
                'display_name': 'Payments',
                'url_name': 'properties:hotel_payments',
                'icon': '',
                'order': 5,
                'parent': 'hotel_management'
            },
            {
                'name': 'hotel_reports',
                'display_name': 'Reports',
                'url_name': 'properties:hotel_reports',
                'icon': '',
                'order': 6,
                'parent': 'hotel_management'
            },
            {
                'name': 'lodge_management',
                'display_name': 'Lodge Management',
                'url_name': '#',
                'icon': '',
                'order': 2,
                'parent': 'manage_properties'
            },
            {
                'name': 'lodge_dashboard',
                'display_name': 'Dashboard',
                'url_name': 'properties:lodge_dashboard',
                'icon': '',
                'order': 1,
                'parent': 'lodge_management'
            },
            {
                'name': 'lodge_bookings',
                'display_name': 'Bookings',
                'url_name': 'properties:lodge_bookings',
                'icon': '',
                'order': 2,
                'parent': 'lodge_management'
            },
            {
                'name': 'lodge_rooms',
                'display_name': 'Room Status',
                'url_name': 'properties:lodge_rooms',
                'icon': '',
                'order': 3,
                'parent': 'lodge_management'
            },
            {
                'name': 'lodge_customers',
                'display_name': 'Customers',
                'url_name': 'properties:lodge_customers',
                'icon': '',
                'order': 4,
                'parent': 'lodge_management'
            },
            {
                'name': 'lodge_payments',
                'display_name': 'Payments',
                'url_name': 'properties:lodge_payments',
                'icon': '',
                'order': 5,
                'parent': 'lodge_management'
            },
            {
                'name': 'lodge_reports',
                'display_name': 'Reports',
                'url_name': 'properties:lodge_reports',
                'icon': '',
                'order': 6,
                'parent': 'lodge_management'
            },
            {
                'name': 'venue_management',
                'display_name': 'Venue Management',
                'url_name': '#',
                'icon': '',
                'order': 3,
                'parent': 'manage_properties'
            },
            {
                'name': 'venue_dashboard',
                'display_name': 'Dashboard',
                'url_name': 'properties:venue_dashboard',
                'icon': '',
                'order': 1,
                'parent': 'venue_management'
            },
            {
                'name': 'venue_bookings',
                'display_name': 'Bookings',
                'url_name': 'properties:venue_bookings',
                'icon': '',
                'order': 2,
                'parent': 'venue_management'
            },
            {
                'name': 'venue_availability',
                'display_name': 'Availability',
                'url_name': 'properties:venue_availability',
                'icon': '',
                'order': 3,
                'parent': 'venue_management'
            },
            {
                'name': 'venue_customers',
                'display_name': 'Customers',
                'url_name': 'properties:venue_customers',
                'icon': '',
                'order': 4,
                'parent': 'venue_management'
            },
            {
                'name': 'venue_payments',
                'display_name': 'Payments',
                'url_name': 'properties:venue_payments',
                'icon': '',
                'order': 5,
                'parent': 'venue_management'
            },
            {
                'name': 'venue_reports',
                'display_name': 'Reports',
                'url_name': 'properties:venue_reports',
                'icon': '',
                'order': 6,
                'parent': 'venue_management'
            },
            {
                'name': 'house_management',
                'display_name': 'House Management',
                'url_name': '#',
                'icon': '',
                'order': 4,
                'parent': 'manage_properties'
            },
            {
                'name': 'house_dashboard',
                'display_name': 'Dashboard',
                'url_name': 'properties:house_dashboard',
                'icon': '',
                'order': 1,
                'parent': 'house_management'
            },
            {
                'name': 'house_bookings',
                'display_name': 'Bookings',
                'url_name': 'properties:house_bookings',
                'icon': '',
                'order': 2,
                'parent': 'house_management'
            },
            {
                'name': 'house_tenants',
                'display_name': 'Tenants',
                'url_name': 'properties:house_tenants',
                'icon': '',
                'order': 3,
                'parent': 'house_management'
            },
            {
                'name': 'house_payments',
                'display_name': 'Payments',
                'url_name': 'properties:house_payments',
                'icon': '',
                'order': 4,
                'parent': 'house_management'
            },
            {
                'name': 'house_reports',
                'display_name': 'Reports',
                'url_name': 'properties:house_reports',
                'icon': '',
                'order': 5,
                'parent': 'house_management'
            },
            
            # User Management submenu items
            {
                'name': 'user_list',
                'display_name': 'All Users',
                'url_name': 'accounts:user_list',
                'icon': '',
                'order': 1,
                'parent': 'user_management'
            },
            {
                'name': 'owner_list',
                'display_name': 'Owner Management',
                'url_name': 'accounts:owner_list',
                'icon': '',
                'order': 2,
                'parent': 'user_management'
            },
            {
                'name': 'role_list',
                'display_name': 'Roles & Permissions',
                'url_name': 'accounts:role_list',
                'icon': '',
                'order': 3,
                'parent': 'user_management'
            },
            
            # Maintenance submenu items
            {
                'name': 'request_list',
                'display_name': 'All Requests',
                'url_name': 'maintenance:request_list',
                'icon': '',
                'order': 1,
                'parent': 'maintenance'
            },
            
            # Complaints submenu items
            {
                'name': 'complaint_list',
                'display_name': 'All Complaints',
                'url_name': 'complaints:complaint_list',
                'icon': '',
                'order': 1,
                'parent': 'complaints'
            },
        ]
        
        # Create navigation items
        created_items = {}
        
        # First pass: create parent items
        for item_data in navigation_items:
            if item_data['parent'] is None:
                item, created = NavigationItem.objects.get_or_create(
                    name=item_data['name'],
                    defaults={
                        'display_name': item_data['display_name'],
                        'url_name': item_data['url_name'],
                        'icon': item_data['icon'],
                        'order': item_data['order'],
                        'is_active': True,
                        'parent': None
                    }
                )
                created_items[item_data['name']] = item
                if created:
                    self.stdout.write(f'Created parent item: {item.display_name}')
                else:
                    self.stdout.write(f'Found existing parent item: {item.display_name}')
        
        # Second pass: create child items
        for item_data in navigation_items:
            if item_data['parent'] is not None:
                parent = created_items.get(item_data['parent'])
                if parent:
                    item, created = NavigationItem.objects.get_or_create(
                        name=item_data['name'],
                        defaults={
                            'display_name': item_data['display_name'],
                            'url_name': item_data['url_name'],
                            'icon': item_data['icon'],
                            'order': item_data['order'],
                            'is_active': True,
                            'parent': parent
                        }
                    )
                    created_items[item_data['name']] = item
                    if created:
                        self.stdout.write(f'Created child item: {item.display_name} under {parent.display_name}')
                    else:
                        self.stdout.write(f'Found existing child item: {item.display_name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated navigation items!')
        )
