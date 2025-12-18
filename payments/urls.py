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
]
