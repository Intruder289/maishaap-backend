from django.core.management.base import BaseCommand
from accounts.models import CustomRole, NavigationItem, RoleNavigationPermission


class Command(BaseCommand):
    help = 'Assign navigation permissions to Tenant role for mobile app and web interface access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--web-only',
            action='store_true',
            help='Only assign web interface navigation items (skip mobile app role check)',
        )

    def handle(self, *args, **options):
        self.stdout.write('Assigning permissions to Tenant role...\n')
        
        # Get or create Tenant role
        tenant_role, created = CustomRole.objects.get_or_create(
            name="Tenant",
            defaults={
                'description': 'Property tenant with mobile app access'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('[OK] Created Tenant role'))
        else:
            self.stdout.write('[OK] Found existing Tenant role')
        
        # Navigation items for web interface (optional - only if tenants use web admin)
        web_navigation_items = [
            'dashboard',
            'properties',
            'property_list',
            'rent',
            'maintenance',
            'complaints',
            'complaint_list',
            'create_complaint',
            'documents',
            'houses',
            'houses_list',
            'request_list',
            'feedback',
            'feedback_list',
            'give_feedback',
        ]
        
        if not options['web_only']:
            self.stdout.write('\n[Mobile App Access]')
            self.stdout.write('   [OK] Tenants can access all mobile app APIs if:')
            self.stdout.write('     - They have "Tenant" role (auto-assigned on mobile registration)')
            self.stdout.write('     - They are approved (is_approved=True)')
            self.stdout.write('     - They are authenticated (logged in via API)')
            self.stdout.write('   [OK] No Navigation Items needed for mobile app access\n')
        
        # Assign web interface navigation items
        self.stdout.write('[Web Interface Access - Navigation Items]')
        assigned_count = 0
        not_found = []
        
        for nav_name in web_navigation_items:
            try:
                nav_item = NavigationItem.objects.get(name=nav_name)
                permission, created = RoleNavigationPermission.objects.get_or_create(
                    role=tenant_role,
                    navigation_item=nav_item,
                    defaults={'can_access': True}
                )
                if created:
                    self.stdout.write(f'   [OK] Assigned: {nav_item.display_name}')
                    assigned_count += 1
                else:
                    self.stdout.write(f'   [SKIP] Already assigned: {nav_item.display_name}')
            except NavigationItem.DoesNotExist:
                not_found.append(nav_name)
        
        if not_found:
            self.stdout.write(self.style.WARNING(f'\n[WARNING] Navigation items not found: {", ".join(not_found)}'))
            self.stdout.write('   Run: python manage.py populate_navigation')
        
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Successfully assigned {assigned_count} navigation items to Tenant role'))
        self.stdout.write('\n[Summary]')
        self.stdout.write('   - Mobile App: Tenants can access all APIs (no navigation items needed)')
        self.stdout.write('   - Web Interface: Tenants can access assigned navigation items')
        self.stdout.write('\n[INFO] See TENANT_PERMISSIONS_GUIDE.md for full details')

