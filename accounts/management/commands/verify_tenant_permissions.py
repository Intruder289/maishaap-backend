from django.core.management.base import BaseCommand
from accounts.models import CustomRole
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Verify and display Tenant role permissions'

    def handle(self, *args, **options):
        try:
            tenant_role = CustomRole.objects.get(name='Tenant')
        except CustomRole.DoesNotExist:
            self.stdout.write(self.style.ERROR('Tenant role does not exist!'))
            return
        
        perms = tenant_role.permissions.all()
        count = perms.count()
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('TENANT ROLE PERMISSIONS VERIFICATION')
        self.stdout.write('=' * 70)
        self.stdout.write(f'\nRole: {tenant_role.name}')
        self.stdout.write(f'Total Django Permissions: {count}\n')
        
        if count == 0:
            self.stdout.write(self.style.WARNING('  [WARNING] No permissions assigned!'))
            self.stdout.write('  Run: python manage.py assign_tenant_django_permissions')
        elif count < 30:
            self.stdout.write(self.style.WARNING(f'  [WARNING] Only {count} permissions assigned (expected ~35)'))
            self.stdout.write('  Run: python manage.py assign_tenant_django_permissions')
        else:
            self.stdout.write(self.style.SUCCESS(f'  [OK] {count} permissions assigned'))
        
        # Group by app
        apps = {}
        for perm in perms.order_by('content_type__app_label', 'codename'):
            app = perm.content_type.app_label
            if app not in apps:
                apps[app] = []
            apps[app].append(perm)
        
        self.stdout.write('\nPermissions by App:')
        self.stdout.write('-' * 70)
        for app in sorted(apps.keys()):
            self.stdout.write(f'\n{app.upper()} ({len(apps[app])} permissions):')
            for perm in apps[app]:
                self.stdout.write(f'  - {perm.codename}')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'\nIf count is less than 35, run: python manage.py assign_tenant_django_permissions\n')

