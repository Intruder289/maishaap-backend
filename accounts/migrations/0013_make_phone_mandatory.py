# Generated migration to make phone mandatory
from django.db import migrations, models


def set_default_phones(apps, schema_editor):
    """Set default phone numbers for existing profiles without phone"""
    Profile = apps.get_model('accounts', 'Profile')
    profiles_without_phone = Profile.objects.filter(phone__isnull=True) | Profile.objects.filter(phone='')
    
    for profile in profiles_without_phone:
        # Generate placeholder: +2557000000{user_id}
        placeholder = f"+2557000000{profile.user_id:03d}"
        
        # Ensure uniqueness
        counter = 1
        while Profile.objects.filter(phone=placeholder).exclude(id=profile.id).exists():
            placeholder = f"+2557000000{profile.user_id:03d}{counter}"
            counter += 1
        
        profile.phone = placeholder
        profile.save()


def reverse_set_default_phones(apps, schema_editor):
    """Reverse migration - set phone to None (not used, but required for reverse)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_profile_phone'),
    ]

    operations = [
        # First, set default phones for existing records
        migrations.RunPython(set_default_phones, reverse_set_default_phones),
        
        # Then, make phone mandatory
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(help_text='Phone number is required and must be unique', max_length=30, unique=True),
        ),
    ]
