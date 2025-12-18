from django.urls import path
from . import views

app_name = 'rent'

urlpatterns = [
    # Dashboard
    path('', views.rent_dashboard, name='dashboard'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    
    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/record/', views.record_payment_general, name='record_payment_general'),
    path('invoices/<int:invoice_id>/pay/', views.record_payment, name='record_payment'),
    
    # Tenant summaries
    path('tenant-summary/', views.tenant_summary, name='tenant_summary'),
    path('tenant-summary/<int:tenant_id>/', views.tenant_summary, name='tenant_summary_detail'),
]