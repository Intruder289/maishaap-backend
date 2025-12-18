from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, UserRole


class Command(BaseCommand):
    help = 'Display test user login credentials'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('TEST USER LOGIN CREDENTIALS')
        self.stdout.write('=' * 60)
        
        try:
            user = User.objects.get(username='testuser')
            profile = Profile.objects.get(user=user)
            roles = UserRole.objects.filter(user=user)
            
            self.stdout.write('\nIMPORTANT: Login uses EMAIL, not username!')
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write('LOGIN CREDENTIALS:')
            self.stdout.write('=' * 60)
            self.stdout.write(f'\nEmail:    {self.style.SUCCESS(user.email)}')
            self.stdout.write(f'Password: {self.style.SUCCESS("testpass123")}')
            self.stdout.write(f'\nUsername: {user.username} (for reference only)')
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write('USER STATUS:')
            self.stdout.write('=' * 60)
            self.stdout.write(f'Is Active:     {user.is_active}')
            self.stdout.write(f'Is Superuser:  {user.is_superuser} (should be False)')
            self.stdout.write(f'Is Staff:      {user.is_staff}')
            self.stdout.write(f'Profile Approved: {profile.is_approved}')
            
            if roles.exists():
                self.stdout.write(f'\nAssigned Roles:')
                for ur in roles:
                    self.stdout.write(f'  - {ur.role.name}')
            
            # Verify password
            if user.check_password('testpass123'):
                self.stdout.write(self.style.SUCCESS('\nPassword verification: SUCCESS'))
            else:
                self.stdout.write(self.style.ERROR('\nPassword verification: FAILED'))
                self.stdout.write('Run: python manage.py fix_test_user_password')
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write('HOW TO LOGIN:')
            self.stdout.write('=' * 60)
            self.stdout.write('1. Go to the login page')
            self.stdout.write(f'2. Enter Email: {user.email}')
            self.stdout.write('3. Enter Password: testpass123')
            self.stdout.write('4. Click "Sign In"')
            self.stdout.write('=' * 60 + '\n')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Test user not found!'))
            self.stdout.write('Run: python manage.py create_test_user_with_limited_permissions')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

