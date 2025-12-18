# Generated migration to backfill assigned_by for existing UserRole records

from django.db import migrations
from django.contrib.auth import get_user_model

User = get_user_model()


def backfill_assigned_by(apps, schema_editor):
    """
    Backfill assigned_by field for existing UserRole records.
    For records without assigned_by, we'll try to find the user who approved the profile
    or set it to the first superuser if available.
    """
    UserRole = apps.get_model('accounts', 'UserRole')
    Profile = apps.get_model('accounts', 'Profile')
    
    # Get all UserRoles with NULL assigned_by
    user_roles_without_assigner = UserRole.objects.filter(assigned_by__isnull=True)
    count = 0
    
    # Try to find the approver from the profile
    for user_role in user_roles_without_assigner:
        try:
            # Check if user has a profile with an approver
            profile = Profile.objects.filter(user=user_role.user).first()
            if profile and profile.approved_by:
                user_role.assigned_by = profile.approved_by
                user_role.save(update_fields=['assigned_by'])
                count += 1
            else:
                # If no approver, try to find the first superuser
                superuser = User.objects.filter(is_superuser=True).first()
                if superuser:
                    user_role.assigned_by = superuser
                    user_role.save(update_fields=['assigned_by'])
                    count += 1
        except Exception:
            # If anything fails, skip this record
            continue
    
    print(f"Backfilled assigned_by for {count} UserRole records")


def reverse_backfill(apps, schema_editor):
    """Reverse migration - set assigned_by back to NULL"""
    UserRole = apps.get_model('accounts', 'UserRole')
    UserRole.objects.filter(assigned_by__isnull=False).update(assigned_by=None)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_notification'),
    ]

    operations = [
        migrations.RunPython(backfill_assigned_by, reverse_backfill),
    ]
