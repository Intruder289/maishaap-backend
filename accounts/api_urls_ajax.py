from django.urls import path
from accounts import api_views_ajax

# AJAX API URLs for web interface only (no authentication endpoints)
# These endpoints are used by the web interface for AJAX operations
urlpatterns = [
    # AJAX endpoints for table functionality
    path('users/search/', api_views_ajax.user_search_api, name='api_user_search'),
    path('users/detail/', api_views_ajax.user_detail_api, name='api_user_detail'),
    path('users/update/', api_views_ajax.user_update_api, name='api_user_update'),
    path('users/<int:user_id>/toggle-status/', api_views_ajax.user_toggle_status_api, name='api_user_toggle_status'),
    path('users/<int:user_id>/toggle-approval/', api_views_ajax.user_toggle_approval_api, name='api_user_toggle_approval'),
    path('users/<int:user_id>/reset-password/', api_views_ajax.user_reset_password_api, name='api_user_reset_password'),
    path('users/<int:user_id>/delete/', api_views_ajax.user_delete_api, name='api_user_delete'),
    path('users/create/', api_views_ajax.user_create_api, name='api_user_create'),
    path('roles/search/', api_views_ajax.role_search_api, name='api_role_search'),
    path('roles/detail/', api_views_ajax.role_detail_api, name='api_role_detail'),
    path('roles/update/', api_views_ajax.role_update_api, name='api_role_update'),
    path('roles/permissions/', api_views_ajax.role_permissions_api, name='api_role_permissions'),
    path('roles/permissions/detail/', api_views_ajax.role_permissions_detail_api, name='api_role_permissions_detail'),
    path('roles/create/', api_views_ajax.role_create_api, name='api_role_create'),
    path('roles/<int:role_id>/delete/', api_views_ajax.role_delete_api, name='api_role_delete'),
    path('users/<int:user_id>/roles/', api_views_ajax.user_roles_api, name='api_user_roles'),
    path('users/<int:user_id>/roles/update/', api_views_ajax.user_roles_update_api, name='api_user_roles_update'),
    path('profile/update/', api_views_ajax.profile_update_api, name='api_profile_update'),
    # Notification endpoints
    path('notifications/count/', api_views_ajax.notification_count_api, name='api_notification_count'),
    path('notifications/<int:notification_id>/mark-read/', api_views_ajax.notification_mark_read_api, name='api_notification_mark_read'),
    path('notifications/<int:notification_id>/delete/', api_views_ajax.notification_delete_api, name='api_notification_delete'),
    path('notifications/mark-all-read/', api_views_ajax.notification_mark_all_read_api, name='api_notification_mark_all_read'),
]

