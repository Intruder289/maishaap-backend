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
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money (AZAM Pay)'),
        ('online', 'Online Payment (AZAM Pay)'),
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
    
    # Mobile Money Provider (for mobile_money payments only)
    MOBILE_MONEY_PROVIDER_CHOICES = [
        ('AIRTEL', 'AIRTEL'),
        ('TIGO', 'TIGO'),
        ('MPESA', 'MPESA (Vodacom)'),
        ('HALOPESA', 'HALOPESA'),
    ]
    mobile_money_provider = models.CharField(
        max_length=20,
        choices=MOBILE_MONEY_PROVIDER_CHOICES,
        blank=True,
        null=True,
        help_text='Mobile money provider (required for mobile_money payments)'
    )
    
    paid_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_ref = models.CharField(max_length=100, blank=True, null=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment processor details (for gateway integration)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    processor_response = models.JSONField(null=True, blank=True)
    
    notes = models.TextField(blank=True, null=True)
    
    # Receipt for cash payments (web portal only)
    receipt = models.FileField(
        upload_to='payment_receipts/%Y/%m/',
        blank=True,
        null=True,
        help_text='Receipt/proof of payment (for cash payments only)'
    )
    
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
        
        # Check if this is a new payment being completed without an invoice
        is_new_completion = False
        if self.pk:
            try:
                old_payment = Payment.objects.get(pk=self.pk)
                is_new_completion = (
                    old_payment.status != 'completed' and 
                    self.status == 'completed' and
                    self.lease and 
                    not self.rent_invoice
                )
            except Payment.DoesNotExist:
                is_new_completion = (
                    self.status == 'completed' and
                    self.lease and 
                    not self.rent_invoice
                )
        else:
            is_new_completion = (
                self.status == 'completed' and
                self.lease and 
                not self.rent_invoice
            )
        
        super().save(*args, **kwargs)
        
        # Auto-create invoice for lease payments without invoices when payment completes
        # Use transaction with lock to prevent race conditions
        if is_new_completion and self.lease and not self.rent_invoice:
            from rent.models import RentInvoice
            from documents.models import Lease
            from django.utils import timezone
            from django.db import transaction
            from datetime import datetime, timedelta
            
            # Use transaction with select_for_update to prevent race conditions
            with transaction.atomic():
                # Lock lease to prevent concurrent invoice creation
                locked_lease = Lease.objects.select_for_update().get(pk=self.lease.pk)
                
                # Determine the period for the invoice (current month)
                # Use payment date if available, otherwise use today
                payment_date = self.paid_date if self.paid_date else timezone.now().date()
                period_start = payment_date.replace(day=1)  # First day of payment month
                
                # Calculate period_end (last day of payment month)
                if period_start.month == 12:
                    period_end = datetime(period_start.year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    period_end = datetime(period_start.year, period_start.month + 1, 1).date() - timedelta(days=1)
                
                # Check if invoice already exists for this period (with lock)
                existing_invoice = RentInvoice.objects.filter(
                    lease=locked_lease,
                    period_start=period_start,
                    period_end=period_end
                ).first()
                
                if existing_invoice:
                    # Link payment to existing invoice
                    self.rent_invoice = existing_invoice
                    self.save(update_fields=['rent_invoice'])
                    # Update invoice amount_paid (will be handled by the code below)
                else:
                    # Create new invoice for this period
                    due_date = period_start + timedelta(days=5)  # Due 5 days after period start
                    new_invoice = RentInvoice.objects.create(
                        lease=locked_lease,
                        tenant=self.tenant,
                        due_date=due_date,
                        period_start=period_start,
                        period_end=period_end,
                        base_rent=locked_lease.rent_amount,
                        status='sent'  # Mark as sent since payment is being made
                    )
                    # Link payment to new invoice
                    self.rent_invoice = new_invoice
                    self.save(update_fields=['rent_invoice'])
        
        # Auto-update rent invoice amount_paid if this is a rent payment
        # This ensures invoice status and balance are always accurate
        if self.rent_invoice and self.status == 'completed':
            from django.db.models import Sum
            # Recalculate total_paid from all completed payments for accuracy
            total_paid = Payment.objects.filter(
                rent_invoice=self.rent_invoice,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            self.rent_invoice.amount_paid = total_paid
            
            # Update invoice status based on payment
            if self.rent_invoice.amount_paid >= self.rent_invoice.total_amount:
                self.rent_invoice.status = 'paid'
            elif self.rent_invoice.due_date < timezone.now().date() and self.rent_invoice.status not in ['paid', 'cancelled']:
                self.rent_invoice.status = 'overdue'
            
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
