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
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Maisha Backend API",
      default_version='v1',
      description="API for Flutter mobile application with role-based authentication (Tenant/Owner) and admin approval workflow",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@maisha.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    # Properties web interface
    path('properties/', include('properties.urls')),
    # API endpoints for mobile app (v1)
    path('api/v1/', include('accounts.api_urls')),
    path('api/v1/', include('properties.api_urls')),
    path('api/v1/', include('payments.api_urls')),
    path('api/v1/', include('documents.api_urls')),
    path('api/v1/rent/', include('rent.api_urls')),
    path('api/v1/maintenance/', include('maintenance.api_urls')),
    path('api/v1/reports/', include('reports.api_urls')),
    path('api/v1/complaints/', include('complaints.api_urls')),
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
    # Swagger documentation URLs
    # Note: Order matters - more specific patterns should come first
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Explicit OpenAPI schema endpoints (for direct access)
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json-alt'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
    # Handle query parameter format (Swagger UI uses ?format=openapi)
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json-slash'),
    path('swagger.yaml/', schema_view.without_ui(cache_timeout=0), name='schema-yaml-slash'),
    # Redirect common /accounts/... paths to the primary routes to avoid
    # including the same URLconf twice (which creates a duplicate namespace).
    # path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
