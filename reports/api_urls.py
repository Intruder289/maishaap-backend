from django.urls import path
from . import api_views

app_name = 'reports_api'

urlpatterns = [
    # Financial reports
    path('financial/summary/', api_views.FinancialSummaryView, name='financial-summary'),
    path('financial/rent-collection/', api_views.RentCollectionReportView, name='rent-collection'),
    path('financial/expenses/', api_views.ExpenseReportView, name='expense-report'),
    
    # Property reports
    path('properties/occupancy/', api_views.PropertyOccupancyReportView, name='property-occupancy'),
    path('properties/maintenance/', api_views.MaintenanceReportView, name='maintenance-report'),
    
    # Dashboard analytics
    path('dashboard/stats/', api_views.DashboardStatsView, name='dashboard-stats'),
    path('dashboard/charts/', api_views.DashboardChartsView, name='dashboard-charts'),
]