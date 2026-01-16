from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_dashboard, name='dashboard'),
    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('transactions/', views.payment_transactions, name='payment_transactions'),
    
    # Payment Action API endpoints
    path('api/payment/<int:payment_id>/view-details/', views.payment_view_details, name='payment_view_details'),
    path('api/payment/<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('api/payment/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('api/payment/<int:payment_id>/generate-receipt/', views.payment_generate_receipt, name='payment_generate_receipt'),
    
    # Transaction Action API endpoints
    path('api/transaction/<int:transaction_id>/view-details/', views.transaction_view_details, name='transaction_view_details'),
    path('api/transaction/<int:transaction_id>/delete/', views.transaction_delete, name='transaction_delete'),
    path('api/transaction/<int:transaction_id>/verify/', views.transaction_verify, name='transaction_verify'),
    
    # Payment Provider Action API endpoints
    path('api/provider/<int:provider_id>/view-details/', views.provider_view_details, name='provider_view_details'),
    path('api/provider/<int:provider_id>/edit/', views.provider_edit, name='provider_edit'),
    path('api/provider/<int:provider_id>/toggle-status/', views.provider_toggle_status, name='provider_toggle_status'),
]
