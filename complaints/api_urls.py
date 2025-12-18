from rest_framework.routers import DefaultRouter
from django.urls import path, include
from complaints.api_views import ComplaintViewSet, FeedbackViewSet, ComplaintResponseViewSet

# Create router for API endpoints
router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'responses', ComplaintResponseViewSet)

# API URLs for complaints module
urlpatterns = [
    path('', include(router.urls)),
]