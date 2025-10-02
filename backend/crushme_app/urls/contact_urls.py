"""
Contact URLs for CrushMe e-commerce application
Handles contact form submissions and management
"""
from django.urls import path
from ..views.contact_views import (
    create_contact, get_all_contacts, get_contact_detail,
    update_contact_status, delete_contact
)

urlpatterns = [
    # Public endpoint - anyone can submit a contact form
    path('', create_contact, name='create_contact'),
    
    # Admin endpoints - manage contact messages
    path('all/', get_all_contacts, name='get_all_contacts'),
    path('<int:contact_id>/', get_contact_detail, name='get_contact_detail'),
    path('<int:contact_id>/status/', update_contact_status, name='update_contact_status'),
    path('<int:contact_id>/delete/', delete_contact, name='delete_contact'),
]


