from django.urls import path
from complaints import views

app_name = 'complaints'

urlpatterns = [
    # Complaint URLs
    path('', views.complaint_list, name='complaint_list'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('create/', views.complaint_create, name='complaint_create'),
    path('<int:pk>/update-status/', views.complaint_update_status, name='complaint_update_status'),
    path('<int:pk>/add-response/', views.add_complaint_response, name='add_complaint_response'),
    path('<int:pk>/delete/', views.complaint_delete, name='complaint_delete'),
    path('test-ajax/', views.test_ajax, name='test_ajax'),
    
    # Feedback URLs
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/create/', views.feedback_create, name='feedback_create'),
    path('feedback/form/', views.feedback_form, name='feedback_form'),
    
    # Dashboard (staff only)
    path('dashboard/', views.complaint_dashboard, name='dashboard'),
]