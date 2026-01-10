from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import RentInvoice, LateFee, RentReminder
from payments.models import Payment
from documents.models import Lease
from properties.models import Property


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
            'payment_date', 'amount', 'payment_method', 'reference_number', 
            'status', 'transaction_id', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'tenant', 'lease']


class RentPaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating rent payments (using unified Payment model)"""
    rent_invoice = serializers.PrimaryKeyRelatedField(
        queryset=RentInvoice.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Payment
        fields = [
            'rent_invoice', 'amount', 'payment_method', 'reference_number', 
            'transaction_id', 'notes', 'lease', 'tenant'
        ]
    
    def create(self, validated_data):
        # If rent_invoice is provided, use it to set lease and tenant
        rent_invoice = validated_data.pop('rent_invoice', None)
        if rent_invoice:
            validated_data['lease'] = rent_invoice.lease
            validated_data['tenant'] = rent_invoice.tenant
        
        # Ensure required fields are set
        if 'lease' not in validated_data or not validated_data.get('lease'):
            raise serializers.ValidationError({
                'lease': 'Lease is required when rent_invoice is not provided.'
            })
        if 'tenant' not in validated_data or not validated_data.get('tenant'):
            # Try to get tenant from lease if not provided
            lease = validated_data.get('lease')
            if lease and hasattr(lease, 'tenant'):
                validated_data['tenant'] = lease.tenant
            else:
                raise serializers.ValidationError({
                    'tenant': 'Tenant is required when rent_invoice is not provided.'
                })
        
        validated_data['paid_date'] = timezone.now().date()
        validated_data['status'] = 'completed'
        validated_data['recorded_by'] = self.context['request'].user
        return super().create(validated_data)


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