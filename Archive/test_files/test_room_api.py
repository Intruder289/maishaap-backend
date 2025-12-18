#!/usr/bin/env python3
"""
Test script for hotel room management functionality
"""

import requests
import json

# Test the room management API endpoints
BASE_URL = "http://127.0.0.1:8001"

def test_room_api():
    """Test the room management API endpoints"""
    
    print("Testing Hotel Room Management API Endpoints")
    print("=" * 50)
    
    # Test data
    test_room_data = {
        'room_number': 'TEST101',
        'room_type': 'Deluxe Room',
        'capacity': 2,
        'floor_number': 1,
        'bed_type': 'King',
        'base_rate': 150.00,
        'amenities': 'WiFi, TV, Air Conditioning',
        'status': 'available'
    }
    
    print("1. Testing room detail endpoint...")
    try:
        # This would need a valid room ID from your database
        response = requests.get(f"{BASE_URL}/properties/api/room/1/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            if data.get('success'):
                room = data.get('room', {})
                print(f"Room Number: {room.get('room_number', 'N/A')}")
                print(f"Room Type: {room.get('room_type', 'N/A')}")
                print(f"Status: {room.get('status', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n2. Testing room edit endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/properties/api/room/1/edit/", data=test_room_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n3. Testing room status update endpoint...")
    try:
        status_data = {
            'status': 'maintenance',
            'reason': 'Routine maintenance'
        }
        response = requests.post(f"{BASE_URL}/properties/api/room/1/status/", data=status_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n4. Testing room delete endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/properties/api/room/1/delete/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_room_api()
