"""
Script to add visit cost to all house properties that don't have one set.
Default visit cost: 5,000 Tsh (can be adjusted)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property, PropertyType
from decimal import Decimal
from django.db import models

# Default visit cost (in Tsh)
DEFAULT_VISIT_COST = Decimal('5000.00')

def add_visit_cost_to_houses(visit_cost=None):
    """Add visit cost to all house properties that don't have one set."""
    if visit_cost is None:
        visit_cost = DEFAULT_VISIT_COST
    
    # Get house property type
    house_type = PropertyType.objects.filter(name__iexact='house').first()
    
    if not house_type:
        print("Error: 'House' property type not found!")
        return
    
    # Get all house properties without visit cost (None or 0)
    houses = Property.objects.filter(
        property_type=house_type
    ).filter(
        models.Q(visit_cost__isnull=True) | models.Q(visit_cost=0)
    )
    
    count = houses.count()
    
    if count == 0:
        print("No house properties found that need visit cost set.")
        return
    
    print(f"Found {count} house properties without visit cost.")
    print(f"Setting visit cost to Tsh {visit_cost:,.2f} for all of them...")
    print("-" * 60)
    
    updated = 0
    for house in houses:
        house.visit_cost = visit_cost
        house.save(update_fields=['visit_cost'])
        updated += 1
        print(f"✓ Updated: {house.title} (ID: {house.id})")
    
    print("-" * 60)
    print(f"Successfully updated {updated} house properties with visit cost of Tsh {visit_cost:,.2f}")
    
    # Show summary
    total_houses = Property.objects.filter(property_type=house_type).count()
    houses_with_cost = Property.objects.filter(
        property_type=house_type
    ).exclude(visit_cost__isnull=True).exclude(visit_cost=0).count()
    
    print(f"\nSummary:")
    print(f"  Total house properties: {total_houses}")
    print(f"  Houses with visit cost: {houses_with_cost}")
    print(f"  Houses without visit cost: {total_houses - houses_with_cost}")

if __name__ == "__main__":
    add_visit_cost_to_houses()

