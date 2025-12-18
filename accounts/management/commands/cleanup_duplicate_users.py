from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from collections import Counter
from django.db import transaction

class Command(BaseCommand):
    help = 'Clean up duplicate users with the same email address'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Find duplicate emails
        all_users = User.objects.all()
        email_counts = Counter(user.email for user in all_users if user.email)
        
        duplicates = {email: count for email, count in email_counts.items() if count > 1}
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate email addresses found.'))
            return

        self.stdout.write(f'Found {len(duplicates)} email addresses with duplicates:')
        
        users_to_delete = []
        
        for email, count in duplicates.items():
            self.stdout.write(f'\nEmail: {email} ({count} users)')
            
            # Get all users with this email, ordered by date_joined (newest first)
            duplicate_users = User.objects.filter(email=email).order_by('-date_joined')
            
            # Keep the newest user, mark others for deletion
            keeper = duplicate_users.first()
            to_delete = duplicate_users[1:]
            
            self.stdout.write(f'  ✓ KEEPING: {keeper.username} (joined: {keeper.date_joined})')
            
            for user in to_delete:
                self.stdout.write(f'  ✗ DELETE: {user.username} (joined: {user.date_joined})')
                users_to_delete.append(user)

        if dry_run:
            self.stdout.write(f'\n{self.style.WARNING("DRY RUN MODE - No users were actually deleted.")}')
            self.stdout.write(f'Would delete {len(users_to_delete)} duplicate users.')
            self.stdout.write('Run without --dry-run to actually delete the duplicates.')
        else:
            # Confirm deletion
            self.stdout.write(f'\n{self.style.WARNING(f"About to delete {len(users_to_delete)} duplicate users.")}')
            
            try:
                with transaction.atomic():
                    deleted_count = 0
                    for user in users_to_delete:
                        user.delete()
                        deleted_count += 1
                        self.stdout.write(f'  Deleted: {user.username}')
                    
                    self.stdout.write(f'\n{self.style.SUCCESS(f"Successfully deleted {deleted_count} duplicate users.")}')
                    
            except Exception as e:
                self.stdout.write(f'\n{self.style.ERROR(f"Error during deletion: {str(e)}")}')