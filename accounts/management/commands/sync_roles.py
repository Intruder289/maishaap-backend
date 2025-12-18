from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from accounts.models import CustomRole, Profile
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Synchronize default roles and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Starting role synchronization...')
        
        # Create default roles with their permissions
        self.create_default_roles()
        
        # Sync Django Groups with CustomRoles
        self.sync_groups_with_roles()
        
        self.stdout.write(self.style.SUCCESS('Role synchronization completed successfully!'))

    def create_default_roles(self):
        """Create default roles with appropriate permissions"""
        
        # Define default roles and their permissions
        default_roles = {
            'Admin': {
                'description': 'Full system administrator with all permissions',
                'permissions': [
                    # User management
                    'auth.add_user', 'auth.change_user', 'auth.delete_user', 'auth.view_user',
                    'auth.add_group', 'auth.change_group', 'auth.delete_group', 'auth.view_group',
                    'auth.add_permission', 'auth.change_permission', 'auth.delete_permission', 'auth.view_permission',
                    
                    # Profile management
                    'accounts.add_profile', 'accounts.change_profile', 'accounts.delete_profile', 'accounts.view_profile',
                    
                    # Role management
                    'accounts.add_customrole', 'accounts.change_customrole', 'accounts.delete_customrole', 'accounts.view_customrole',
                    
                    # Admin interface
                    'admin.view_logentry', 'admin.add_logentry', 'admin.change_logentry', 'admin.delete_logentry',
                    
                    # Content types
                    'contenttypes.add_contenttype', 'contenttypes.change_contenttype', 'contenttypes.delete_contenttype', 'contenttypes.view_contenttype',
                    
                    # Sessions
                    'sessions.add_session', 'sessions.change_session', 'sessions.delete_session', 'sessions.view_session',
                ]
            },
            'Manager': {
                'description': 'Property manager with limited user management permissions - can only view and manage users they created',
                'permissions': [
                    # User management - can create users (for registering property owners)
                    'auth.add_user', 'auth.view_user', 'auth.change_user',
                    
                    # Profile management
                    'accounts.add_profile', 'accounts.change_profile', 'accounts.view_profile',
                    
                    # Property management - view all properties (for oversight)
                    'properties.view_property',
                    
                    # Booking management - view all bookings
                    'properties.view_booking',
                    
                    # Room management - view all rooms
                    'properties.view_room',
                    
                    # Payment management - view all payments
                    'payments.view_payment',
                    
                    # Maintenance management - view all maintenance requests
                    'maintenance.view_maintenancerequest',
                    
                    # Reports - view all reports
                    'reports.view_generatedreport',
                    'reports.view_financialsummary',
                    
                    # Document/Lease management - view all leases
                    'documents.view_lease',
                ]
            },
            'Property owner': {
                'description': 'Property owner with limited property and tenant management permissions',
                'permissions': [
                    # Very limited permissions - mainly view own data
                    'auth.view_user',
                    'accounts.view_profile', 'accounts.change_profile',
                    
                    # Property management - view own properties
                    'properties.view_property',  # Required for hotel_dashboard, lodge_dashboard, venue_dashboard, house_dashboard
                    'properties.add_property',  # Allow owners to create properties
                    'properties.change_property',  # Allow owners to edit their properties
                    
                    # Booking management - view own bookings
                    'properties.view_booking',  # Required for hotel_bookings, lodge_bookings, venue_bookings, house_bookings
                    
                    # Room management - view own rooms
                    'properties.view_room',  # Required for hotel_rooms, lodge_rooms
                    
                    # Payment management - view own payments
                    'payments.view_payment',  # Required for hotel_payments, lodge_payments, venue_payments, house_payments
                    
                    # Reports - view own reports
                    'reports.view_generatedreport',  # Required for hotel_reports, lodge_reports, venue_reports, house_reports
                    'reports.view_financialsummary',  # View financial summary reports
                    
                    # Lease management - view own leases
                    'documents.view_lease',  # Required for house_tenants
                ]
            }
        }
        
        for role_name, role_data in default_roles.items():
            # Create or update the role
            role, created = CustomRole.objects.get_or_create(
                name=role_name,
                defaults={'description': role_data['description']}
            )
            
            if created:
                self.stdout.write(f'Created role: {role_name}')
            else:
                role.description = role_data['description']
                role.save()
                self.stdout.write(f'Updated role: {role_name}')
            
            # Clear existing permissions and add new ones
            role.permissions.clear()
            
            permissions_added = 0
            for perm_code in role_data['permissions']:
                try:
                    app_label, codename = perm_code.split('.')
                    permission = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    role.permissions.add(permission)
                    permissions_added += 1
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Permission not found: {perm_code}')
                    )
                except ValueError:
                    self.stdout.write(
                        self.style.WARNING(f'Invalid permission format: {perm_code}')
                    )
            
            self.stdout.write(f'Added {permissions_added} permissions to {role_name}')

    def sync_groups_with_roles(self):
        """Sync Django Groups with CustomRoles for backward compatibility"""
        
        for role in CustomRole.objects.all():
            # Create corresponding Django Group
            group, created = Group.objects.get_or_create(name=role.name)
            
            if created:
                self.stdout.write(f'Created Django group: {role.name}')
            
            # Clear existing group permissions and sync with role permissions
            group.permissions.clear()
            group.permissions.set(role.permissions.all())
            
            self.stdout.write(f'Synced permissions for group: {role.name}')

        # Handle legacy "Property manager" vs "Manager" naming
        try:
            manager_role = CustomRole.objects.get(name='Manager')
            # Also create "Property manager" group for backward compatibility
            prop_manager_group, created = Group.objects.get_or_create(name='Property manager')
            if created:
                self.stdout.write('Created legacy "Property manager" group')
            prop_manager_group.permissions.set(manager_role.permissions.all())
        except CustomRole.DoesNotExist:
            pass