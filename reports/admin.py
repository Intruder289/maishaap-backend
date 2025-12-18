from django.contrib import admin
from .models import ReportTemplate, GeneratedReport, FinancialSummary


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'report_type', 'is_active')
        }),
        ('Configuration', {
            'fields': ('template_config',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'format', 'generated_by', 'created_at', 'completed_at']
    list_filter = ['status', 'format', 'created_at']
    search_fields = ['title', 'generated_by__username']
    readonly_fields = ['created_at', 'completed_at', 'generation_time']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'template', 'status', 'format')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Parameters', {
            'fields': ('parameters',),
            'classes': ('collapse',)
        }),
        ('File Information', {
            'fields': ('file_path', 'file_size', 'total_records'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('generated_by', 'created_at', 'completed_at', 'generation_time', 'error_message'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FinancialSummary)
class FinancialSummaryAdmin(admin.ModelAdmin):
    list_display = ['period_type', 'period_start', 'period_end', 'total_revenue', 'net_income', 'occupancy_rate']
    list_filter = ['period_type', 'period_start']
    readonly_fields = ['total_revenue', 'total_expenses', 'net_income', 'profit_margin', 'occupancy_rate']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('period_type', 'period_start', 'period_end')
        }),
        ('Revenue', {
            'fields': ('total_rent_collected', 'total_other_income', 'total_revenue')
        }),
        ('Expenses', {
            'fields': ('total_maintenance_costs', 'total_utility_costs', 'total_management_fees', 'total_other_expenses', 'total_expenses')
        }),
        ('Calculated Fields', {
            'fields': ('net_income', 'profit_margin'),
            'classes': ('collapse',)
        }),
        ('Occupancy', {
            'fields': ('total_units', 'occupied_units', 'occupancy_rate')
        }),
        ('Maintenance', {
            'fields': ('maintenance_requests', 'completed_maintenance')
        }),
    )
