"""
Django management command to add visit cost to all house properties.
Usage: python manage.py add_visit_cost_to_houses [--cost=5000]
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from decimal import Decimal
from properties.models import Property, PropertyType


class Command(BaseCommand):
    help = 'Add visit cost to all house properties that don\'t have one set'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cost',
            type=float,
            default=5000.0,
            help='Visit cost amount in Tsh (default: 5000)',
        )

    def handle(self, *args, **options):
        visit_cost = Decimal(str(options['cost']))
        
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('Adding Visit Cost to All House Properties'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Get house property type
        house_type = PropertyType.objects.filter(name__iexact='house').first()
        
        if not house_type:
            self.stdout.write(self.style.ERROR("ERROR: 'House' property type not found!"))
            return
        
        self.stdout.write(f"\nProperty Type: {house_type.name} (ID: {house_type.id})")
        
        # Get all house properties
        all_houses = Property.objects.filter(property_type=house_type)
        total_count = all_houses.count()
        self.stdout.write(f"Total house properties: {total_count}")
        
        # Get houses without visit cost
        houses_to_update = all_houses.filter(Q(visit_cost__isnull=True) | Q(visit_cost=0))
        count = houses_to_update.count()
        
        self.stdout.write(f"House properties without visit cost: {count}")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("\n✓ All house properties already have visit cost set!"))
            return
        
        self.stdout.write(f"\nSetting visit cost to Tsh {visit_cost:,.2f}...")
        self.stdout.write('-' * 60)
        
        updated = 0
        for house in houses_to_update:
            house.visit_cost = visit_cost
            house.save(update_fields=['visit_cost'])
            updated += 1
            self.stdout.write(
                self.style.SUCCESS(f"[{updated}] {house.title} (ID: {house.id}) - Set to Tsh {visit_cost:,.2f}")
            )
        
        self.stdout.write('-' * 60)
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Successfully updated {updated} house properties!")
        )
        self.stdout.write(f"  Visit cost set to: Tsh {visit_cost:,.2f}")
        
        # Final summary
        houses_with_cost = Property.objects.filter(
            property_type=house_type
        ).exclude(visit_cost__isnull=True).exclude(visit_cost=0).count()
        
        self.stdout.write(f"\nFinal Summary:")
        self.stdout.write(f"  Total house properties: {total_count}")
        self.stdout.write(f"  Houses with visit cost: {houses_with_cost}")
        self.stdout.write(f"  Houses without visit cost: {total_count - houses_with_cost}")
        self.stdout.write(self.style.SUCCESS('=' * 60))



