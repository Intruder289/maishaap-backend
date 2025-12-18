# Generated migration to add missing fields to PaymentProvider

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_add_azam_pay_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentprovider',
            name='provider_type',
            field=models.CharField(choices=[('gateway', 'Payment Gateway'), ('bank', 'Bank'), ('mobile_money', 'Mobile Money'), ('other', 'Other')], default='gateway', max_length=20),
        ),
        migrations.AddField(
            model_name='paymentprovider',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='paymentprovider',
            name='transaction_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Transaction fee percentage', max_digits=5),
        ),
        migrations.AddField(
            model_name='paymentprovider',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='paymentprovider',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name='paymentprovider',
            options={'ordering': ['-created_at']},
        ),
    ]

