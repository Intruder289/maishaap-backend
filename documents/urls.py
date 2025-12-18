from django.urls import path
from documents import views

app_name = 'documents'

urlpatterns = [
    path('leases/', views.lease_list, name='lease_list'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:doc_id>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:doc_id>/delete/', views.document_delete, name='document_delete'),
]
