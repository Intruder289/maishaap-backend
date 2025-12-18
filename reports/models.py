from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from properties.models import Property
from rent.models import RentPayment, RentInvoice
from maintenance.models import MaintenanceRequest
from payments.models import Payment
from decimal import Decimal


class ReportTemplate(models.Model):
    """
    Predefined report templates for common reporting needs
    """
    REPORT_TYPE_CHOICES = [
        ('financial', 'Financial Reports'),
        ('occupancy', 'Occupancy Reports'),
        ('maintenance', 'Maintenance Reports'),
        ('tenant', 'Tenant Reports'),
        ('property', 'Property Reports'),
        ('custom', 'Custom Reports'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    template_config = models.JSONField(default=dict)  # Store report configuration
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['report_type', 'name']
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class GeneratedReport(models.Model):
    """
    Store generated reports and their metadata
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    
    title = models.CharField(max_length=200)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, null=True, blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    
    # Date range for the report
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Report parameters
    parameters = models.JSONField(default=dict)
    
    # File storage
    file_path = models.FileField(upload_to='reports/%Y/%m/', blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Metadata
    total_records = models.PositiveIntegerField(null=True, blank=True)
    generation_time = models.DurationField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Generated Report'
        verbose_name_plural = 'Generated Reports'
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def is_ready(self):
        return self.status == 'completed' and self.file_path


class FinancialSummary(models.Model):
    """
    Monthly/Yearly financial summary data for quick reporting
    """
    PERIOD_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Revenue
    total_rent_collected = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_other_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Expenses
    total_maintenance_costs = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_utility_costs = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_management_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_other_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Calculated fields
    net_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Occupancy
    total_units = models.PositiveIntegerField(default=0)
    occupied_units = models.PositiveIntegerField(default=0)
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Maintenance
    maintenance_requests = models.PositiveIntegerField(default=0)
    completed_maintenance = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['period_type', 'period_start']
        verbose_name = 'Financial Summary'
        verbose_name_plural = 'Financial Summaries'
    
    def __str__(self):
        return f"{self.get_period_type_display()} Summary - {self.period_start}"
