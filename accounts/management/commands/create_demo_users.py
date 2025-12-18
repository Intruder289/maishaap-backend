from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Create demo Property manager and Property owner users and assign them to correct groups.'

    def add_arguments(self, parser):
        parser.add_argument('--manager-username', default='pmanager', help='Username for demo Property manager')
        parser.add_argument('--owner-username', default='powner', help='Username for demo Property owner')
        parser.add_argument('--password', default='UserPass123!', help='Password for demo users')

    def handle(self, *args, **options):
        User = get_user_model()
        manager_username = options['manager_username']
        owner_username = options['owner_username']
        password = options['password']

        # Ensure groups exist
        manager_group, _ = Group.objects.get_or_create(name='Property manager')
        owner_group, _ = Group.objects.get_or_create(name='Property owner')

        m, m_created = User.objects.update_or_create(username=manager_username, defaults={'email': f'{manager_username}@example.com', 'is_staff': False})
        m.set_password(password)
        m.save()
        m.groups.add(manager_group)

        o, o_created = User.objects.update_or_create(username=owner_username, defaults={'email': f'{owner_username}@example.com', 'is_staff': False})
        o.set_password(password)
        o.save()
        o.groups.add(owner_group)

        self.stdout.write(self.style.SUCCESS(f'Created/updated Property manager: {manager_username} / {password}'))
        self.stdout.write(self.style.SUCCESS(f'Created/updated Property owner: {owner_username} / {password}'))
