from django.urls import path
from . import api_views

app_name = 'properties_api'

# API URLs for mobile app (v1) - Mobile endpoints only
# Note: AJAX endpoints are in api_urls_ajax.py for web interface
urlpatterns = [
    # Property CRUD
    path('properties/', api_views.PropertyListCreateAPIView.as_view(), name='property_list_create'),
    path('properties/<int:pk>/', api_views.PropertyDetailAPIView.as_view(), name='property_detail'),
    path('properties/<int:pk>/toggle-status/', api_views.PropertyToggleStatusAPIView.as_view(), name='property_toggle_status'),
    path('properties/<int:pk>/delete/', api_views.PropertyDeleteAPIView.as_view(), name='property_delete'),
    
    # User properties
    path('my-properties/', api_views.MyPropertiesAPIView.as_view(), name='my_properties'),
    
    # Property metadata
    path('property-types/', api_views.PropertyTypeListAPIView.as_view(), name='property_types'),
    path('property-types/<int:pk>/', api_views.PropertyTypeDetailAPIView.as_view(), name='property_type_detail'),
    # Categories endpoint (alias for property-types for mobile app home screen)
    path('categories/', api_views.PropertyTypeListAPIView.as_view(), name='categories'),
    path('regions/', api_views.RegionListAPIView.as_view(), name='regions'),
    path('regions/<int:pk>/', api_views.RegionDetailAPIView.as_view(), name='region_detail'),
    path('districts/', api_views.DistrictListAPIView.as_view(), name='districts'),
    path('districts/<int:pk>/', api_views.DistrictDetailAPIView.as_view(), name='district_detail'),
    path('amenities/', api_views.AmenityListAPIView.as_view(), name='amenities'),
    path('amenities/<int:pk>/', api_views.AmenityDetailAPIView.as_view(), name='amenity_detail'),
    
    # Property images
    path('property-images/', api_views.PropertyImageUploadAPIView.as_view(), name='property_image_upload'),
    
    # Favorites
    path('favorites/', api_views.FavoritePropertiesAPIView.as_view(), name='favorite_properties'),
    path('toggle-favorite/', api_views.toggle_favorite, name='toggle_favorite'),
    
    # Search and filters
    path('search/', api_views.property_search, name='property_search'),
    
    # Special endpoints
    path('featured/', api_views.featured_properties, name='featured_properties'),
    path('recent/', api_views.recent_properties, name='recent_properties'),
    path('stats/', api_views.property_stats, name='property_stats'),
    
    # Booking endpoints
    path('bookings/<int:booking_id>/details/', api_views.booking_details_api, name='booking_details_api'),
    path('bookings/<int:booking_id>/status-update/', api_views.booking_status_update_api, name='booking_status_update_api'),
    path('bookings/<int:booking_id>/edit/', api_views.booking_edit_api, name='booking_edit_api'),
    
    # Visit payment endpoints (house properties only)
    path('properties/<int:property_id>/visit/status/', api_views.property_visit_status, name='property_visit_status'),
    path('properties/<int:property_id>/visit/initiate/', api_views.property_visit_initiate, name='property_visit_initiate'),
    path('properties/<int:property_id>/visit/verify/', api_views.property_visit_verify, name='property_visit_verify'),
    
    # Available rooms endpoint (hotels/lodges only)
    path('available-rooms/', api_views.available_rooms_api, name='available_rooms_api'),
    
    # Create booking with room number endpoint (mobile app)
    path('bookings/create/', api_views.create_booking_with_room_api, name='create_booking_with_room_api'),
]