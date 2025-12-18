from rest_framework import routers
from . import api_views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'providers', api_views.PaymentProviderViewSet, basename='provider')
router.register(r'invoices', api_views.InvoiceViewSet, basename='invoice')
router.register(r'payments', api_views.PaymentViewSet, basename='payment')
router.register(r'transactions', api_views.PaymentTransactionViewSet, basename='transaction')
router.register(r'audits', api_views.PaymentAuditViewSet, basename='audit')
router.register(r'expenses', api_views.ExpenseViewSet, basename='expense')

urlpatterns = [
    path('payments/', include(router.urls)),
    # Webhook endpoint (no authentication required)
    path('payments/webhook/azam-pay/', api_views.azam_pay_webhook, name='azam-pay-webhook'),
]
