#!/usr/bin/env python
"""
User Creation Script for Maisha Backend
=======================================

This script creates users for your Django web application with proper roles and profiles.
Run this script from your Django project root directory.

Usage:
    python create_users.py

Options:
    - Creates sample users with different roles
    - Creates superuser
    - Creates users with profiles and roles
"""

import os
import sys
import django
from django.db import transaction

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User, Group
from accounts.models import Profile, CustomRole, UserRole
from django.contrib.auth.models import Permission


def create_custom_roles():
    """Create custom roles for the system"""
    roles_data = [
        {
            'name': 'Admin',
            'description': 'Full system administrator with all permissions'
        },
        {
            'name': 'Property Manager',
            'description': 'Manages properties and tenant relationships'
        },
        {
            'name': 'Property Owner',
            'description': 'Owns properties and can view reports'
        },
        {
            'name': 'Tenant',
            'description': 'Property tenant with limited access'
        },
        {
            'name': 'Maintenance Staff',
            'description': 'Handles property maintenance requests'
        }
    ]
    
    created_roles = []
    for role_data in roles_data:
        role, created = CustomRole.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        if created:
            print(f"✅ Created role: {role.name}")
        else:
            print(f"📝 Role already exists: {role.name}")
        created_roles.append(role)
    
    return created_roles


def create_sample_users():
    """Create sample users with different roles and profiles"""
    
    users_data = [
        {
            'username': 'admin_user',
            'email': 'admin@maisha.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'admin123!',
            'is_superuser': True,
            'is_staff': True,
            'role': 'Admin',
            'phone': '+254712345678'
        },
        {
            'username': 'property_manager1',
            'email': 'manager@maisha.com',
            'first_name': 'John',
            'last_name': 'Manager',
            'password': 'manager123!',
            'is_superuser': False,
            'is_staff': True,
            'role': 'Property Manager',
            'phone': '+254712345679'
        },
        {
            'username': 'property_owner1',
            'email': 'owner@maisha.com',
            'first_name': 'Sarah',
            'last_name': 'Owner',
            'password': 'owner123!',
            'is_superuser': False,
            'is_staff': False,
            'role': 'Property Owner',
            'phone': '+254712345680'
        },
        {
            'username': 'tenant1',
            'email': 'tenant1@maisha.com',
            'first_name': 'Mike',
            'last_name': 'Tenant',
            'password': 'tenant123!',
            'is_superuser': False,
            'is_staff': False,
            'role': 'Tenant',
            'phone': '+254712345681'
        },
        {
            'username': 'tenant2',
            'email': 'tenant2@maisha.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'tenant123!',
            'is_superuser': False,
            'is_staff': False,
            'role': 'Tenant',
            'phone': '+254712345682'
        },
        {
            'username': 'maintenance1',
            'email': 'maintenance@maisha.com',
            'first_name': 'David',
            'last_name': 'Maintenance',
            'password': 'maintenance123!',
            'is_superuser': False,
            'is_staff': False,
            'role': 'Maintenance Staff',
            'phone': '+254712345683'
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            with transaction.atomic():
                # Create or get user
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'is_superuser': user_data['is_superuser'],
                        'is_staff': user_data['is_staff'],
                        'is_active': True
                    }
                )
                
                if created:
                    # Set password
                    user.set_password(user_data['password'])
                    user.save()
                    
                    # Create profile
                    profile, profile_created = Profile.objects.get_or_create(
                        user=user,
                        defaults={'phone': user_data['phone']}
                    )
                    
                    # Assign role
                    try:
                        role = CustomRole.objects.get(name=user_data['role'])
                        user_role, role_created = UserRole.objects.get_or_create(
                            user=user,
                            role=role
                        )
                        if role_created:
                            print(f"✅ Assigned role '{role.name}' to {user.username}")
                    except CustomRole.DoesNotExist:
                        print(f"⚠️ Role '{user_data['role']}' not found for {user.username}")
                    
                    print(f"✅ Created user: {user.username} ({user.email}) - {user_data['role']}")
                    created_users.append(user)
                else:
                    print(f"📝 User already exists: {user.username}")
                    
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {str(e)}")
    
    return created_users


def create_django_groups():
    """Create Django groups for backward compatibility"""
    groups_data = [
        'Admin',
        'Property Manager', 
        'Property Owner',
        'Tenant',
        'Maintenance Staff'
    ]
    
    for group_name in groups_data:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✅ Created group: {group.name}")
        else:
            print(f"📝 Group already exists: {group.name}")


def display_created_users():
    """Display all created users with their details"""
    print("\n" + "="*60)
    print("CREATED USERS SUMMARY")
    print("="*60)
    
    users = User.objects.all().order_by('date_joined')
    
    for user in users:
        print(f"\n👤 {user.username}")
        print(f"   📧 Email: {user.email}")
        print(f"   👤 Name: {user.get_full_name()}")
        print(f"   🔐 Staff: {'Yes' if user.is_staff else 'No'}")
        print(f"   🔐 Superuser: {'Yes' if user.is_superuser else 'No'}")
        
        # Get profile info
        try:
            profile = user.profile
            print(f"   📱 Phone: {profile.phone}")
            
            # Get roles
            roles = profile.get_user_roles()
            if roles.exists():
                role_names = [role.name for role in roles]
                print(f"   🎭 Roles: {', '.join(role_names)}")
        except Profile.DoesNotExist:
            print(f"   ⚠️ No profile found")


def main():
    """Main function to create users"""
    print("🚀 Starting User Creation Script for Maisha Backend")
    print("="*60)
    
    try:
        # Step 1: Create custom roles
        print("\n📋 Creating Custom Roles...")
        create_custom_roles()
        
        # Step 2: Create Django groups (for backward compatibility)
        print("\n👥 Creating Django Groups...")
        create_django_groups()
        
        # Step 3: Create sample users
        print("\n👤 Creating Sample Users...")
        created_users = create_sample_users()
        
        # Step 4: Display summary
        display_created_users()
        
        print(f"\n🎉 Script completed successfully!")
        print(f"✅ Created {len(created_users)} new users")
        
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS")
        print("="*60)
        print("Admin User:")
        print("  Username: admin_user")
        print("  Password: admin123!")
        print("  URL: http://127.0.0.1:8000/accounts/login/")
        print("\nProperty Manager:")
        print("  Username: property_manager1")
        print("  Password: manager123!")
        print("\nProperty Owner:")
        print("  Username: property_owner1") 
        print("  Password: owner123!")
        print("\nTenant:")
        print("  Username: tenant1")
        print("  Password: tenant123!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error running script: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()