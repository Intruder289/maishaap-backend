from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'requests', api_views.MaintenanceRequestViewSet, basename='maintenance-request')

urlpatterns = [
    path('', include(router.urls)),
]