from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

from complaints.models import Complaint, ComplaintResponse, Feedback
from properties.models import Property


@login_required
def complaint_list(request):
    """List complaints for current user or all complaints for staff"""
    # Handle POST requests for actions
    if request.method == 'POST':
        action = request.POST.get('action')
        complaint_id = request.POST.get('complaint_id')
        
        if action == 'get_details':
            try:
                complaint = Complaint.objects.get(id=complaint_id)
                return JsonResponse({
                    'title': complaint.title,
                    'description': complaint.description,
                    'property': complaint.property.title if complaint.property else None,
                    'status': complaint.get_status_display(),
                    'status_value': complaint.status,  # Add status value for checking
                    'priority': complaint.get_priority_display(),
                    'category': complaint.get_category_display(),
                    'user': complaint.user.get_full_name() or complaint.user.username,
                    'created_at': complaint.created_at.strftime('%B %d, %Y at %I:%M %p')
                })
            except Complaint.DoesNotExist:
                return JsonResponse({'error': 'Complaint not found'}, status=404)
        
        elif action == 'start_work':
            try:
                complaint = Complaint.objects.get(id=complaint_id)
                # Security: Only staff can start work on complaints
                if not request.user.is_staff:
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                
                # Validation: If changing from resolved, require reason
                status_change_reason = request.POST.get('status_change_reason', '').strip()
                if complaint.status == 'resolved':
                    if not status_change_reason:
                        return JsonResponse({
                            'error': 'Reason is required when changing status from Resolved. Please provide an explanation.',
                            'requires_reason': True
                        }, status=400)
                    complaint.status_change_reason = status_change_reason
                
                complaint.status = 'in_progress'
                complaint.save()
                return JsonResponse({'success': True})
            except Complaint.DoesNotExist:
                return JsonResponse({'error': 'Complaint not found'}, status=404)
        
        elif action == 'mark_resolved':
            try:
                complaint = Complaint.objects.get(id=complaint_id)
                # Security: Only staff can mark complaints as resolved
                if not request.user.is_staff:
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                complaint.status = 'resolved'
                complaint.resolved_by = request.user
                complaint.resolved_at = timezone.now()
                complaint.save()
                return JsonResponse({'success': True})
            except Complaint.DoesNotExist:
                return JsonResponse({'error': 'Complaint not found'}, status=404)
        
        elif action == 'delete':
            try:
                complaint = Complaint.objects.get(id=complaint_id)
                # Security: Only staff or the user who created the complaint can delete
                if not (request.user.is_staff or complaint.user == request.user):
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                if complaint.status == 'resolved':
                    complaint.delete()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'error': 'Only resolved complaints can be deleted'}, status=400)
            except Complaint.DoesNotExist:
                return JsonResponse({'error': 'Complaint not found'}, status=404)
    
    if request.user.is_staff:
        complaints = Complaint.objects.select_related('user', 'property').all()
        is_staff_view = True
    else:
        complaints = Complaint.objects.filter(user=request.user).select_related('property')
        is_staff_view = False
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by priority if provided
    priority_filter = request.GET.get('priority')
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(complaints, 5)  # Show 5 complaints per page (matching maintenance)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Handle AJAX requests
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.GET.get('ajax') == 'true' or
        'application/json' in request.headers.get('Accept', '')
    )
    
    if is_ajax:
        return render(request, 'complaints/complaint_list_table.html', {
            'complaints': page_obj,
            'user': request.user,
        })
    
    # Calculate statistics based on user role
    if request.user.is_staff:
        stats_complaints = Complaint.objects.all()
    else:
        stats_complaints = Complaint.objects.filter(user=request.user)
    
    context = {
        'complaints': page_obj,
        'is_staff_view': is_staff_view,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'current_status': status_filter,
        'current_priority': priority_filter,
        'search_query': search_query,
        'properties': Property.objects.all(),
        'pending_count': stats_complaints.filter(status='pending').count(),
        'in_progress_count': stats_complaints.filter(status='in_progress').count(),
        'resolved_count': stats_complaints.filter(status='resolved').count(),
    }
    return render(request, 'complaints/complaint_list.html', context)


@login_required
def complaint_detail(request, pk):
    """View complaint details and responses"""
    if request.user.is_staff:
        complaint = get_object_or_404(Complaint, pk=pk)
    else:
        complaint = get_object_or_404(Complaint, pk=pk, user=request.user)
    
    responses = complaint.responses.all()
    if not request.user.is_staff:
        responses = responses.filter(is_visible_to_user=True)
    
    context = {
        'complaint': complaint,
        'responses': responses,
        'can_respond': request.user.is_staff,
    }
    return render(request, 'complaints/complaint_detail.html', context)


