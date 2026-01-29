from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import RentInvoice, LateFee, RentReminder
from payments.models import Payment
from documents.models import Lease
from properties.models import Property


def format_currency(amount):
    """Format decimal amount as currency string"""
    if amount is None:
        return "0.00"
    return f"{float(amount):,.2f}"


class TenantSerializer(serializers.ModelSerializer):
    """Minimal tenant info for API responses"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class PropertyMinimalSerializer(serializers.ModelSerializer):
    """Minimal property info for API responses"""
    class Meta:
        model = Property
        fields = ['id', 'title', 'address', 'property_type']


class LeaseMinimalSerializer(serializers.ModelSerializer):
    """Minimal lease info for API responses"""
    property_ref = PropertyMinimalSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    
    class Meta:
        model = Lease
        fields = ['id', 'property_ref', 'tenant', 'start_date', 'end_date', 'rent_amount', 'status']


class RentPaymentSerializer(serializers.ModelSerializer):
    """Serializer for rent payments (using unified Payment model)"""
    tenant = TenantSerializer(read_only=True)
    invoice_number = serializers.CharField(source='rent_invoice.invoice_number', read_only=True)
    lease_property = serializers.CharField(source='lease.property_ref.title', read_only=True)
    payment_date = serializers.DateField(source='paid_date', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'rent_invoice', 'lease', 'tenant', 'invoice_number', 'lease_property',
            'payment_date', 'amount', 'payment_method', 'mobile_money_provider', 
            'reference_number', 'status', 'transaction_id', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'tenant', 'lease']


class RentPaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating rent payments (using unified Payment model)
    
    **Payment Options:**
    1. **With Invoice:** Provide `rent_invoice` ID - payment is linked to specific invoice
    2. **Without Invoice:** Provide `lease` ID - payment is linked directly to lease.
       An invoice will be auto-created when payment completes.
    
    **Note:** Either `rent_invoice` OR `lease` must be provided. If `rent_invoice` is provided,
    `lease` will be automatically set from the invoice.
    """
    rent_invoice = serializers.PrimaryKeyRelatedField(
        queryset=RentInvoice.objects.all(),
        required=False,
        allow_null=True,
        help_text="Optional: Invoice ID. If not provided, lease must be provided."
    )
    lease = serializers.PrimaryKeyRelatedField(
        queryset=Lease.objects.all(),
        required=False,
        allow_null=True,
        help_text="Optional: Lease ID. Required if rent_invoice is not provided."
    )
    
    class Meta:
        model = Payment
        fields = [
            'rent_invoice', 'lease', 'amount', 'payment_method', 'mobile_money_provider', 
            'reference_number', 'transaction_id', 'notes', 'tenant'
        ]
    
    def validate(self, data):
        """
        Validate payment data:
        1. Either rent_invoice OR lease must be provided
        2. If rent_invoice provided, validate amount doesn't exceed invoice balance
        3. Ensure amount is positive
        """
        rent_invoice = data.get('rent_invoice')
        lease = data.get('lease')
        amount = data.get('amount')
        
        # Ensure either rent_invoice or lease is provided
        if not rent_invoice and not lease:
            raise serializers.ValidationError({
                'rent_invoice': 'Either rent_invoice or lease must be provided.',
                'lease': 'Either rent_invoice or lease must be provided.'
            })
        
        # If rent_invoice is provided, validate amount against invoice balance
        if rent_invoice and amount:
            from decimal import Decimal
            from django.db.models import Sum
            from django.db import transaction
            
            # Use select_for_update to prevent race conditions
            with transaction.atomic():
                # Lock the invoice row to prevent concurrent modifications
                locked_invoice = RentInvoice.objects.select_for_update().get(pk=rent_invoice.pk)
                
                # Calculate ALL payments (completed + pending) to get accurate balance
                total_completed = Payment.objects.filter(
                    rent_invoice=locked_invoice,
                    status='completed'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                # Also consider pending payments (they will eventually complete)
                total_pending = Payment.objects.filter(
                    rent_invoice=locked_invoice,
                    status='pending'
                ).exclude(id=self.instance.pk if self.instance else None).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                # Total amount that will be paid (completed + pending)
                total_will_be_paid = total_completed + total_pending
                
                # Calculate remaining balance (what's actually still due)
                balance_due = locked_invoice.total_amount - total_completed
                
                # STRICT VALIDATION: Invoice must not be fully paid
                if balance_due <= 0:
                    raise serializers.ValidationError({
                        'rent_invoice': f'This invoice ({locked_invoice.invoice_number}) is already fully paid. No additional payment is needed. Total amount: TZS {format_currency(locked_invoice.total_amount)}, Amount paid: TZS {format_currency(total_completed)}.'
                    })
                
                # STRICT VALIDATION: Payment amount cannot exceed remaining balance
                if amount > balance_due:
                    raise serializers.ValidationError({
                        'amount': f'Payment amount (TZS {format_currency(amount)}) exceeds the remaining balance (TZS {format_currency(balance_due)}). Please pay TZS {format_currency(balance_due)} or less. Invoice: {locked_invoice.invoice_number}'
                    })
                
                # STRICT VALIDATION: Combined payments (completed + pending + this new one) cannot exceed total
                if total_will_be_paid + amount > locked_invoice.total_amount:
                    excess = (total_will_be_paid + amount) - locked_invoice.total_amount
                    raise serializers.ValidationError({
                        'amount': f'This payment would cause overpayment. Remaining balance: TZS {format_currency(balance_due)}, Pending payments: TZS {format_currency(total_pending)}, Your payment: TZS {format_currency(amount)}. Maximum you can pay: TZS {format_currency(balance_due)}'
                    })
                
                # Ensure amount is positive
                if amount <= 0:
                    raise serializers.ValidationError({
                        'amount': 'Payment amount must be greater than zero. Please enter a valid payment amount.'
                    })
        
        # Validate amount is positive for lease-only payments too
        if amount and amount <= 0:
            raise serializers.ValidationError({
                'amount': 'Payment amount must be greater than zero. Please enter a valid payment amount.'
            })
        
        return data
    
    def create(self, validated_data):
        from django.db import transaction
        from decimal import Decimal
        from django.db.models import Sum
        
        # Get rent_invoice before popping (needed for locking)
        rent_invoice_id = None
        if 'rent_invoice' in validated_data:
            rent_invoice_obj = validated_data['rent_invoice']
            rent_invoice_id = rent_invoice_obj.pk if rent_invoice_obj else None
        
        # Use transaction with select_for_update to prevent race conditions
        with transaction.atomic():
            if rent_invoice_id:
                # Lock invoice to prevent concurrent modifications
                locked_invoice = RentInvoice.objects.select_for_update().get(pk=rent_invoice_id)
                
                # Re-validate balance after locking (double-check)
                total_completed = Payment.objects.filter(
                    rent_invoice=locked_invoice,
                    status='completed'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                total_pending = Payment.objects.filter(
                    rent_invoice=locked_invoice,
                    status='pending'
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
                
                balance_due = locked_invoice.total_amount - total_completed
                amount = validated_data.get('amount', Decimal('0'))
                
                # Final validation check after lock
                if balance_due <= 0:
                    raise serializers.ValidationError({
                        'rent_invoice': f'This invoice ({locked_invoice.invoice_number}) is already fully paid. No additional payment is needed. Total amount: TZS {format_currency(locked_invoice.total_amount)}, Amount paid: TZS {format_currency(total_completed)}.'
                    })
                
                if amount > balance_due:
                    raise serializers.ValidationError({
                        'amount': f'Payment amount (TZS {format_currency(amount)}) exceeds the remaining balance (TZS {format_currency(balance_due)}). Please pay TZS {format_currency(balance_due)} or less. Invoice: {locked_invoice.invoice_number}'
                    })
                
                if total_completed + total_pending + amount > locked_invoice.total_amount:
                    raise serializers.ValidationError({
                        'amount': f'This payment would cause overpayment. Remaining balance: TZS {format_currency(balance_due)}, Pending payments: TZS {format_currency(total_pending)}, Your payment: TZS {format_currency(amount)}. Maximum you can pay: TZS {format_currency(balance_due)}'
                    })
                
                validated_data['rent_invoice'] = locked_invoice
                validated_data['lease'] = locked_invoice.lease
                validated_data['tenant'] = locked_invoice.tenant
            else:
                # Payment without invoice - ensure lease is provided
                lease = validated_data.get('lease')
                if not lease:
                    raise serializers.ValidationError({
                        'lease': 'Lease information is required when creating a payment without an invoice.'
                    })
                
                # Ensure tenant is set from lease
                if 'tenant' not in validated_data or not validated_data.get('tenant'):
                    if lease and hasattr(lease, 'tenant'):
                        validated_data['tenant'] = lease.tenant
                    else:
                        raise serializers.ValidationError({
                            'tenant': 'Tenant information is required. Please provide a valid tenant when creating a payment without an invoice.'
                        })
                
                # Validate lease is active (optional but good practice)
                if lease.status != 'active':
                    raise serializers.ValidationError({
                        'lease': f'Cannot create payment for lease with status "{lease.status}". Only active leases can receive payments.'
                    })
            
            # Set payment status and paid_date based on payment method
            payment_method = validated_data.get('payment_method', 'cash')
            
            # For cash payments, mark as completed immediately
            # For gateway payments (mobile_money, online), mark as pending until gateway completes
            if payment_method == 'cash':
                validated_data['status'] = 'completed'
                validated_data['paid_date'] = timezone.now().date()
            else:
                # Gateway payments start as pending
                validated_data['status'] = 'pending'
                # Don't set paid_date yet - it will be set when gateway payment completes
                validated_data['paid_date'] = None
            
            validated_data['recorded_by'] = self.context['request'].user
            
            # Create payment
            payment = super().create(validated_data)
            
            # Refresh invoice to update amount_paid (Payment.save() handles this automatically)
            if rent_invoice_id:
                locked_invoice.refresh_from_db()
            
            return payment


class RentInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for rent invoices"""
    tenant = TenantSerializer(read_only=True)
    lease = LeaseMinimalSerializer(read_only=True)
    balance_due = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    payments = serializers.SerializerMethodField()
    payments_count = serializers.SerializerMethodField()
    last_payment_date = serializers.SerializerMethodField()
    
    class Meta:
        model = RentInvoice
        fields = [
            'id', 'lease', 'tenant', 'invoice_number', 'invoice_date', 
            'due_date', 'period_start', 'period_end', 'base_rent', 
            'late_fee', 'other_charges', 'discount', 'total_amount', 
            'amount_paid', 'balance_due', 'status', 'is_overdue', 
            'days_overdue', 'notes', 'payments', 'payments_count',
            'last_payment_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'total_amount', 'amount_paid', 
            'balance_due', 'is_overdue', 'days_overdue', 'created_at', 'updated_at'
        ]
    
    def get_payments(self, obj):
        """Get unified payments for this rent invoice"""
        payments = Payment.objects.filter(rent_invoice=obj)
        return RentPaymentSerializer(payments, many=True).data
    
    def get_payments_count(self, obj):
        return Payment.objects.filter(rent_invoice=obj, status='completed').count()
    
    def get_last_payment_date(self, obj):
        last_payment = Payment.objects.filter(rent_invoice=obj, status='completed').order_by('-paid_date').first()
        return last_payment.paid_date if last_payment else None


class RentInvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating rent invoices"""
    
    class Meta:
        model = RentInvoice
        fields = [
            'lease', 'due_date', 'period_start', 'period_end', 
            'base_rent', 'late_fee', 'other_charges', 'discount', 'notes'
        ]
    
    def create(self, validated_data):
        # Set tenant from lease
        lease = validated_data['lease']
        validated_data['tenant'] = lease.tenant
        return super().create(validated_data)


class LateFeeSerializer(serializers.ModelSerializer):
    """Serializer for late fee configurations"""
    lease_info = serializers.SerializerMethodField()
    
    class Meta:
        model = LateFee
        fields = [
            'id', 'lease', 'lease_info', 'fee_type', 'amount', 
            'grace_period_days', 'max_late_fee', 'is_active', 'created_at'
        ]
    
    def get_lease_info(self, obj):
        return f"{obj.lease.property_ref.name} - {obj.lease.tenant.get_full_name() or obj.lease.tenant.username}"


class RentReminderSerializer(serializers.ModelSerializer):
    """Serializer for rent reminders"""
    tenant = TenantSerializer(read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = RentReminder
        fields = [
            'id', 'invoice', 'invoice_number', 'tenant', 'reminder_type', 
            'days_before_due', 'sent_at', 'is_successful', 'error_message'
        ]
        read_only_fields = ['id', 'sent_at', 'tenant']


class RentDashboardSerializer(serializers.Serializer):
    """Serializer for rent dashboard statistics"""
    total_monthly_rent = serializers.DecimalField(max_digits=12, decimal_places=2)
    collected_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    overdue_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_invoices = serializers.IntegerField()
    paid_invoices = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    active_leases = serializers.IntegerField()
    collection_rate = serializers.FloatField()
    
    recent_payments = RentPaymentSerializer(many=True)
    overdue_invoices_list = RentInvoiceSerializer(many=True)


class TenantRentSummarySerializer(serializers.Serializer):
    """Serializer for tenant's rent summary"""
    tenant = TenantSerializer()
    active_lease = LeaseMinimalSerializer()
    current_invoice = RentInvoiceSerializer()
    payment_history = RentPaymentSerializer(many=True)
    total_paid_this_year = serializers.DecimalField(max_digits=12, decimal_places=2)
    outstanding_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    next_due_date = serializers.DateField()
    is_current = serializers.BooleanField()