from django.contrib import admin
from . import models


@admin.register(models.PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'amount', 'due_date', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('tenant__username', 'tenant__email')


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'amount', 'status', 'provider', 'transaction_ref', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('tenant__username', 'transaction_ref')


@admin.register(models.PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'provider', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'provider')


@admin.register(models.PaymentAudit)
class PaymentAuditAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'old_status', 'new_status', 'changed_at')
    list_filter = ('old_status', 'new_status')


@admin.register(models.Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'amount', 'incurred_date')
    search_fields = ('property__title',)
