#!/usr/bin/env python
"""Update all house properties with visit cost"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, PropertyType
from django.db.models import Q
from decimal import Decimal

# Set visit cost amount
VISIT_COST = Decimal('5000.00')

print("=" * 60)
print("Adding Visit Cost to All House Properties")
print("=" * 60)

# Get house property type
house_type = PropertyType.objects.filter(name__iexact='house').first()

if not house_type:
    print("ERROR: 'House' property type not found!")
    sys.exit(1)

print(f"\nProperty Type: {house_type.name} (ID: {house_type.id})")

# Get all house properties
all_houses = Property.objects.filter(property_type=house_type)
print(f"Total house properties: {all_houses.count()}")

# Get houses without visit cost
houses_to_update = all_houses.filter(Q(visit_cost__isnull=True) | Q(visit_cost=0))
count = houses_to_update.count()

print(f"House properties without visit cost: {count}")

if count == 0:
    print("\nAll house properties already have visit cost set!")
    sys.exit(0)

print(f"\nSetting visit cost to Tsh {VISIT_COST:,.2f}...")
print("-" * 60)

updated = 0
for house in houses_to_update:
    old_cost = house.visit_cost
    house.visit_cost = VISIT_COST
    house.save(update_fields=['visit_cost'])
    updated += 1
    print(f"[{updated}] {house.title} (ID: {house.id}) - Set to Tsh {VISIT_COST:,.2f}")

print("-" * 60)
print(f"\n✓ Successfully updated {updated} house properties!")
print(f"  Visit cost set to: Tsh {VISIT_COST:,.2f}")

# Final summary
houses_with_cost = Property.objects.filter(
    property_type=house_type
).exclude(visit_cost__isnull=True).exclude(visit_cost=0).count()

print(f"\nFinal Summary:")
print(f"  Total house properties: {all_houses.count()}")
print(f"  Houses with visit cost: {houses_with_cost}")
print(f"  Houses without visit cost: {all_houses.count() - houses_with_cost}")
print("=" * 60)



