from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Initialize default roles (Admin, Property manager, Property owner) and assign permissions.'

    def add_arguments(self, parser):
        parser.add_argument('--assign-manager', action='store_true', help='Give manager some app permissions (optional)')
        parser.add_argument('--assign-owner', action='store_true', help='Give property owner some app permissions (optional)')

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        manager_group, _ = Group.objects.get_or_create(name='Property manager')
        owner_group, _ = Group.objects.get_or_create(name='Property owner')

        # Assign all permissions to Admin
        all_perms = Permission.objects.all()
        admin_group.permissions.set(all_perms)
        self.stdout.write(self.style.SUCCESS(f'Assigned {all_perms.count()} permissions to Admin'))

        # Optionally give Manager or Property owner a subset of permissions
        if options.get('assign_manager'):
            # Example: give Property manager add/change/view on models in 'accounts' app
            manager_perms = Permission.objects.filter(content_type__app_label__in=['accounts'])
            manager_group.permissions.set(manager_perms)
            self.stdout.write(self.style.SUCCESS(f'Assigned {manager_perms.count()} accounts permissions to Property manager'))

        if options.get('assign_owner'):
            # Example: give Property owner limited view/add permissions on certain apps
            owner_perms = Permission.objects.filter(content_type__app_label__in=['accounts'])
            owner_group.permissions.set(owner_perms)
            self.stdout.write(self.style.SUCCESS(f'Assigned {owner_perms.count()} accounts permissions to Property owner'))

        self.stdout.write(self.style.SUCCESS('Roles initialization complete.'))
