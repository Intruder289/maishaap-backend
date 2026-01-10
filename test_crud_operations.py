"""
Test script for CRUD operations with different user roles
Tests data isolation and CRUD functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"  # Adjust if your server runs on different port
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials - Updated from database
TEST_ADMIN = {
    "email": "admin@maisha.com",
    "password": "test123456"
}

TEST_OWNER = {
    "email": "july@maisha.com",
    "password": "test123456"
}

TEST_TENANT = {
    "email": "manager@maisha.com",
    "password": "test123456"
}


def get_auth_token(email, password):
    """Get JWT token for authentication"""
    url = f"{API_BASE}/auth/login/"
    data = {"email": email, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get("access")
    print(f"❌ Login failed for {email}: {response.status_code} - {response.text}")
    return None


def test_crud_operation(module_name, endpoint_base, token, test_data=None):
    """Test CRUD operations for a module"""
    print(f"\n{'='*60}")
    print(f"Testing CRUD Operations: {module_name}")
    print(f"{'='*60}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # CREATE
    print(f"\n1. CREATE - POST {endpoint_base}")
    if test_data:
        create_response = requests.post(f"{API_BASE}/{endpoint_base}", headers=headers, json=test_data)
        if create_response.status_code in [200, 201]:
            created_obj = create_response.json()
            obj_id = created_obj.get("id")
            print(f"✅ Created object with ID: {obj_id}")
            
            # READ
            print(f"\n2. READ - GET {endpoint_base}/{obj_id}/")
            read_response = requests.get(f"{API_BASE}/{endpoint_base}/{obj_id}/", headers=headers)
            if read_response.status_code == 200:
                print(f"✅ Retrieved object: {read_response.json()}")
            else:
                print(f"❌ Failed to retrieve: {read_response.status_code}")
            
            # UPDATE
            print(f"\n3. UPDATE - PUT {endpoint_base}/{obj_id}/")
            if test_data:
                update_data = test_data.copy()
                update_data["description"] = "Updated description"
                update_response = requests.put(f"{API_BASE}/{endpoint_base}/{obj_id}/", headers=headers, json=update_data)
                if update_response.status_code in [200, 201]:
                    print(f"✅ Updated object")
                else:
                    print(f"❌ Failed to update: {update_response.status_code}")
            
            # DELETE
            print(f"\n4. DELETE - DELETE {endpoint_base}/{obj_id}/")
            delete_response = requests.delete(f"{API_BASE}/{endpoint_base}/{obj_id}/", headers=headers)
            if delete_response.status_code in [200, 204]:
                print(f"✅ Deleted object")
            else:
                print(f"❌ Failed to delete: {delete_response.status_code}")
            
            return obj_id
        else:
            print(f"❌ Failed to create: {create_response.status_code} - {create_response.text}")
    else:
        print("⚠️  No test data provided, skipping CREATE test")
    
    # LIST
    print(f"\n5. LIST - GET {endpoint_base}")
    list_response = requests.get(f"{API_BASE}/{endpoint_base}", headers=headers)
    if list_response.status_code == 200:
        data = list_response.json()
        if isinstance(data, dict) and "results" in data:
            count = len(data["results"])
        elif isinstance(data, list):
            count = len(data)
        else:
            count = 0
        print(f"✅ Retrieved {count} objects")
        return count
    else:
        print(f"❌ Failed to list: {list_response.status_code}")
    
    return None


def test_data_isolation():
    """Test that users only see their own data"""
    print("\n" + "="*60)
    print("TESTING DATA ISOLATION")
    print("="*60)
    
    admin_token = get_auth_token(TEST_ADMIN["email"], TEST_ADMIN["password"])
    owner_token = get_auth_token(TEST_OWNER["email"], TEST_OWNER["password"])
    tenant_token = get_auth_token(TEST_TENANT["email"], TEST_TENANT["password"])
    
    if not all([admin_token, owner_token, tenant_token]):
        print("⚠️  Warning: Could not get all tokens. Update credentials in script.")
        return
    
    # Test maintenance requests (tenants should only see their own)
    print("\n--- Maintenance Requests Data Isolation ---")
    
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_owner = {"Authorization": f"Bearer {owner_token}"}
    headers_tenant = {"Authorization": f"Bearer {tenant_token}"}
    
    # Admin sees all
    admin_response = requests.get(f"{API_BASE}/maintenance/requests/", headers=headers_admin)
    admin_count = len(admin_response.json()) if admin_response.status_code == 200 else 0
    print(f"Admin sees {admin_count} maintenance requests")
    
    # Owner sees their properties' requests
    owner_response = requests.get(f"{API_BASE}/maintenance/requests/", headers=headers_owner)
    owner_count = len(owner_response.json()) if owner_response.status_code == 200 else 0
    print(f"Owner sees {owner_count} maintenance requests")
    
    # Tenant sees only their own
    tenant_response = requests.get(f"{API_BASE}/maintenance/requests/", headers=headers_tenant)
    tenant_count = len(tenant_response.json()) if tenant_response.status_code == 200 else 0
    print(f"Tenant sees {tenant_count} maintenance requests")
    
    # Verify isolation
    if admin_count >= owner_count >= tenant_count:
        print("✅ Data isolation working correctly (admin >= owner >= tenant)")
    else:
        print("⚠️  Data isolation may not be working correctly")
    
    # Test rent invoices
    print("\n--- Rent Invoices Data Isolation ---")
    
    admin_invoices = requests.get(f"{API_BASE}/rent/invoices/", headers=headers_admin)
    admin_inv_count = len(admin_invoices.json()) if admin_invoices.status_code == 200 else 0
    print(f"Admin sees {admin_inv_count} rent invoices")
    
    tenant_invoices = requests.get(f"{API_BASE}/rent/invoices/", headers=headers_tenant)
    tenant_inv_count = len(tenant_invoices.json()) if tenant_invoices.status_code == 200 else 0
    print(f"Tenant sees {tenant_inv_count} rent invoices")
    
    if admin_inv_count >= tenant_inv_count:
        print("✅ Data isolation working correctly")
    else:
        print("⚠️  Data isolation may not be working correctly")


def main():
    """Main test function"""
    print("CRUD Operations Test Script")
    print("="*60)
    print("Make sure your Django server is running!")
    print("Update test credentials at the top of this script if needed.")
    print("="*60)
    
    # Get tokens
    admin_token = get_auth_token(TEST_ADMIN["email"], TEST_ADMIN["password"])
    owner_token = get_auth_token(TEST_OWNER["email"], TEST_OWNER["password"])
    tenant_token = get_auth_token(TEST_TENANT["email"], TEST_TENANT["password"])
    
    if not admin_token:
        print("\n⚠️  Could not authenticate. Please update credentials.")
        return
    
    # Test CRUD for different modules
    modules = [
        ("Maintenance Requests", "maintenance/requests/", {
            "title": "Test Maintenance Request",
            "description": "Test description",
            "priority": "medium",
            "property": 1  # Update with actual property ID
        }),
        ("Complaints", "complaints/complaints/", {
            "title": "Test Complaint",
            "description": "Test complaint description",
            "category": "other",
            "priority": "medium"
        }),
    ]
    
    print("\n" + "="*60)
    print("TESTING CRUD OPERATIONS")
    print("="*60)
    
    for module_name, endpoint, test_data in modules:
        if admin_token:
            test_crud_operation(module_name, endpoint, admin_token, test_data)
    
    # Test data isolation
    test_data_isolation()
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
