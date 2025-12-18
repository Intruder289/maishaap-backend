from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    RentInvoiceViewSet, RentPaymentViewSet, LateFeeViewSet, 
    RentReminderViewSet, RentDashboardViewSet
)

# API Router
router = DefaultRouter()
router.register(r'invoices', RentInvoiceViewSet, basename='rent-invoices')
router.register(r'payments', RentPaymentViewSet, basename='rent-payments')
router.register(r'late-fees', LateFeeViewSet, basename='late-fees')
router.register(r'reminders', RentReminderViewSet, basename='rent-reminders')
router.register(r'dashboard', RentDashboardViewSet, basename='rent-dashboard')

app_name = 'rent-api'

urlpatterns = [
    path('', include(router.urls)),
]