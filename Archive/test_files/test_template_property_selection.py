#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from properties.models import Property
from django.template.loader import render_to_string

def test_property_selection_template():
    print("TESTING PROPERTY SELECTION TEMPLATE")
    print("=" * 50)
    
    # Test data
    hotel_properties = Property.objects.filter(property_type__name__iexact='hotel')
    
    context = {
        'properties': hotel_properties,
        'property_type': 'hotel',
        'management_type': 'Hotel Management',
    }
    
    print("Context data:")
    for key, value in context.items():
        print(f"  {key}: {value}")
    
    # Test template rendering
    try:
        rendered = render_to_string('properties/property_selection.html', context)
        print(f"\nTemplate rendered successfully, length: {len(rendered)}")
        
        # Check for specific content
        if "Property Selection" in rendered:
            print("Template check: 'Property Selection' found")
        else:
            print("Template check: 'Property Selection' NOT found")
            
        if "Hotel Management" in rendered:
            print("Template check: 'Hotel Management' found")
        else:
            print("Template check: 'Hotel Management' NOT found")
            
        if "Grand Hotel" in rendered:
            print("Template check: 'Grand Hotel' found")
        else:
            print("Template check: 'Grand Hotel' NOT found")
            
        if "Work with All Properties" in rendered:
            print("Template check: 'Work with All Properties' found")
        else:
            print("Template check: 'Work with All Properties' NOT found")
            
    except Exception as e:
        print(f"Template rendering error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_property_selection_template()
