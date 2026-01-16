from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.property_dashboard, name='dashboard'),
    
    # Property CRUD
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('create/', views.property_create, name='property_create'),
    path('<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('<int:pk>/delete/', views.property_delete, name='property_delete'),
    
    # Property Image Management
    path('<int:pk>/images/add/', views.property_image_add, name='property_image_add'),
    path('<int:pk>/images/<int:image_id>/delete/', views.property_image_delete, name='property_image_delete'),
    path('<int:pk>/images/<int:image_id>/set-primary/', views.property_image_set_primary, name='property_image_set_primary'),
    path('<int:pk>/images/<int:image_id>/update-caption/', views.property_image_update_caption, name='property_image_update_caption'),
    
    # User properties
    path('my-properties/', views.my_properties, name='my_properties'),
    path('favorites/', views.favorites, name='favorites'),
    
    # AJAX endpoints
    path('toggle-favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('geocode-address/', views.geocode_property_address, name='geocode_address'),
    
    # Management views
    path('manage/regions/', views.manage_regions, name='manage_regions'),
    path('manage/districts/', views.manage_districts, name='manage_districts'),
    path('manage/property-types/', views.manage_property_types, name='manage_property_types'),
    path('manage/amenities/', views.manage_amenities, name='manage_amenities'),
    
    # Property Approval Management
    path('approval/', views.property_approval_list, name='property_approval_list'),
    path('approval/<int:pk>/', views.property_approval_detail, name='property_approval_detail'),
    path('approval/<int:pk>/approve/', views.approve_property, name='approve_property'),
    path('approval/<int:pk>/reject/', views.reject_property, name='reject_property'),
    path('approval/<int:pk>/delete/', views.delete_approval_request, name='delete_approval_request'),
    
    # Hotel Management
    path('hotel/dashboard/', views.hotel_dashboard, name='hotel_dashboard'),
    path('hotel/bookings/', views.hotel_bookings, name='hotel_bookings'),
    path('hotel/rooms/', views.hotel_rooms, name='hotel_rooms'),
    path('hotel/customers/', views.hotel_customers, name='hotel_customers'),
    path('hotel/payments/', views.hotel_payments, name='hotel_payments'),
    path('hotel/reports/', views.hotel_reports, name='hotel_reports'),
    path('hotel/select-property/', views.hotel_select_property, name='hotel_select_property'),
    path('hotel/clear-selection/', views.hotel_clear_selection, name='hotel_clear_selection'),
    path('hotel/add-room/', views.add_room, name='add_room'),
    
    # Room Management API endpoints
    path('api/room/<int:room_id>/', views.api_room_detail, name='api_room_detail'),
    path('api/room/<int:room_id>/edit/', views.api_edit_room, name='api_edit_room'),
    path('api/room/<int:room_id>/status/', views.api_update_room_status, name='api_update_room_status'),
    path('api/room/<int:room_id>/delete/', views.api_delete_room, name='api_delete_room'),
    
    # Customer Management
    path('customers/create/', views.create_customer, name='create_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.edit_customer, name='edit_customer'),
    
    # Customer AJAX Modal endpoints
    path('customer/<int:pk>/profile/', views.customer_profile_modal, name='customer_profile_modal'),
    path('customer/<int:pk>/edit/', views.customer_edit_modal, name='customer_edit_modal'),
    path('customer/<int:pk>/bookings/', views.customer_booking_history_modal, name='customer_booking_history_modal'),
    path('customer/<int:pk>/new-booking/', views.customer_new_booking_modal, name='customer_new_booking_modal'),
    path('customer/<int:pk>/vip-status/', views.customer_vip_status_modal, name='customer_vip_status_modal'),
    
    # Payment Management
    path('bookings/<int:booking_id>/payment/', views.create_payment, name='create_payment'),
    path('payments/<int:payment_id>/record/', views.create_payment, {'booking_id': None}, name='create_visit_payment'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    
    # Payment API endpoints
    path('api/payment-details/<int:payment_id>/', views.api_payment_details, name='api_payment_details'),
    path('api/booking-status/<int:booking_id>/', views.api_booking_status, name='api_booking_status'),
    path('api/booking/<int:booking_id>/cancel/', views.api_booking_cancel, name='api_booking_cancel'),
    path('api/booking/<int:booking_id>/soft-delete/', views.api_booking_soft_delete, name='api_booking_soft_delete'),
    path('api/booking/<int:booking_id>/restore/', views.api_booking_restore, name='api_booking_restore'),
    path('api/available-rooms/', views.api_available_rooms, name='api_available_rooms'),
    path('api/create-booking/', views.api_create_booking, name='api_create_booking'),
    path('api/collect-payment/', views.api_collect_payment, name='api_collect_payment'),
    path('api/process-refund/', views.api_process_refund, name='api_process_refund'),
    
    # Lodge Management
    path('lodge/dashboard/', views.lodge_dashboard, name='lodge_dashboard'),
    path('lodge/bookings/', views.lodge_bookings, name='lodge_bookings'),
    path('lodge/rooms/', views.lodge_rooms, name='lodge_rooms'),
    path('lodge/customers/', views.lodge_customers, name='lodge_customers'),
    path('lodge/payments/', views.lodge_payments, name='lodge_payments'),
    path('lodge/reports/', views.lodge_reports, name='lodge_reports'),
    path('lodge/reports/export/', views.lodge_reports_export, name='lodge_reports_export'),
    path('lodge/select-property/', views.lodge_select_property, name='lodge_select_property'),
    path('lodge/clear-selection/', views.lodge_clear_selection, name='lodge_clear_selection'),
    path('lodge/create-booking/', views.create_lodge_booking, name='create_lodge_booking'),
    path('lodge/add-room/', views.add_lodge_room, name='add_lodge_room'),
    
    # Venue Management
    path('venue/dashboard/', views.venue_dashboard, name='venue_dashboard'),
    path('venue/bookings/', views.venue_bookings, name='venue_bookings'),
    path('venue/availability/', views.venue_availability, name='venue_availability'),
    path('venue/customers/', views.venue_customers, name='venue_customers'),
    path('venue/payments/', views.venue_payments, name='venue_payments'),
    path('venue/reports/', views.venue_reports, name='venue_reports'),
    path('venue/reports/export/', views.venue_reports_export, name='venue_reports_export'),
    path('venue/select-property/', views.venue_select_property, name='venue_select_property'),
    path('venue/clear-selection/', views.venue_clear_selection, name='venue_clear_selection'),
    path('venue/create-booking/', views.create_venue_booking, name='create_venue_booking'),
    
    # House Management
    path('house/dashboard/', views.house_dashboard, name='house_dashboard'),
    path('house/bookings/', views.house_bookings, name='house_bookings'),
    path('house/tenants/', views.house_tenants, name='house_tenants'),
    path('house/payments/', views.house_payments, name='house_payments'),
    path('house/reports/', views.house_reports, name='house_reports'),
    path('house/reports/export/', views.house_reports_export, name='house_reports_export'),
    path('house/select-property/', views.house_select_property, name='house_select_property'),
    path('house/clear-selection/', views.house_clear_selection, name='house_clear_selection'),
    path('house/create-booking/', views.create_house_booking, name='create_house_booking'),
    
    # House Rent Reminders
    path('house/rent-reminders/', views.house_rent_reminders_dashboard, name='house_rent_reminders_dashboard'),
    path('house/rent-reminders/list/', views.house_rent_reminders_list, name='house_rent_reminders_list'),
    path('house/rent-reminders/<int:reminder_id>/', views.house_rent_reminder_detail, name='house_rent_reminder_detail'),
    path('house/rent-reminders/settings/', views.house_rent_reminder_settings, name='house_rent_reminder_settings'),
    path('house/rent-reminders/templates/', views.house_rent_reminder_templates, name='house_rent_reminder_templates'),
    path('house/rent-reminders/templates/<int:template_id>/', views.house_rent_reminder_template_detail, name='house_rent_reminder_template_detail'),
    path('house/rent-reminders/analytics/', views.house_rent_reminder_analytics, name='house_rent_reminder_analytics'),
    path('house/rent-reminders/send-manual/', views.send_manual_reminder, name='send_manual_reminder'),
    path('house/rent-reminders/cancel/', views.cancel_reminder, name='cancel_reminder'),
    
    # Property availability API endpoint
    path('api/property/<int:property_id>/availability/', views.api_property_availability, name='api_property_availability'),
    
    # Hotel room status summary API endpoint
    path('api/hotel/<int:property_id>/room-status-summary/', views.api_hotel_room_status_summary, name='api_hotel_room_status_summary'),
    
    # Booking API endpoints for modals
    path('api/booking/<int:booking_id>/details/', views.api_booking_details, name='api_booking_details'),
    path('api/booking/<int:booking_id>/edit/', views.api_booking_edit, name='api_booking_edit'),
    path('api/booking/<int:booking_id>/confirm/', views.api_booking_confirm, name='api_booking_confirm'),
    path('api/booking/<int:booking_id>/checkin/', views.api_booking_checkin, name='api_booking_checkin'),
    path('api/booking/<int:booking_id>/checkout/', views.api_booking_checkout, name='api_booking_checkout'),
    path('api/booking/<int:booking_id>/payments/', views.api_booking_payments, name='api_booking_payments'),
    path('api/booking/<int:booking_id>/invoice/', views.api_booking_invoice, name='api_booking_invoice'),
    path('api/booking/<int:booking_id>/invoice/download/', views.api_booking_invoice_download, name='api_booking_invoice_download'),
    path('api/booking/<int:booking_id>/invoice/email/', views.api_booking_invoice_email, name='api_booking_invoice_email'),
    path('api/booking/<int:booking_id>/cancel/', views.api_booking_cancel, name='api_booking_cancel'),
    path('api/booking/<int:booking_id>/update-total/', views.api_booking_update_total, name='api_booking_update_total'),
    
    # Tenant Management API endpoints for modals
    path('api/tenant/<int:tenant_id>/profile/', views.api_tenant_profile, name='api_tenant_profile'),
    path('api/tenant/<int:tenant_id>/edit/', views.api_tenant_edit, name='api_tenant_edit'),
    path('api/tenant/<int:tenant_id>/lease-history/', views.api_tenant_lease_history, name='api_tenant_lease_history'),
    path('api/tenant/<int:tenant_id>/payment-history/', views.api_tenant_payment_history, name='api_tenant_payment_history'),
    path('api/tenant/<int:tenant_id>/make-vip/', views.api_tenant_make_vip, name='api_tenant_make_vip'),
    path('api/tenant/<int:tenant_id>/remove-vip/', views.api_tenant_remove_vip, name='api_tenant_remove_vip'),
    
    # Property API endpoints for modals
    path('api/property/<int:property_id>/details/', views.api_property_details, name='api_property_details'),
    
    # Payment API endpoints
    path('api/record-payment/', views.api_record_payment, name='api_record_payment'),
    
    # Payment Action API endpoints
    path('api/payment/<int:payment_id>/view-details/', views.api_payment_view_details, name='api_payment_view_details'),
    path('api/payment/<int:payment_id>/generate-receipt/', views.api_payment_generate_receipt, name='api_payment_generate_receipt'),
    path('api/payment/<int:payment_id>/download-receipt/', views.api_payment_download_receipt, name='api_payment_download_receipt'),
    path('api/payment/<int:payment_id>/edit/', views.api_payment_edit, name='api_payment_edit'),
    path('api/payment/<int:payment_id>/mark-paid/', views.api_payment_mark_paid, name='api_payment_mark_paid'),
    path('api/payment/<int:payment_id>/delete/', views.api_payment_delete, name='api_payment_delete'),
    path('api/payment/<int:payment_id>/booking-details/', views.api_payment_booking_details, name='api_payment_booking_details'),
    path('api/payment/<int:payment_id>/property-details/', views.api_payment_property_details, name='api_payment_property_details'),
    path('api/payment/<int:payment_id>/send-reminder/', views.api_payment_send_reminder, name='api_payment_send_reminder'),
    
    # Visit Payment API endpoints (for web interface)
    path('api/visit-payment/<int:property_id>/status/', views.api_visit_payment_status, name='api_visit_payment_status'),
    path('api/visit-payment/<int:property_id>/initiate/', views.api_visit_payment_initiate, name='api_visit_payment_initiate'),
    path('api/visit-payment/<int:property_id>/verify/', views.api_visit_payment_verify, name='api_visit_payment_verify'),
    
    # Venue Management API endpoints
    path('api/venue/<int:venue_id>/details/', views.api_venue_details, name='api_venue_details'),
    path('api/venue/availability/', views.api_venue_availability, name='api_venue_availability'),
    path('api/venue/booking/<int:booking_id>/status/', views.api_venue_booking_status, name='api_venue_booking_status'),
    path('api/venue/capacity-check/', views.api_venue_capacity_check, name='api_venue_capacity_check'),
    path('api/venue/analytics/', views.api_venue_analytics, name='api_venue_analytics'),
    
    # Test endpoints
    path('test/bookings/', views.test_bookings, name='test_bookings'),
]