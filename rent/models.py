from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from documents.models import Lease


class RentInvoice(models.Model):
    """
    Monthly rent invoices generated for each lease
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='rent_invoices')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rent_invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    period_start = models.DateField()  # The month/period this invoice covers
    period_end = models.DateField()
    
    # Amounts
    base_rent = models.DecimalField(max_digits=12, decimal_places=2)
    late_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rent Invoice'
        verbose_name_plural = 'Rent Invoices'
        unique_together = ['lease', 'period_start', 'period_end']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.tenant.get_full_name() or self.tenant.username}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        
        # Calculate total amount
        self.total_amount = self.base_rent + self.late_fee + self.other_charges - self.discount
        
        # Update status based on payment and due date
        if self.amount_paid >= self.total_amount:
            self.status = 'paid'
        elif self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        import uuid
        return f"INV-{timezone.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
    
    @property
    def balance_due(self):
        """Calculate remaining balance"""
        return self.total_amount - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        return self.due_date < timezone.now().date() and self.status != 'paid'
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0


class RentPayment(models.Model):
    """
    Individual payments made against rent invoices
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money (AZAM Pay)'),
        ('online', 'Online Payment (AZAM Pay)'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice = models.ForeignKey(RentInvoice, on_delete=models.CASCADE, related_name='payments')
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='rent_payments')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rent_payments')
    
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='completed')
    
    # Payment processor details
    transaction_id = models.CharField(max_length=100, blank=True)
    processor_response = models.JSONField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='recorded_payments'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Rent Payment'
        verbose_name_plural = 'Rent Payments'
    
    def __str__(self):
        return f"Payment TZS {self.amount:,.0f} for {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update invoice amount_paid when payment is saved
        if self.status == 'completed':
            self.invoice.amount_paid = self.invoice.payments.filter(
                status='completed'
            ).aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal('0.00')
            self.invoice.save()


class LateFee(models.Model):
    """
    Late fee configuration and tracking
    """
    FEE_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage of Rent'),
        ('daily', 'Daily Rate'),
    ]
    
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='late_fees')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='fixed')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    grace_period_days = models.IntegerField(default=5)
    max_late_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Late Fee Configuration'
        verbose_name_plural = 'Late Fee Configurations'
    
    def __str__(self):
        return f"Late Fee for {self.lease} - {self.get_fee_type_display()}: TZS {self.amount:,.0f}"
    
    def calculate_late_fee(self, invoice, days_overdue):
        """Calculate late fee for an overdue invoice"""
        if days_overdue <= self.grace_period_days:
            return Decimal('0.00')
        
        if self.fee_type == 'fixed':
            return self.amount
        elif self.fee_type == 'percentage':
            fee = invoice.base_rent * (self.amount / 100)
        elif self.fee_type == 'daily':
            effective_days = days_overdue - self.grace_period_days
            fee = self.amount * effective_days
        else:
            return Decimal('0.00')
        
        # Apply maximum late fee if set
        if self.max_late_fee and fee > self.max_late_fee:
            fee = self.max_late_fee
        
        return fee


class RentReminder(models.Model):
    """
    Track rent payment reminders sent to tenants
    """
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    invoice = models.ForeignKey(RentInvoice, on_delete=models.CASCADE, related_name='reminders')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    days_before_due = models.IntegerField()  # Negative for overdue reminders
    
    sent_at = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Rent Reminder'
        verbose_name_plural = 'Rent Reminders'
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} reminder for {self.invoice.invoice_number}"