from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('settings/', views.settings_view, name='settings'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    
    # MULTI-TENANCY: Owner Management
    path('owners/', views.owner_list, name='owner_list'),
    path('owners/register/', views.register_owner, name='register_owner'),
    path('owners/<int:user_id>/activate/', views.activate_owner, name='activate_owner'),
    path('owners/<int:user_id>/deactivate/', views.deactivate_owner, name='deactivate_owner'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/profile/', views.user_profile_view, name='user_profile'),
    path('users/<int:user_id>/assign-role/', views.assign_user_role, name='assign_user_role'),
    path('users/<int:user_id>/edit-roles/', views.edit_user_roles, name='edit_user_roles'),
    path('users/<int:user_id>/remove-role/<int:role_id>/', views.remove_user_role, name='remove_user_role'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/activate/', views.activate_user, name='activate_user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user, name='deactivate_user'),
    
    # Role Management  
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.create_role, name='create_role'),
    path('roles/<int:role_id>/edit/', views.edit_role, name='edit_role'),
    path('roles/<int:role_id>/delete/', views.delete_role, name='delete_role'),
    path('permissions/', views.manage_permissions, name='manage_permissions'),
    
    # System Logs
    path('system-logs/', views.system_logs, name='system_logs'),
    
    # AJAX endpoints
    path('api/permissions/', views.get_permissions, name='get_permissions'),
    path('api/navigation-items/', views.get_navigation_items, name='get_navigation_items'),
    path('debug/navigation-items/', views.debug_navigation_items, name='debug_navigation_items'),
    path('api/roles/create/', views.create_role_ajax, name='create_role_ajax'),
    path('api/roles/<int:role_id>/navigation/', views.get_role_navigation, name='get_role_navigation'),
    path('api/roles/navigation/edit/', views.edit_role_navigation, name='edit_role_navigation'),
    path('api/roles/for-user-creation/', views.get_roles_for_user_creation, name='get_roles_for_user_creation'),
    path('api/users/create/', views.create_user_ajax, name='create_user_ajax'),
    path('api/users/<int:user_id>/roles/', views.get_user_roles, name='get_user_roles'),
    path('api/users/<int:user_id>/roles/update/', views.update_user_roles_ajax, name='update_user_roles_ajax'),
    path('api/dashboard/properties/', views.dashboard_properties_ajax, name='dashboard_properties_ajax'),
    
    # Password reset and notifications
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path('notifications/', views.notifications_list, name='notifications_list'),

    # Firebase-related routes removed (unused)
    
    # Houses/Properties Management
    path('houses/', views.houses_list, name='houses_list'),
    path('houses/<int:pk>/', views.house_detail, name='house_detail'),
    path('houses/create/', views.house_create, name='house_create'),
    path('houses/<int:pk>/edit/', views.house_edit, name='house_edit'),
    path('houses/<int:pk>/delete/', views.house_delete, name='house_delete'),
    path('houses/bulk-delete/', views.bulk_delete_houses, name='bulk_delete_houses'),
    path('houses/my-houses/', views.my_houses, name='my_houses'),
    path('houses/manage-metadata/', views.house_manage_metadata, name='house_manage_metadata'),
    
    # Metadata deletion
    path('houses/metadata/property-type/<int:pk>/delete/', views.delete_property_type, name='delete_property_type'),
    path('houses/metadata/region/<int:pk>/delete/', views.delete_region, name='delete_region'),
    path('houses/metadata/amenity/<int:pk>/delete/', views.delete_amenity, name='delete_amenity'),
]

