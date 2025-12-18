from django.contrib import admin
from .models import MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'property', 'tenant', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']