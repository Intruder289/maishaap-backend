from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class PaymentProvider(models.Model):
    PROVIDER_TYPE_CHOICES = [
        ('gateway', 'Payment Gateway'),
        ('bank', 'Bank'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPE_CHOICES, default='gateway')
    is_active = models.BooleanField(default=True)
    transaction_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Transaction fee percentage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_providers'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    lease_id = models.BigIntegerField(blank=True, null=True)
    booking_id = models.BigIntegerField(blank=True, null=True)
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invoices'

    def __str__(self):
        return f"Invoice #{self.pk} - {self.tenant} - {self.amount}"


class Payment(models.Model):
    """
    Unified Payment model for all payment types:
    - Rent payments (linked to RentInvoice)
    - General invoice payments (linked to Invoice)
    - Booking payments (linked to Booking)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),  # Added for rent payments compatibility
        ('cancelled', 'Cancelled'),  # Added for rent payments compatibility
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('mobile_money', 'Mobile Money'),
        ('online', 'Online Payment'),
    ]

    # Payment can be linked to one of these (only one should be set)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    rent_invoice = models.ForeignKey('rent.RentInvoice', on_delete=models.SET_NULL, blank=True, null=True, related_name='unified_payments')
    booking = models.ForeignKey('properties.Booking', on_delete=models.SET_NULL, blank=True, null=True, related_name='unified_payments')
    lease = models.ForeignKey('documents.Lease', on_delete=models.SET_NULL, blank=True, null=True, related_name='unified_payments')
    
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.SET_NULL, blank=True, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    paid_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment processor details (for gateway integration)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    processor_response = models.JSONField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_unified_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def clean(self):
        """Ensure only one payment source is set (lease can be set with rent_invoice)"""
        sources = [self.invoice, self.rent_invoice, self.booking]
        set_sources = [s for s in sources if s is not None]
        if len(set_sources) > 1:
            raise ValidationError('Payment can only be linked to one source: invoice, rent_invoice, or booking')
        # Allow payments without sources for visit payments and other special payment types
        # (they are tracked via PropertyVisitPayment or other specialized models)
        # if len(set_sources) == 0:
        #     raise ValidationError('Payment must be linked to at least one source: invoice, rent_invoice, or booking')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Auto-update rent invoice amount_paid if this is a rent payment
        if self.rent_invoice and self.status == 'completed':
            from django.db.models import Sum
            total_paid = Payment.objects.filter(
                rent_invoice=self.rent_invoice,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            self.rent_invoice.amount_paid = total_paid
            self.rent_invoice.save()

    def __str__(self):
        return f"Payment #{self.pk} - {self.tenant} - {self.amount}"


class PaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    provider = models.ForeignKey(PaymentProvider, on_delete=models.SET_NULL, blank=True, null=True, related_name='transactions')
    selcom_reference = models.CharField(max_length=100, blank=True, null=True)  # Legacy field
    azam_reference = models.CharField(max_length=100, blank=True, null=True)  # AZAM Pay transaction reference
    gateway_transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Generic gateway transaction ID
    request_payload = models.JSONField(blank=True, null=True)
    response_payload = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_transactions'

    def __str__(self):
        return f"Transaction #{self.pk} - Payment {self.payment_id} - {self.status}"


class PaymentAudit(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='audits')
    old_status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    new_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_audit'

    def __str__(self):
        return f"Audit #{self.pk} - Payment {self.payment_id} {self.old_status}->{self.new_status}"


class Expense(models.Model):
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='expenses')
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    incurred_date = models.DateField()

    class Meta:
        db_table = 'expenses'

    def __str__(self):
        return f"Expense #{self.pk} - {self.property} - {self.amount}"
