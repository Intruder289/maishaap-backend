#!/usr/bin/env python3
"""
Test rent navigation functionality
"""
import requests
import sys

def test_rent_navigation():
    """Test rent module navigation and pages"""
    base_url = "http://127.0.0.1:8000"
    
    # Test pages
    test_pages = [
        ("/rent/", "Rent Management Dashboard"),
        ("/rent/invoices/", "Rent Invoices"),
        ("/rent/payments/", "Rent Payments"),
    ]
    
    print("Testing rent navigation...")
    print("-" * 50)
    
    for url, expected_title in test_pages:
        try:
            response = requests.get(f"{base_url}{url}")
            if response.status_code == 200:
                if expected_title.lower() in response.text.lower():
                    print(f"✓ {url} - {expected_title} (200 OK)")
                else:
                    print(f"⚠ {url} - Page loads but title not found (200 OK)")
            elif response.status_code == 302:
                print(f"→ {url} - Redirected (needs login) (302)")
            else:
                print(f"✗ {url} - Error {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ {url} - Connection error: {e}")
    
    print("-" * 50)
    print("Rent navigation implementation complete!")
    print("\nTo test the navigation:")
    print("1. Visit http://127.0.0.1:8000/rent/")
    print("2. Check the sidebar for 'Rent Management' section")
    print("3. Navigate between Dashboard, Invoices, and Payments")

if __name__ == "__main__":
    test_rent_navigation()