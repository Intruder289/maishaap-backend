from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from collections import defaultdict


class Command(BaseCommand):
    help = 'Analyze permissions to find duplicates by name (different apps)'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('ANALYZING PERMISSIONS FOR DUPLICATE NAMES')
        self.stdout.write('=' * 70 + '\n')
        
        all_perms = Permission.objects.all().order_by('content_type__app_label', 'codename')
        
        # Group by permission name (case-insensitive)
        by_name = defaultdict(list)
        for perm in all_perms:
            by_name[perm.name.lower()].append(perm)
        
        # Find permissions with same name but different apps
        duplicates = {name: perms for name, perms in by_name.items() if len(perms) > 1}
        
        if duplicates:
            self.stdout.write(self.style.WARNING(f'Found {len(duplicates)} permission names that appear in multiple apps:\n'))
            
            for name, perms in sorted(duplicates.items()):
                if len(set(p.content_type.app_label for p in perms)) > 1:
                    self.stdout.write(f'\n"{perms[0].name}" appears in {len(perms)} places:')
                    for perm in perms:
                        self.stdout.write(f'  - {perm.content_type.app_label}.{perm.codename} (ID: {perm.id})')
        else:
            self.stdout.write(self.style.SUCCESS('[OK] No duplicate permission names found'))
        
        # Check for similar names (case variations)
        self.stdout.write('\n' + '-' * 70)
        self.stdout.write('Checking for case variations...\n')
        
        similar = defaultdict(list)
        for perm in all_perms:
            key = perm.name.lower().strip()
            similar[key].append(perm)
        
        case_duplicates = {name: perms for name, perms in similar.items() if len(perms) > 1 and len(set(p.name for p in perms)) > 1}
        
        if case_duplicates:
            self.stdout.write(self.style.WARNING(f'Found {len(case_duplicates)} permissions with case variations:\n'))
            for name, perms in list(case_duplicates.items())[:10]:
                self.stdout.write(f'\n"{name}":')
                for perm in perms:
                    self.stdout.write(f'  - "{perm.name}" ({perm.content_type.app_label}.{perm.codename})')
        else:
            self.stdout.write('[OK] No case variations found')
        
        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(f'Total permissions: {all_perms.count()}')
        self.stdout.write(f'Unique permission names: {len(by_name)}')
        self.stdout.write(f'Permissions with duplicate names: {len(duplicates)}')
        self.stdout.write('=' * 70 + '\n')

