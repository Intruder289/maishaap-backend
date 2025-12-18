from django.urls import path, include
from rest_framework.routers import DefaultRouter
from documents.api_views import LeaseViewSet, BookingViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]
