"""Assign Tenant role to test user"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile, CustomRole, UserRole

# Get the test user
test_user = User.objects.get(username='api_test_user')

# Get the Tenant role
try:
    tenant_role = CustomRole.objects.get(name='Tenant')
    print(f"[OK] Found Tenant role: {tenant_role.name}")
except CustomRole.DoesNotExist:
    print("[ERROR] Tenant role does not exist")
    exit(1)

# Assign the role
assignment, created = UserRole.objects.get_or_create(
    user=test_user,
    role=tenant_role
)

if created:
    print(f"[SUCCESS] Assigned role '{tenant_role.name}' to user '{test_user.username}'")
else:
    print(f"[INFO] Role '{tenant_role.name}' already assigned to user '{test_user.username}'")

# Verify
user_roles = test_user.user_roles.all()
print(f"\n[VERIFY] User now has {user_roles.count()} role(s):")
for role in user_roles:
    print(f"  - {role.role.name}: {role.role.description}")

print("\n" + "="*80)


