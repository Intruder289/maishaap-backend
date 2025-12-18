from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('requests/', views.request_list, name='request_list'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/form/', views.request_form, name='request_form'),
    path('test-ajax/', views.test_ajax, name='test_ajax'),
]