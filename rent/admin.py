from django.contrib import admin
from .models import RentInvoice, RentPayment, LateFee, RentReminder


@admin.register(RentInvoice)
class RentInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'tenant', 'due_date', 'total_amount', 'amount_paid', 'status', 'is_overdue']
    list_filter = ['status', 'due_date', 'created_at']
    search_fields = ['invoice_number', 'tenant__username', 'tenant__first_name', 'tenant__last_name']
    date_hierarchy = 'due_date'
    readonly_fields = ['invoice_number', 'total_amount', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'lease', 'tenant', 'status')
        }),
        ('Period & Dates', {
            'fields': ('period_start', 'period_end', 'invoice_date', 'due_date')
        }),
        ('Financial Details', {
            'fields': ('base_rent', 'late_fee', 'other_charges', 'discount', 'total_amount', 'amount_paid')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'tenant', 'amount', 'payment_method', 'payment_date', 'status']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'tenant__username', 'reference_number', 'transaction_id']
    date_hierarchy = 'payment_date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LateFee)
class LateFeeAdmin(admin.ModelAdmin):
    list_display = ['lease', 'fee_type', 'amount', 'grace_period_days', 'is_active']
    list_filter = ['fee_type', 'is_active']
    search_fields = ['lease__property_ref__name', 'lease__tenant__username']


@admin.register(RentReminder)
class RentReminderAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'tenant', 'reminder_type', 'days_before_due', 'sent_at', 'is_successful']
    list_filter = ['reminder_type', 'is_successful', 'sent_at']
    search_fields = ['invoice__invoice_number', 'tenant__username']
    date_hierarchy = 'sent_at'