from django.core.management.base import BaseCommand
from accounts.models import CustomRole
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Assign all Django permissions to Tenant role for complete mobile app API access'

    def handle(self, *args, **options):
        self.stdout.write('Assigning Django permissions to Tenant role...\n')
        
        try:
            tenant_role = CustomRole.objects.get(name='Tenant')
        except CustomRole.DoesNotExist:
            self.stdout.write(self.style.ERROR('Tenant role does not exist!'))
            self.stdout.write('Run: python manage.py assign_tenant_permissions')
            return
        
        # Get current permissions
        current_perms = set(tenant_role.permissions.all())
        self.stdout.write(f'Current permissions: {len(current_perms)}\n')
        
        # Define all permissions needed for mobile app APIs
        # Based on the mobile app API endpoints, tenants need:
        
        # Properties app permissions
        property_perms = [
            'view_property',      # View all properties (houses, hotels, lodges, venues)
            'view_propertytype',  # View property types
            'view_region',       # View regions
            'view_amenity',      # View amenities
            'view_propertyimage', # View property images
            'view_propertyfavorite', # View/manage favorites
            'add_propertyfavorite',   # Add to favorites
            'delete_propertyfavorite', # Remove from favorites
            'view_booking',      # View bookings
            'add_booking',       # Create bookings
            'change_booking',    # Edit bookings
            'view_payment',      # View payments
            'view_room',         # View rooms
        ]
        
        # Rent app permissions
        rent_perms = [
            'view_rentinvoice',  # View rent invoices
            'view_rentpayment',  # View rent payments
            'view_latefee',     # View late fees
            'view_rentreminder', # View rent reminders
        ]
        
        # Payments app permissions
        payment_perms = [
            'view_paymentprovider', # View payment providers
            'view_invoice',         # View invoices
            'view_payment',         # View payments
            'add_payment',          # Create payments
            'view_paymenttransaction', # View transactions
            'view_expense',         # View expenses
        ]
        
        # Maintenance app permissions
        maintenance_perms = [
            'view_maintenancerequest', # View maintenance requests
            'add_maintenancerequest',  # Create maintenance requests
            'change_maintenancerequest', # Update maintenance requests
            'delete_maintenancerequest', # Delete maintenance requests
        ]
        
        # Complaints app permissions
        complaint_perms = [
            'view_complaint',    # View complaints
            'add_complaint',     # Create complaints
            'change_complaint',  # Update complaints
            'view_feedback',     # View feedback
            'add_feedback',      # Create feedback
        ]
        
        # Documents app permissions
        document_perms = [
            'view_lease',       # View leases
            'view_booking',      # View bookings (documents app)
            'add_booking',      # Create bookings (documents app)
            'change_booking',   # Edit bookings (documents app)
            'view_document',    # View documents
        ]
        
        # Accounts app permissions (for profile)
        account_perms = [
            'view_profile',     # View own profile
            'change_profile',   # Update own profile
        ]
        
        # Combine all permissions
        all_perm_codenames = (
            property_perms +
            rent_perms +
            payment_perms +
            maintenance_perms +
            complaint_perms +
            document_perms +
            account_perms
        )
        
        # Get all permissions
        assigned_count = 0
        not_found = []
        
        for codename in all_perm_codenames:
            # Try to find permission in different apps
            perm = None
            for app_label in ['properties', 'rent', 'payments', 'maintenance', 'complaints', 'documents', 'accounts']:
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename
                    )
                    break
                except Permission.DoesNotExist:
                    continue
            
            if perm:
                if perm not in current_perms:
                    tenant_role.permissions.add(perm)
                    assigned_count += 1
                    self.stdout.write(f'  [OK] Assigned: {perm.content_type.app_label}.{perm.codename} ({perm.name})')
            else:
                not_found.append(codename)
        
        if not_found:
            self.stdout.write(self.style.WARNING(f'\n[WARNING] Permissions not found: {", ".join(not_found)}'))
            self.stdout.write('  These may not exist in your database or have different names')
        
        # Get updated count
        updated_count = tenant_role.permissions.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Tenant role now has {updated_count} Django permissions'))
        self.stdout.write(f'  - Previously had: {len(current_perms)}')
        self.stdout.write(f'  - Newly assigned: {assigned_count}')
        self.stdout.write(f'  - Total now: {updated_count}')
        
        self.stdout.write('\n[IMPORTANT NOTE]')
        self.stdout.write('  Mobile app APIs use IsAuthenticated permission (not Django permissions)')
        self.stdout.write('  Django permissions are assigned for:')
        self.stdout.write('    1. Consistency and future use')
        self.stdout.write('    2. Web interface access (if needed)')
        self.stdout.write('    3. Admin panel operations')
        self.stdout.write('\n  Tenants can access mobile app APIs if they are:')
        self.stdout.write('    - Authenticated (logged in)')
        self.stdout.write('    - Have "Tenant" role')
        self.stdout.write('    - Are approved (is_approved=True)')