@login_required
def complaint_create(request):
    """Create a new complaint"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        priority = request.POST.get('priority', 'medium')
        property_id = request.POST.get('property')
        rating = request.POST.get('rating')
        
        if not title or not description:
            messages.error(request, 'Title and description are required.')
            return render(request, 'complaints/complaint_form.html', {
                'properties': Property.objects.all(),
                'category_choices': Complaint.CATEGORY_CHOICES,
                'priority_choices': Complaint.PRIORITY_CHOICES,
            })
        
        complaint = Complaint(
            user=request.user,
            title=title,
            description=description,
            category=category,
            priority=priority,
        )
        
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                # Security: Validate that user has access to this property
                from documents.models import Lease
                has_access = False
                if request.user.is_staff:
                    has_access = True
                elif property_obj.owner == request.user:
                    has_access = True
                else:
                    # Check if user is a tenant with active lease
                    active_leases = Lease.objects.filter(
                        tenant=request.user, 
                        property=property_obj,
                        status='active'
                    )
                    if active_leases.exists():
                        has_access = True
                
                if has_access:
                    complaint.property = property_obj
            except Property.DoesNotExist:
                pass
        
        if rating:
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    complaint.rating = rating_int
            except (ValueError, TypeError):
                pass
        
        complaint.save()
        messages.success(request, 'Complaint submitted successfully!')
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Complaint submitted successfully!',
                'complaint_id': complaint.pk
            })
        
        return redirect('complaints:complaint_detail', pk=complaint.pk)
    
    context = {
        'properties': Property.objects.all(),
        'category_choices': Complaint.CATEGORY_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
    }
    return render(request, 'complaints/complaint_form.html', context)


@staff_member_required
def complaint_update_status(request, pk):
    """Update complaint status (staff only)"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        status_change_reason = request.POST.get('status_change_reason', '').strip()
        
        # Validation: If changing from resolved status, reason is required
        if complaint.status == 'resolved' and new_status != 'resolved':
            if not status_change_reason:
                messages.error(request, 'Reason is required when changing status from Resolved. Please provide an explanation.')
                return redirect('complaints:complaint_detail', pk=complaint.pk)
        
        if new_status in dict(Complaint.STATUS_CHOICES):
            # Store the reason if changing from resolved
            if complaint.status == 'resolved' and new_status != 'resolved':
                complaint.status_change_reason = status_change_reason
            
            complaint.status = new_status
            if new_status == 'resolved':
                complaint.resolved_by = request.user
                complaint.resolved_at = timezone.now()
                # Clear reason when marking as resolved
                complaint.status_change_reason = None
            complaint.save()
            messages.success(request, f'Complaint status updated to {complaint.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected')
    
    return redirect('complaints:complaint_detail', pk=complaint.pk)


@staff_member_required
def add_complaint_response(request, pk):
    """Add response to complaint (staff only)"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        response_type = request.POST.get('response_type', 'user')
        is_visible = request.POST.get('is_visible_to_user') == 'on'
        
        if message:
            ComplaintResponse.objects.create(
                complaint=complaint,
                responder=request.user,
                response_type=response_type,
                message=message,
                is_visible_to_user=is_visible
            )
            messages.success(request, 'Response added successfully!')
        else:
            messages.error(request, 'Response message is required')
    
    return redirect('complaints:complaint_detail', pk=complaint.pk)


@login_required
def feedback_list(request):
    """List feedback for current user or all feedback for staff"""
    if request.user.is_staff:
        feedback_items = Feedback.objects.select_related('user', 'property').all()
        is_staff_view = True
    else:
        feedback_items = Feedback.objects.filter(user=request.user).select_related('property')
        is_staff_view = False
    
    # Filter by type if provided
    type_filter = request.GET.get('type')
    if type_filter:
        feedback_items = feedback_items.filter(feedback_type=type_filter)
    
    # Pagination
    paginator = Paginator(feedback_items, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'feedback_items': page_obj,
        'is_staff_view': is_staff_view,
        'type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
        'current_type': type_filter,
    }
    return render(request, 'complaints/feedback_list.html', context)


@login_required
def feedback_create(request):
    """Create new feedback"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        feedback_type = request.POST.get('feedback_type', 'general')
        property_id = request.POST.get('property')
        rating = request.POST.get('rating')
        
        if not message:
            messages.error(request, 'Message is required.')
            return render(request, 'complaints/feedback_form.html', {
                'properties': Property.objects.all(),
                'type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
            })
        
        feedback = Feedback(
            user=request.user,
            title=title,
            message=message,
            feedback_type=feedback_type,
        )
        
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                # Security: Validate that user has access to this property
                from documents.models import Lease
                has_access = False
                if request.user.is_staff:
                    has_access = True
                elif property_obj.owner == request.user:
                    has_access = True
                else:
                    # Check if user is a tenant with active lease
                    active_leases = Lease.objects.filter(
                        tenant=request.user, 
                        property=property_obj,
                        status='active'
                    )
                    if active_leases.exists():
                        has_access = True
                
                if has_access:
                    feedback.property = property_obj
            except Property.DoesNotExist:
                pass
        
        if rating:
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    feedback.rating = rating_int
            except (ValueError, TypeError):
                pass
        
        feedback.save()
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('complaints:feedback_list')
    
    context = {
        'properties': Property.objects.all(),
        'type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
    }
    return render(request, 'complaints/feedback_form.html', context)


