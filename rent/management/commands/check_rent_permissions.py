from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserRole, CustomRole, Profile


class Command(BaseCommand):
    help = 'Check current user roles and rent navigation permissions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to check (defaults to first superuser)'
        )
    
    def handle(self, *args, **options):
        username = options.get('username')
        
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
                return
        else:
            # Get first superuser
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No superuser found'))
                return
        
        self.stdout.write(f'Checking user: {user.username} ({user.email})')
        self.stdout.write(f'Is superuser: {user.is_superuser}')
        self.stdout.write(f'Is staff: {user.is_staff}')
        
        # Check profile
        profile = getattr(user, 'profile', None)
        if profile:
            self.stdout.write(f'Profile role: {profile.role}')
            self.stdout.write(f'Is approved: {profile.is_approved}')
        
        # Check custom roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        if user_roles:
            self.stdout.write('Custom roles:')
            for user_role in user_roles:
                self.stdout.write(f'  - {user_role.role.name}')
        else:
            self.stdout.write('No custom roles assigned')
        
        # Check rent navigation permission
        from accounts.templatetags.navigation_tags import has_nav_permission
        has_rent_permission = has_nav_permission(user, 'rent')
        
        self.stdout.write(f'Has rent navigation permission: {has_rent_permission}')
        
        if user.is_superuser:
            self.stdout.write(self.style.SUCCESS('✓ User is superuser - has access to all navigation'))
        elif has_rent_permission:
            self.stdout.write(self.style.SUCCESS('✓ User has rent navigation permission'))
        else:
            self.stdout.write(self.style.WARNING('⚠ User does not have rent navigation permission'))
            self.stdout.write('To grant access, assign the user to "manager" or "System Administrator" role')