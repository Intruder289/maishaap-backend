"""Debug user roles and authentication"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Maisha_backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile, CustomRole, UserRole

# Check the test user
test_user = User.objects.get(username='api_test_user')
profile = test_user.profile

print("\n[DEBUG] User Information:")
print("="*80)
print(f"Username: {test_user.username}")
print(f"Email: {test_user.email}")
print(f"Is Active: {test_user.is_active}")
print(f"Is Approved: {profile.is_approved}")

print("\n[DEBUG] Profile Information:")
print("="*80)
print(f"Phone: {profile.phone}")
print(f"Role: {profile.role}")
print(f"Role Display: {profile.get_role_display()}")

print("\n[DEBUG] Custom Roles:")
print("="*80)
user_roles = profile.get_user_roles()
print(f"Number of roles: {user_roles.count()}")
for role in user_roles:
    print(f"  - {role.name}: {role.description}")

print("\n[DEBUG] All CustomRole objects in DB:")
print("="*80)
all_roles = CustomRole.objects.all()
print(f"Total roles in DB: {all_roles.count()}")
for role in all_roles:
    print(f"  - {role.name}: {role.description}")

print("\n[DEBUG] UserRole assignments:")
print("="*80)
assignments = UserRole.objects.filter(user=test_user)
print(f"Total assignments: {assignments.count()}")
for assignment in assignments:
    print(f"  - {assignment.role.name} (assigned at {assignment.assigned_at})")

print("\n" + "="*80)


