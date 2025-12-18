from django.contrib import admin
from documents.models import Lease, Booking, Document


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'property_ref', 'tenant', 'start_date', 'end_date', 'rent_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'start_date', 'end_date']
    search_fields = ['property_ref__name', 'tenant__username', 'tenant__email']
    date_hierarchy = 'created_at'
    raw_id_fields = ['property_ref', 'tenant']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Lease Information', {
            'fields': ('property_ref', 'tenant', 'start_date', 'end_date', 'rent_amount')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'property_ref', 'tenant', 'check_in', 'check_out', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'check_in', 'check_out']
    search_fields = ['property_ref__name', 'tenant__username', 'tenant__email']
    date_hierarchy = 'created_at'
    raw_id_fields = ['property_ref', 'tenant']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('property_ref', 'tenant', 'check_in', 'check_out', 'total_amount')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_name', 'lease', 'booking', 'property_ref', 'user', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'lease__property_ref__name', 'booking__property_ref__name']
    date_hierarchy = 'uploaded_at'
    raw_id_fields = ['lease', 'booking', 'property_ref', 'user']
    readonly_fields = ['uploaded_at', 'file_url', 'file_size']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('file_name', 'file')
        }),
        ('Related To', {
            'fields': ('lease', 'booking', 'property_ref', 'user')
        }),
        ('Metadata', {
            'fields': ('uploaded_at', 'file_url', 'file_size'),
            'classes': ('collapse',)
        }),
    )