@login_required
def feedback_form(request):
    """Display feedback form for users to submit feedback"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        feedback_type = request.POST.get('feedback_type', 'general')
        property_id = request.POST.get('property')
        rating = request.POST.get('rating')
        
        if not message:
            messages.error(request, 'Message is required.')
            return render(request, 'complaints/feedback_form.html', {
                'properties': Property.objects.all(),
                'type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
            })
        
        feedback = Feedback(
            user=request.user,
            title=title,
            message=message,
            feedback_type=feedback_type,
        )
        
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                # Security: Validate that user has access to this property
                from documents.models import Lease
                has_access = False
                if request.user.is_staff:
                    has_access = True
                elif property_obj.owner == request.user:
                    has_access = True
                else:
                    # Check if user is a tenant with active lease
                    active_leases = Lease.objects.filter(
                        tenant=request.user, 
                        property=property_obj,
                        status='active'
                    )
                    if active_leases.exists():
                        has_access = True
                
                if has_access:
                    feedback.property = property_obj
            except Property.DoesNotExist:
                pass
        
        if rating:
            try:
                rating_int = int(rating)
                if 1 <= rating_int <= 5:
                    feedback.rating = rating_int
            except (ValueError, TypeError):
                pass
        
        feedback.save()
        messages.success(request, 'Thank you for your feedback!')
        return redirect('complaints:feedback_form')
    
    context = {
        'properties': Property.objects.all(),
        'type_choices': Feedback.FEEDBACK_TYPE_CHOICES,
    }
    return render(request, 'complaints/feedback_form.html', context)


@staff_member_required
def complaint_dashboard(request):
    """Dashboard for complaint management (staff only)"""
    complaints = Complaint.objects.all()
    
    stats = {
        'total': complaints.count(),
        'pending': complaints.filter(status='pending').count(),
        'in_progress': complaints.filter(status='in_progress').count(),
        'resolved': complaints.filter(status='resolved').count(),
        'closed': complaints.filter(status='closed').count(),
    }
    
    recent_complaints = complaints.order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'complaints/dashboard.html', context)


@login_required
def test_ajax(request):
    """Test AJAX endpoint for complaints"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    print(f"TEST AJAX - Search: {search_query}, Status: {status_filter}, Priority: {priority_filter}")
    print(f"AJAX parameter: {request.GET.get('ajax')}")
    print(f"X-Requested-With header: {request.headers.get('X-Requested-With')}")
    
    if request.user.is_staff:
        complaints = Complaint.objects.select_related('user', 'property').all()
    else:
        complaints = Complaint.objects.filter(user=request.user).select_related('property')
    
    if search_query:
        complaints = complaints.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    
    print(f"Filtered count: {complaints.count()}")
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(complaints, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'complaints': page_obj,
        'user': request.user,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
    }
    
    return render(request, 'complaints/complaint_list_table.html', context)


@login_required
def complaint_delete(request, pk):
    """Delete a complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check permissions: staff can delete any complaint, users can delete their own
    if not (request.user.is_staff or complaint.user == request.user):
        messages.error(request, "You don't have permission to delete this complaint.")
        return redirect('complaints:complaint_list')
    
    if request.method == 'POST':
        complaint_title = complaint.title
        complaint.delete()
        messages.success(request, f'Complaint "{complaint_title}" has been deleted successfully.')
        return redirect('complaints:complaint_list')
    
    # If GET request, redirect to list (shouldn't happen with modal)
    return redirect('complaints:complaint_list')