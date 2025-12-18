from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.db.models import Count
from collections import defaultdict


class Command(BaseCommand):
    help = 'Check for duplicate permissions and identify issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Remove duplicate permissions (keeps the first one)',
        )

    def handle(self, *args, **options):
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('CHECKING FOR DUPLICATE PERMISSIONS')
        self.stdout.write('=' * 70 + '\n')
        
        # Get all permissions grouped by app_label and codename
        all_perms = Permission.objects.all().order_by('id')
        
        # Group by (app_label, codename) - case insensitive
        grouped = defaultdict(list)
        for perm in all_perms:
            key = (perm.content_type.app_label.lower(), perm.codename.lower())
            grouped[key].append(perm)
        
        # Find duplicates
        duplicates_found = []
        for key, perms in grouped.items():
            if len(perms) > 1:
                duplicates_found.append((key, perms))
        
        if not duplicates_found:
            self.stdout.write(self.style.SUCCESS('[OK] No duplicate permissions found!'))
            self.stdout.write('\nTotal permissions: {}'.format(all_perms.count()))
            return
        
        self.stdout.write(self.style.WARNING(f'[WARNING] Found {len(duplicates_found)} sets of duplicate permissions:\n'))
        
        total_duplicates = 0
        for (app_label, codename), perms in duplicates_found:
            total_duplicates += len(perms) - 1  # Keep one, remove the rest
            self.stdout.write(f'\n{app_label}.{codename} ({len(perms)} duplicates):')
            for perm in perms:
                roles_count = perm.customrole_set.count()
                self.stdout.write(f'  ID {perm.id}: "{perm.name}" (used by {roles_count} roles)')
        
        self.stdout.write(f'\n[INFO] Total duplicate permissions to remove: {total_duplicates}')
        
        if options['fix']:
            self.stdout.write('\n' + '-' * 70)
            self.stdout.write('REMOVING DUPLICATES (keeping the first one)...')
            self.stdout.write('-' * 70 + '\n')
            
            removed_count = 0
            for (app_label, codename), perms in duplicates_found:
                # Keep the first one (lowest ID)
                keep_perm = perms[0]
                remove_perms = perms[1:]
                
                for perm in remove_perms:
                    # Transfer role assignments to the kept permission
                    roles = perm.customrole_set.all()
                    for role in roles:
                        if keep_perm not in role.permissions.all():
                            role.permissions.add(keep_perm)
                        role.permissions.remove(perm)
                    
                    # Delete the duplicate
                    perm.delete()
                    removed_count += 1
                    self.stdout.write(f'  [REMOVED] ID {perm.id}: "{perm.name}"')
            
            self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Removed {removed_count} duplicate permissions'))
            self.stdout.write(f'Remaining permissions: {Permission.objects.count()}')
        else:
            self.stdout.write('\n[INFO] Run with --fix to remove duplicates')
            self.stdout.write('Example: python manage.py check_duplicate_permissions --fix')

