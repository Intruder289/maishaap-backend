from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Fix test user password if login is not working'

    def handle(self, *args, **options):
        self.stdout.write('Checking and fixing test user...')
        
        try:
            user = User.objects.get(username='testuser')
            self.stdout.write(f'Found user: {user.username}')
            
            # Reset password
            user.set_password('testpass123')
            user.is_active = True
            user.is_superuser = False
            user.is_staff = False
            user.save()
            
            # Ensure profile is approved
            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_approved = True
            profile.save()
            
            self.stdout.write(self.style.SUCCESS('Password reset successfully!'))
            self.stdout.write('\nLogin credentials:')
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write('   Password: testpass123')
            self.stdout.write(f'   Is Active: {user.is_active}')
            self.stdout.write(f'   Is Superuser: {user.is_superuser}')
            self.stdout.write(f'   Profile Approved: {profile.is_approved}')
            
            # Verify password
            if user.check_password('testpass123'):
                self.stdout.write(self.style.SUCCESS('\nPassword verification: SUCCESS'))
            else:
                self.stdout.write(self.style.ERROR('\nPassword verification: FAILED'))
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User "testuser" not found!'))
            self.stdout.write('Run: python manage.py create_test_user_with_limited_permissions')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

