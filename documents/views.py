from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from documents.models import Lease, Booking, Document
from accounts.models import Profile
from django.utils import timezone
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal


@login_required
def lease_list(request):
    """Display list of leases"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.user.is_staff or request.user.is_superuser:
        # Staff/Admin: see all leases
        leases = Lease.objects.select_related('property_ref', 'tenant').all()
    else:
        # Non-staff users: see leases where they are tenant OR property owner
        leases = Lease.objects.filter(
            Q(tenant=request.user) | Q(property_ref__owner=request.user)
        ).select_related('property_ref', 'tenant')
    
    # Calculate statistics
    total_leases = leases.count()
    active_leases_count = leases.filter(status='active').count()
    
    # Month-over-month calculations
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    
    # Current month leases
    current_month_leases = leases.filter(created_at__gte=current_month_start).count()
    # Previous month leases
    previous_month_leases = leases.filter(
        created_at__gte=previous_month_start,
        created_at__lt=current_month_start
    ).count()
    
    # Calculate percentage change for total leases
    if previous_month_leases > 0:
        total_leases_change = ((current_month_leases - previous_month_leases) / previous_month_leases) * 100
    elif current_month_leases > 0:
        total_leases_change = 100.0  # 100% increase from 0
    else:
        total_leases_change = 0.0
    
    # Current month active leases
    current_month_active = leases.filter(
        status='active',
        created_at__gte=current_month_start
    ).count()
    # Previous month active leases
    previous_month_active = leases.filter(
        status='active',
        created_at__gte=previous_month_start,
        created_at__lt=current_month_start
    ).count()
    
    # Calculate percentage change for active leases
    if previous_month_active > 0:
        active_leases_change = ((current_month_active - previous_month_active) / previous_month_active) * 100
    elif current_month_active > 0:
        active_leases_change = 100.0
    else:
        active_leases_change = 0.0
    
    # Calculate expiring leases (expiring in next 30 days)
    today = now.date()
    expiring_date = today + timedelta(days=30)
    expiring_leases_count = leases.filter(
        status='active',
        end_date__gte=today,
        end_date__lte=expiring_date
    ).count()
    
    # Calculate monthly revenue from lease-related payments
    from payments.models import Payment
    current_month_revenue = Payment.objects.filter(
        lease__isnull=False,
        status='completed',
        created_at__gte=current_month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    previous_month_revenue = Payment.objects.filter(
        lease__isnull=False,
        status='completed',
        created_at__gte=previous_month_start,
        created_at__lt=current_month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate percentage change for revenue
    if previous_month_revenue > 0:
        revenue_change = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
    elif current_month_revenue > 0:
        revenue_change = 100.0
    else:
        revenue_change = 0.0
    
    # Format revenue for display
    if current_month_revenue >= 1000000:
        revenue_display = f"TZS {current_month_revenue / 1000000:.1f}M"
    elif current_month_revenue >= 1000:
        revenue_display = f"TZS {current_month_revenue / 1000:.1f}K"
    else:
        revenue_display = f"TZS {current_month_revenue:.0f}"
    
    context = {
        'leases': leases,
        'profile': profile,
        'active_leases_count': active_leases_count,
        'total_leases_change': round(total_leases_change, 1),
        'active_leases_change': round(active_leases_change, 1),
        'expiring_leases_count': expiring_leases_count,
        'monthly_revenue': current_month_revenue,
        'monthly_revenue_display': revenue_display,
        'revenue_change': round(revenue_change, 1),
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