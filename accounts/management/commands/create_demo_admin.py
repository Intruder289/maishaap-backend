from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create or update a demo admin user (development only)'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin', help='Username for demo admin')
        parser.add_argument('--email', default='admin@example.com', help='Email for demo admin')
        parser.add_argument('--password', default='AdminPass123!', help='Password for demo admin')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        email = options['email']
        password = options['password']

        user, created = User.objects.update_or_create(
            username=username,
            defaults={'email': email, 'is_superuser': True, 'is_staff': True},
        )
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created demo admin user: {username} / {password}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated demo admin user: {username} / {password}'))
