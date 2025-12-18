#!/usr/bin/env python
import requests
import json

def test_hotel_dashboard_detailed():
    print("TESTING HOTEL DASHBOARD DETAILED")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8001"
    
    # Test Hotel Dashboard with detailed response
    print("\n1. Testing Hotel Dashboard Response...")
    try:
        response = requests.get(f"{base_url}/properties/hotel/dashboard/")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Length: {len(response.text)}")
        
        if response.status_code == 200:
            # Check for specific content
            content = response.text
            
            # Check for property selection
            if "Managing: All Hotels" in content:
                print("   Property Selection: Found 'Managing: All Hotels'")
            elif "Managing:" in content:
                print("   Property Selection: Found 'Managing:' text")
            else:
                print("   Property Selection: NOT FOUND")
            
            # Check for stats cards
            if "Total Rooms" in content:
                print("   Stats Cards: Found 'Total Rooms'")
            else:
                print("   Stats Cards: NOT FOUND")
            
            # Check for New Booking button
            if "create_hotel_booking" in content:
                print("   New Booking Button: Found 'create_hotel_booking'")
            else:
                print("   New Booking Button: NOT FOUND")
            
            # Check for authentication redirect
            if "login" in content.lower() or "sign in" in content.lower():
                print("   Authentication: Redirected to login")
            else:
                print("   Authentication: No login redirect detected")
                
        else:
            print(f"   Dashboard failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Dashboard error: {e}")

if __name__ == "__main__":
    test_hotel_dashboard_detailed()
