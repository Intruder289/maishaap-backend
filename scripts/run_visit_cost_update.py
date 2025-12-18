#!/usr/bin/env python
"""Run visit cost update and save output to file"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')

import django
django.setup()

from properties.models import Property, PropertyType
from django.db.models import Q
from decimal import Decimal

VISIT_COST = Decimal('5000.00')
output_file = 'visit_cost_update_results.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('=' * 60 + '\n')
    f.write('Adding Visit Cost to All House Properties\n')
    f.write('=' * 60 + '\n\n')
    
    house_type = PropertyType.objects.filter(name__iexact='house').first()
    
    if not house_type:
        f.write("ERROR: 'House' property type not found!\n")
        sys.exit(1)
    
    f.write(f"Property Type: {house_type.name} (ID: {house_type.id})\n\n")
    
    all_houses = Property.objects.filter(property_type=house_type)
    total_count = all_houses.count()
    f.write(f"Total house properties: {total_count}\n")
    
    houses_to_update = all_houses.filter(Q(visit_cost__isnull=True) | Q(visit_cost=0))
    count = houses_to_update.count()
    f.write(f"House properties without visit cost: {count}\n\n")
    
    if count == 0:
        f.write("✓ All house properties already have visit cost set!\n")
    else:
        f.write(f"Setting visit cost to Tsh {VISIT_COST:,.2f}...\n")
        f.write('-' * 60 + '\n')
        
        updated = 0
        for house in houses_to_update:
            house.visit_cost = VISIT_COST
            house.save(update_fields=['visit_cost'])
            updated += 1
            f.write(f"[{updated}] {house.title} (ID: {house.id}) - Set to Tsh {VISIT_COST:,.2f}\n")
            print(f"Updated: {house.title} (ID: {house.id})")
        
        f.write('-' * 60 + '\n')
        f.write(f"\n✓ Successfully updated {updated} house properties!\n")
        f.write(f"  Visit cost set to: Tsh {VISIT_COST:,.2f}\n")
        
        houses_with_cost = Property.objects.filter(
            property_type=house_type
        ).exclude(visit_cost__isnull=True).exclude(visit_cost=0).count()
        
        f.write(f"\nFinal Summary:\n")
        f.write(f"  Total house properties: {total_count}\n")
        f.write(f"  Houses with visit cost: {houses_with_cost}\n")
        f.write(f"  Houses without visit cost: {total_count - houses_with_cost}\n")
    
    f.write('=' * 60 + '\n')

print(f"\n✓ Update complete! Results saved to: {output_file}")
print("You can now check the property detail page to see the visit cost.")



