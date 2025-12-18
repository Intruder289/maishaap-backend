from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from documents.models import Lease, Booking, Document
from accounts.models import Profile


@login_required
def lease_list(request):
    """Display list of leases"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.user.is_staff or request.user.is_superuser:
        # Staff/Admin: see all leases
        leases = Lease.objects.select_related('property_ref', 'tenant').all()
    else:
        # Non-staff users: see leases where they are tenant OR property owner
        from django.db.models import Q
        leases = Lease.objects.filter(
            Q(tenant=request.user) | Q(property_ref__owner=request.user)
        ).select_related('property_ref', 'tenant')
    
    context = {
        'leases': leases,
        'profile': profile,
        'active_leases_count': leases.filter(status='active').count(),
    }
    return render(request, 'documents/lease_list.html', context)


@login_required
def booking_list(request):
    """Display list of bookings"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.user.is_staff:
        bookings = Booking.objects.select_related('property_ref', 'tenant').all()
    else:
        bookings = Booking.objects.filter(tenant=request.user).select_related('property_ref')
    
    context = {
        'bookings': bookings,
        'profile': profile,
        'pending_bookings_count': bookings.filter(status='pending').count(),
    }
    return render(request, 'documents/booking_list.html', context)


@login_required
def document_list(request):
    """Display list of documents"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.user.is_staff:
        documents = Document.objects.select_related('lease', 'booking', 'property_ref', 'user').all()
    else:
        from django.db.models import Q
        documents = Document.objects.filter(
            Q(user=request.user) |
            Q(lease__tenant=request.user) |
            Q(booking__tenant=request.user)
        ).select_related('lease', 'booking', 'property_ref', 'user').distinct()
    
    context = {
        'documents': documents,
        'profile': profile,
    }
    return render(request, 'documents/document_list.html', context)


@login_required
def document_edit(request, doc_id):
    """Edit document metadata (file_name)"""
    document = get_object_or_404(Document, pk=doc_id)
    
    # Check permissions - staff can edit any, users can only edit their own
    if not request.user.is_staff:
        from django.db.models import Q
        if not (document.user == request.user or 
                (document.lease and document.lease.tenant == request.user) or
                (document.booking and document.booking.tenant == request.user)):
            messages.error(request, 'You do not have permission to edit this document.')
            return redirect('documents:document_list')
    
    if request.method == 'POST':
        file_name = request.POST.get('file_name', '').strip()
        if file_name:
            document.file_name = file_name
            document.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('documents:document_list')
        else:
            messages.error(request, 'File name is required.')
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    context = {
        'document': document,
        'profile': profile,
    }
    return render(request, 'documents/document_edit.html', context)


@login_required
def document_delete(request, doc_id):
    """Delete a document"""
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('documents:document_list')
    
    document = get_object_or_404(Document, pk=doc_id)
    
    # Check permissions - staff can delete any, users can only delete their own
    if not request.user.is_staff:
        from django.db.models import Q
        if not (document.user == request.user or 
                (document.lease and document.lease.tenant == request.user) or
                (document.booking and document.booking.tenant == request.user)):
            messages.error(request, 'You do not have permission to delete this document.')
            return redirect('documents:document_list')
    
    try:
        file_name = document.file_name or 'Document'
        # Delete the file from storage
        if document.file:
            document.file.delete(save=False)
        document.delete()
        messages.success(request, f'Document "{file_name}" deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting document: {str(e)}')
    
    return redirect('documents:document_list')