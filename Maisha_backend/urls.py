"""
URL configuration for Maisha_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# =============================================================================
# API LAYER (DRF-only) - For Mobile App
# =============================================================================
# These are the ONLY endpoints that should appear in Swagger documentation
# All endpoints use Django REST Framework (DRF) views/viewsets
api_patterns = [
    path('api/v1/', include('accounts.api_urls')),
    path('api/v1/', include('properties.api_urls')),
    path('api/v1/', include('payments.api_urls')),
    path('api/v1/', include('documents.api_urls')),
    path('api/v1/rent/', include('rent.api_urls')),
    path('api/v1/maintenance/', include('maintenance.api_urls')),
    path('api/v1/reports/', include('reports.api_urls')),
    path('api/v1/complaints/', include('complaints.api_urls')),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    # Properties web interface
    path('properties/', include('properties.urls')),
    # API endpoints for mobile app (v1) - using api_patterns defined above
] + api_patterns + [
    # AJAX API endpoints for web interface (with unique namespace to avoid conflicts)
    # Note: Only AJAX endpoints, no mobile app endpoints (those are only in /api/v1/)
    path('api/', include(('accounts.api_urls_ajax', 'accounts'), namespace='accounts_ajax')),
    path('api/', include(('properties.api_urls_ajax', 'properties'), namespace='properties_ajax')),
    # Web views
    path('payments/', include('payments.urls')),
    path('documents/', include('documents.urls')),
    path('rent/', include('rent.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('reports/', include('reports.urls')),
    path('complaints/', include('complaints.urls')),
    # =============================================================================
    # SWAGGER DOCUMENTATION (API Layer Only)
    # =============================================================================
    # Swagger ONLY documents DRF API endpoints (/api/v1/)
    # AJAX endpoints (/api/) and web views are excluded
    path('api/schema/', SpectacularAPIView.as_view(patterns=api_patterns), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Legacy URLs for backward compatibility
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-legacy'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-legacy'),
    path('swagger.json', SpectacularAPIView.as_view(patterns=api_patterns), name='schema-json'),
    path('swagger.yaml', SpectacularAPIView.as_view(patterns=api_patterns), name='schema-yaml'),
    # Redirect common /accounts/... paths to the primary routes to avoid
    # including the same URLconf twice (which creates a duplicate namespace).
    # path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),
]

if settings.DEBUG:
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve static files in development (including drf-yasg static files)
    # Serve from STATIC_ROOT where collectstatic puts all static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
