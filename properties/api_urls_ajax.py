from django.urls import path
from . import api_views_ajax

# AJAX API URLs for web interface only (no mobile app endpoints)
# These endpoints are used by the web interface for AJAX operations
urlpatterns = [
    # AJAX endpoints for table functionality
    path('properties/search/', api_views_ajax.property_search_api, name='api_property_search'),
    path('properties/<int:property_id>/toggle-status/', api_views_ajax.property_toggle_status_api, name='api_property_toggle_status'),
    path('properties/<int:property_id>/delete/', api_views_ajax.property_delete_api, name='api_property_delete'),
    path('properties/create/', api_views_ajax.property_create_api, name='api_property_create'),
    path('properties/form-data/', api_views_ajax.property_form_data_api, name='api_property_form_data'),
    path('districts/by-region/', api_views_ajax.districts_by_region_api, name='api_districts_by_region'),
    
    # Metadata management AJAX endpoints
    path('property-types/<int:property_type_id>/update/', api_views_ajax.property_type_update_api, name='api_property_type_update'),
    path('property-types/<int:property_type_id>/delete-ajax/', api_views_ajax.property_type_delete_api, name='api_property_type_delete'),
    path('regions/<int:region_id>/update/', api_views_ajax.region_update_api, name='api_region_update'),
    path('regions/<int:region_id>/delete-ajax/', api_views_ajax.region_delete_api, name='api_region_delete'),
    path('amenities/<int:amenity_id>/update/', api_views_ajax.amenity_update_api, name='api_amenity_update'),
    path('amenities/<int:amenity_id>/delete-ajax/', api_views_ajax.amenity_delete_api, name='api_amenity_delete'),
    
    # Property owner assignment
    path('property-owners/', api_views_ajax.get_property_owners_api, name='api_get_property_owners'),
    path('properties/<int:property_id>/assign-owner/', api_views_ajax.assign_property_owner_api, name='api_assign_property_owner'),
]

