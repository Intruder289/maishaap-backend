from django.core.management.base import BaseCommand
from django.db import transaction
from properties.models import PropertyType, Property


class Command(BaseCommand):
    help = 'Fix duplicate PropertyType entries by standardizing to lowercase and merging properties'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Standardize to lowercase
        # Strategy: Keep lowercase versions, merge properties from capitalized versions to lowercase
        
        # Find all property types
        all_types = PropertyType.objects.all()
        
        # Group by lowercase name
        from collections import defaultdict
        type_groups = defaultdict(list)
        
        for prop_type in all_types:
            type_groups[prop_type.name.lower()].append(prop_type)
        
        merged_count = 0
        deleted_count = 0
        renamed_count = 0
        
        with transaction.atomic():
            for lowercase_name, types_list in type_groups.items():
                if len(types_list) > 1:
                    # Multiple types with same lowercase name - need to merge
                    self.stdout.write(f'\nFound duplicates for "{lowercase_name}":')
                    
                    # Find the lowercase version (preferred) or use the first one
                    lowercase_type = None
                    capitalized_types = []
                    
                    for pt in types_list:
                        if pt.name == lowercase_name:
                            lowercase_type = pt
                        else:
                            capitalized_types.append(pt)
                    
                    # If no lowercase version exists, use the first one and rename it
                    if not lowercase_type:
                        lowercase_type = types_list[0]
                        if lowercase_type.name != lowercase_name:
                            if dry_run:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'  Would rename "{lowercase_type.name}" (ID: {lowercase_type.id}) to "{lowercase_name}"'
                                    )
                                )
                            else:
                                lowercase_type.name = lowercase_name
                                lowercase_type.save()
                                renamed_count += 1
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'  ✓ Renamed "{types_list[0].name}" to "{lowercase_name}"'
                                    )
                                )
                    
                    # Merge properties from capitalized versions to lowercase version
                    for cap_type in capitalized_types:
                        properties_count = Property.objects.filter(property_type=cap_type).count()
                        
                        if properties_count > 0:
                            if dry_run:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'  Would move {properties_count} properties from "{cap_type.name}" (ID: {cap_type.id}) to "{lowercase_name}" (ID: {lowercase_type.id})'
                                    )
                                )
                                merged_count += properties_count
                            else:
                                Property.objects.filter(property_type=cap_type).update(property_type=lowercase_type)
                                merged_count += properties_count
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'  ✓ Moved {properties_count} properties from "{cap_type.name}" to "{lowercase_name}"'
                                    )
                                )
                        
                        # Delete the duplicate
                        if dry_run:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  Would delete duplicate PropertyType: "{cap_type.name}" (ID: {cap_type.id})'
                                )
                            )
                            deleted_count += 1
                        else:
                            cap_type.delete()
                            deleted_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Deleted duplicate PropertyType: "{cap_type.name}" (ID: {cap_type.id})'
                                )
                            )
                else:
                    # Single type - just ensure it's lowercase
                    prop_type = types_list[0]
                    if prop_type.name != prop_type.name.lower():
                        if dry_run:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Would rename "{prop_type.name}" (ID: {prop_type.id}) to "{prop_type.name.lower()}"'
                                )
                            )
                            renamed_count += 1
                        else:
                            old_name = prop_type.name
                            prop_type.name = prop_type.name.lower()
                            prop_type.save()
                            renamed_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Renamed "{old_name}" to "{prop_type.name.lower()}"'
                                )
                            )
            
            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nDry run complete. Would rename {renamed_count} types, merge {merged_count} properties, and delete {deleted_count} duplicates.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Successfully standardized PropertyTypes:'
                        f'\n  - Renamed: {renamed_count}'
                        f'\n  - Properties merged: {merged_count}'
                        f'\n  - Duplicates deleted: {deleted_count}'
                    )
                )
                
                # Show final state
                self.stdout.write('\nFinal PropertyTypes:')
                for pt in PropertyType.objects.all().order_by('name'):
                    prop_count = Property.objects.filter(property_type=pt).count()
                    self.stdout.write(f'  - {pt.name} (ID: {pt.id}, {prop_count} properties)')

