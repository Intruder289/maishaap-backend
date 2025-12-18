from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('financial/', views.financial_reports, name='financial'),
    path('maintenance/', views.maintenance_reports_redirect, name='maintenance'),
    path('generate/', views.generate_report, name='generate'),
    path('download/<int:report_id>/', views.download_report, name='download'),
    path('view/<int:report_id>/', views.view_report, name='view'),
    path('generate-financial/', views.generate_financial_report, name='generate_financial'),
    path('financial-excel/', views.financial_excel_report, name='financial_excel'),
    path('export-payment/', views.export_payment_report, name='export_payment'),
    path('export-booking/', views.export_booking_report, name='export_booking'),
]