from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import CustomRole, UserRole


class Command(BaseCommand):
    help = 'Assign roles to users'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to assign role to')
        parser.add_argument('--role', type=str, help='Role name to assign')
        parser.add_argument('--list-roles', action='store_true', help='List all available roles')
        parser.add_argument('--list-users', action='store_true', help='List all users and their roles')

    def handle(self, *args, **options):
        if options['list_roles']:
            self.list_roles()
        elif options['list_users']:
            self.list_users()
        elif options['username'] and options['role']:
            self.assign_role(options['username'], options['role'])
        else:
            self.stdout.write(self.style.ERROR('Please provide --username and --role, or use --list-roles or --list-users'))

    def list_roles(self):
        self.stdout.write('Available roles:')
        for role in CustomRole.objects.all():
            self.stdout.write(f'- {role.name}: {role.description}')

    def list_users(self):
        self.stdout.write('Users and their roles:')
        for user in User.objects.all():
            roles = UserRole.objects.filter(user=user).values_list('role__name', flat=True)
            roles_str = ', '.join(roles) if roles else 'No roles assigned'
            self.stdout.write(f'- {user.username} ({user.email}): {roles_str}')

    def assign_role(self, username, role_name):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return

        try:
            role = CustomRole.objects.get(name=role_name)
        except CustomRole.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Role "{role_name}" not found'))
            return

        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Role "{role_name}" assigned to "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'User "{username}" already has role "{role_name}"'))