from django.urls import path, include
from accounts import api_views, api_views_ajax

app_name = 'accounts_api'

# API URLs for mobile app (v1)
urlpatterns = [
    # Test endpoint
    path('', api_views.api_root, name='api_root'),
    path('test/', api_views.api_test, name='api_test'),
    
    # Authentication endpoints
    path('auth/signup/', api_views.tenant_signup, name='api_tenant_signup'),
    path('auth/login/', api_views.tenant_login, name='api_tenant_login'),
    path('auth/logout/', api_views.tenant_logout, name='api_tenant_logout'),
    path('auth/forgot-password/', api_views.forgot_password, name='api_forgot_password'),
    path('auth/refresh/', api_views.refresh_token, name='api_refresh_token'),
    path('auth/verify/', api_views.verify_token, name='api_verify_token'),
    
    # Profile endpoints
    path('auth/profile/', api_views.tenant_profile, name='api_tenant_profile'),
    path('auth/profile/update/', api_views.update_tenant_profile, name='api_update_tenant_profile'),
    path('auth/change-password/', api_views.change_password, name='api_change_password'),
    
    # Admin endpoints
    path('admin/pending-users/', api_views.pending_users, name='api_pending_users'),
    path('admin/approve-user/', api_views.approve_user, name='api_approve_user'),
    
    # MULTI-TENANCY: Admin owner management endpoints
    path('admin/register-owner/', api_views.admin_register_owner, name='api_admin_register_owner'),
    path('admin/list-owners/', api_views.admin_list_owners, name='api_admin_list_owners'),
    path('admin/activate-deactivate-owner/', api_views.admin_activate_deactivate_owner, name='api_admin_activate_deactivate_owner'),
    
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
    path('users/<int:user_id>/roles/', api_views_ajax.user_roles_api, name='api_user_roles'),
    path('users/<int:user_id>/roles/update/', api_views_ajax.user_roles_update_api, name='api_user_roles_update'),
    path('profile/update/', api_views_ajax.profile_update_api, name='api_profile_update'),
]