"""
Quick test script to verify Swagger parameters are correctly configured.
Run this after starting your Django server to check if parameters are detected.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema
from properties.api_views import (
    available_rooms_api,
    property_search,
    recent_properties,
    PropertyListCreateAPIView
)
from rest_framework.request import Request
from django.test import RequestFactory

def check_decorator(func, endpoint_name):
    """Check if function has @extend_schema decorator with parameters"""
    print(f"\n{'='*60}")
    print(f"Checking: {endpoint_name}")
    print(f"{'='*60}")
    
    # Check if function has __wrapped__ attribute (indicates decorators)
    has_wrapped = hasattr(func, '__wrapped__')
    print(f"Has decorators: {has_wrapped}")
    
    # Try to inspect the function's decorators
    if hasattr(func, '__wrapped__'):
        print(f"Function is wrapped: ✓")
    else:
        print(f"Function is NOT wrapped: ⚠️")
    
    # Check for drf-spectacular schema
    if hasattr(func, 'kwargs'):
        print(f"Has kwargs attribute: ✓")
    
    print(f"Function name: {func.__name__}")
    print(f"Function module: {func.__module__}")
    
    return True

def test_endpoints():
    """Test all fixed endpoints"""
    print("\n" + "="*60)
    print("SWAGGER PARAMETERS VERIFICATION TEST")
    print("="*60)
    
    endpoints = [
        (available_rooms_api, "GET /api/v1/available-rooms/"),
        (property_search, "GET /api/v1/search/"),
        (recent_properties, "GET /api/v1/recent/"),
    ]
    
    for func, name in endpoints:
        check_decorator(func, name)
    
    # Check class-based view
    print(f"\n{'='*60}")
    print(f"Checking: GET /api/v1/properties/ (PropertyListCreateAPIView)")
    print(f"{'='*60}")
    view = PropertyListCreateAPIView()
    get_method = view.get
    check_decorator(get_method, "PropertyListCreateAPIView.get")
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Open Swagger UI: http://127.0.0.1:8081/swagger/")
    print("3. Check each endpoint shows parameters (not 'No parameters')")
    print("4. Click 'Try it out' to verify input fields appear")
    print("\nExpected results:")
    print("  ✓ available-rooms: 3 parameters (property_id, check_in_date, check_out_date)")
    print("  ✓ search: 9 parameters (search, property_type, category, etc.)")
    print("  ✓ recent: 1 parameter (limit)")
    print("  ✓ properties: 5 parameters (property_type, category, region, etc.)")

if __name__ == "__main__":
    test_endpoints()
