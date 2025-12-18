# PaymentProvider Migration Instructions

## Issue
The PaymentProvider model was missing fields that are used in views and templates:
- `is_active`
- `provider_type`
- `transaction_fee`
- `created_at`
- `updated_at`

## Solution
A migration file has been created: `payments/migrations/0007_add_payment_provider_fields.py`

## How to Apply the Migration

### Option 1: Use the Pre-created Migration (Recommended)
The migration file is already created. Simply run:

```bash
python manage.py migrate payments
```

If you have existing PaymentProvider records, Django will prompt you for a default value for `created_at`. Accept the default by pressing Enter:

```
[default: timezone.now] >>> 
```

### Option 2: If Migration Fails
If you encounter issues, you can:

1. **Check existing data:**
   ```bash
   python manage.py shell
   >>> from payments.models import PaymentProvider
   >>> PaymentProvider.objects.count()
   ```

2. **If you have existing records**, the migration will set:
   - `created_at` = current time for all existing records
   - `is_active` = True (default)
   - `provider_type` = 'gateway' (default)
   - `transaction_fee` = 0.00 (default)

3. **Run the migration:**
   ```bash
   python manage.py migrate payments
   ```

### Option 3: Manual Migration (If Needed)
If the automatic migration doesn't work, you can manually update existing records:

```python
python manage.py shell
>>> from payments.models import PaymentProvider
>>> from django.utils import timezone
>>> 
>>> # Update all existing providers
>>> PaymentProvider.objects.all().update(
...     created_at=timezone.now(),
...     is_active=True,
...     provider_type='gateway',
...     transaction_fee=0.00
... )
```

Then run the migration:
```bash
python manage.py migrate payments
```

## Verification

After migration, verify the fields exist:

```python
python manage.py shell
>>> from payments.models import PaymentProvider
>>> provider = PaymentProvider.objects.first()
>>> print(provider.is_active)  # Should work
>>> print(provider.provider_type)  # Should work
>>> print(provider.created_at)  # Should work
```

## Status

✅ Migration file created: `0007_add_payment_provider_fields.py`
⏳ **Action Required**: Run `python manage.py migrate payments`

