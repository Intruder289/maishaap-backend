# Database Users Information

## Users Found in Database

### Admin/Superuser
- **Username:** `admin_user`
- **Email:** `admin@maisha.com`
- **Password:** `test123456` (set for testing)
- **Role:** Admin/Superuser

### Property Owners
1. **Username:** `july`
   - **Email:** `july@maisha.com`
   - **Password:** `test123456` (set for testing)
   - **Role:** Owner

2. **Username:** `alfred`
   - **Email:** `mimi@gmail.com`
   - **Password:** `test123456` (set for testing)
   - **Role:** Owner

### Tenants
1. **Username:** `property_manager1`
   - **Email:** `manager@maisha.com`
   - **Password:** `test123456` (set for testing)
   - **Role:** Tenant

2. **Username:** `property_owner1`
   - **Email:** `owner@maisha.com`
   - **Password:** `test123456` (set for testing)
   - **Role:** Tenant

3. **Username:** `tenant1`
   - **Email:** `tenant1@maisha.com`
   - **Role:** Tenant

4. **Username:** `tenant2`
   - **Email:** `tenant2@maisha.com`
   - **Role:** Tenant

5. **Username:** `maintenance1`
   - **Email:** `maintenance@maisha.com`
   - **Role:** Tenant

And more...

## Test Credentials for Scripts

The following credentials have been set and can be used for testing:

```python
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
```

## Scripts Created

1. **check_users.py** - Lists all users in the database
2. **set_test_passwords.py** - Sets test passwords for users

## Note

- Passwords are stored as hashes in Django, so original passwords cannot be retrieved
- Test password `test123456` has been set for the test users above
- You can run `python set_test_passwords.py` again to reset passwords if needed
