from django.core.management.base import BaseCommand
from django.db import transaction, models
from django.utils import timezone
from properties.models import Property


class Command(BaseCommand):
    help = 'Update all properties created by admin/staff to have is_active=True and is_approved=True'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        # Find all properties owned by admin/staff users
        admin_properties = Property.objects.filter(
            owner__is_staff=True
        ) | Property.objects.filter(
            owner__is_superuser=True
        )
        
        # Get distinct properties (in case owner is both staff and superuser)
        admin_properties = admin_properties.distinct()
        
        # Filter properties that need updating
        properties_to_update = admin_properties.filter(
            models.Q(is_active=False) | models.Q(is_approved=False)
        )
        
        updated_count = 0
        
        with transaction.atomic():
            for property_obj in properties_to_update:
                needs_update = False
                updates = []
                
                if not property_obj.is_active:
                    needs_update = True
                    updates.append('is_active=True')
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Would update property "{property_obj.title}" (ID: {property_obj.id}): '
                                f'is_active=False -> is_active=True'
                            )
                        )
                    else:
                        property_obj.is_active = True
                
                if not property_obj.is_approved:
                    needs_update = True
                    updates.append('is_approved=True')
                    if not property_obj.approved_by:
                        updates.append('approved_by=owner')
                    if not property_obj.approved_at:
                        updates.append('approved_at=now')
                    
                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Would update property "{property_obj.title}" (ID: {property_obj.id}): '
                                f'is_approved=False -> is_approved=True'
                            )
                        )
                    else:
                        property_obj.is_approved = True
                        if not property_obj.approved_by:
                            property_obj.approved_by = property_obj.owner
                        if not property_obj.approved_at:
                            property_obj.approved_at = timezone.now()
                
                if needs_update and not dry_run:
                    property_obj.save(update_fields=['is_active', 'is_approved', 'approved_by', 'approved_at'])
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated property "{property_obj.title}" (ID: {property_obj.id}): {", ".join(updates)}'
                        )
                    )
                elif needs_update and dry_run:
                    updated_count += 1
        
        total_admin_properties = admin_properties.count()
        already_correct = total_admin_properties - properties_to_update.count()
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nDry run complete:\n'
                    f'  - Total admin properties: {total_admin_properties}\n'
                    f'  - Already correct: {already_correct}\n'
                    f'  - Would update: {updated_count}'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully updated {updated_count} admin properties.\n'
                    f'  - Total admin properties: {total_admin_properties}\n'
                    f'  - Already correct: {already_correct}\n'
                    f'  - Updated: {updated_count}'
                )
            )

