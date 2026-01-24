from rest_framework import serializers
from . import models
from django.conf import settings


class PaymentProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentProvider
        fields = ['id', 'name', 'description']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invoice
        fields = ['id', 'lease_id', 'booking_id', 'tenant', 'amount', 'due_date', 'status', 'created_at']
        read_only_fields = ['created_at']


class PaymentSerializer(serializers.ModelSerializer):
    booking_reference = serializers.CharField(source='booking.booking_reference', read_only=True)
    booking_id = serializers.IntegerField(source='booking.id', read_only=True)
    
    class Meta:
        model = models.Payment
        fields = [
            'id', 'invoice', 'rent_invoice', 'booking', 'tenant', 'provider', 
            'amount', 'payment_method', 'mobile_money_provider', 'paid_date', 
            'status', 'transaction_ref', 'reference_number', 'transaction_id',
            'notes', 'created_at', 'updated_at', 'booking_reference', 'booking_id'
        ]
        read_only_fields = ['created_at', 'updated_at', 'booking_reference', 'booking_id']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentTransaction
        fields = [
            'id', 'payment', 'provider', 
            'selcom_reference', 'azam_reference', 'gateway_transaction_id',
            'request_payload', 'response_payload', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PaymentAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PaymentAudit
        fields = ['id', 'payment', 'old_status', 'new_status', 'changed_at']
        read_only_fields = ['changed_at']


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Expense
        fields = ['id', 'property', 'description', 'amount', 'incurred_date']
