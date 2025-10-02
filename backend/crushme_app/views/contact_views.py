"""
Views for Contact model
Handles contact form submissions
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from ..models.contact import Contact
from ..serializers.contact_serializers import (
    ContactCreateSerializer, ContactListSerializer,
    ContactDetailSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_contact(request):
    """
    Create a new contact message
    
    Required fields:
    - email: Email del contacto
    - nombre: Nombre completo
    - asunto: Asunto del mensaje
    - texto: Contenido del mensaje
    
    Optional fields:
    - numero: Número de teléfono
    """
    serializer = ContactCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        contact = serializer.save()
        detail_serializer = ContactDetailSerializer(contact)
        
        return Response({
            'success': True,
            'message': 'Mensaje de contacto enviado exitosamente. Te responderemos pronto.',
            'contact': detail_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_contacts(request):
    """
    Get all contact messages (Admin only)
    
    Query params:
    - is_read: Filter by read status (true/false)
    - is_responded: Filter by responded status (true/false)
    """
    contacts = Contact.objects.all()
    
    # Apply filters if provided
    is_read = request.query_params.get('is_read')
    if is_read is not None:
        is_read = is_read.lower() == 'true'
        contacts = contacts.filter(is_read=is_read)
    
    is_responded = request.query_params.get('is_responded')
    if is_responded is not None:
        is_responded = is_responded.lower() == 'true'
        contacts = contacts.filter(is_responded=is_responded)
    
    serializer = ContactListSerializer(contacts, many=True)
    
    return Response({
        'success': True,
        'total_contacts': contacts.count(),
        'contacts': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_contact_detail(request, contact_id):
    """
    Get detailed information about a specific contact message (Admin only)
    """
    contact = get_object_or_404(Contact, id=contact_id)
    
    # Mark as read when admin views it
    if not contact.is_read:
        contact.mark_as_read()
    
    serializer = ContactDetailSerializer(contact)
    
    return Response({
        'success': True,
        'contact': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_contact_status(request, contact_id):
    """
    Update contact message status (Admin only)
    
    Optional fields:
    - is_read: Mark as read/unread
    - is_responded: Mark as responded/not responded
    - admin_notes: Add admin notes
    """
    contact = get_object_or_404(Contact, id=contact_id)
    
    if 'is_read' in request.data:
        contact.is_read = request.data['is_read']
    
    if 'is_responded' in request.data:
        contact.is_responded = request.data['is_responded']
    
    if 'admin_notes' in request.data:
        contact.admin_notes = request.data['admin_notes']
    
    contact.save()
    serializer = ContactDetailSerializer(contact)
    
    return Response({
        'success': True,
        'message': 'Estado del contacto actualizado exitosamente',
        'contact': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_contact(request, contact_id):
    """
    Delete a contact message (Admin only)
    """
    contact = get_object_or_404(Contact, id=contact_id)
    contact_name = contact.nombre
    contact.delete()
    
    return Response({
        'success': True,
        'message': f'Mensaje de contacto de {contact_name} eliminado exitosamente'
    }, status=status.HTTP_200_OK)


