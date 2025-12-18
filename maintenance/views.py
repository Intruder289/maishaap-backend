from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import MaintenanceRequest


@login_required
def request_list(request):
    """List all maintenance requests with AJAX support"""
    # Handle POST requests for actions
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        
        if action == 'get_details':
            try:
                maintenance_request = MaintenanceRequest.objects.get(id=request_id)
                
                # Format status and priority with badge classes
                status_badges = {
                    'pending': 'badge bg-warning',
                    'in_progress': 'badge bg-primary',
                    'completed': 'badge bg-success',
                    'cancelled': 'badge bg-secondary'
                }
                
                priority_badges = {
                    'urgent': 'badge bg-danger',
                    'high': 'badge bg-warning text-dark',
                    'medium': 'badge bg-info',
                    'low': 'badge bg-success'
                }
                
                status_class = status_badges.get(maintenance_request.status, 'badge bg-secondary')
                priority_class = priority_badges.get(maintenance_request.priority, 'badge bg-secondary')
                
                return JsonResponse({
                    'title': maintenance_request.title,
                    'description': maintenance_request.description,
                    'property': maintenance_request.property.title,
                    'status': f'<span class="{status_class}">{maintenance_request.get_status_display()}</span>',
                    'priority': f'<span class="{priority_class}">{maintenance_request.get_priority_display()}</span>',
                    'category': maintenance_request.get_category_display() if hasattr(maintenance_request, 'get_category_display') else 'N/A',
                    'location_details': maintenance_request.location_details if hasattr(maintenance_request, 'location_details') else None,
                    'created_at': maintenance_request.created_at.strftime('%B %d, %Y at %I:%M %p')
                })
            except MaintenanceRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
        
        elif action == 'start_work':
            try:
                maintenance_request = MaintenanceRequest.objects.get(id=request_id)
                # Security: Only staff or the tenant who created the request can start work
                if not (request.user.is_staff or maintenance_request.tenant == request.user):
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                maintenance_request.status = 'in_progress'
                maintenance_request.assigned_to = request.user
                if request.POST.get('notes'):
                    maintenance_request.admin_notes = request.POST.get('notes')
                maintenance_request.save()
                return JsonResponse({'success': True})
            except MaintenanceRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
        
        elif action == 'mark_complete':
            try:
                maintenance_request = MaintenanceRequest.objects.get(id=request_id)
                # Security: Only staff or assigned user can mark as complete
                if not (request.user.is_staff or maintenance_request.assigned_to == request.user):
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                maintenance_request.status = 'completed'
                if not maintenance_request.assigned_to:
                    maintenance_request.assigned_to = request.user
                if request.POST.get('actual_cost'):
                    try:
                        maintenance_request.actual_cost = float(request.POST.get('actual_cost'))
                    except (ValueError, TypeError):
                        return JsonResponse({'error': 'Invalid cost value'}, status=400)
                if request.POST.get('notes'):
                    maintenance_request.admin_notes = request.POST.get('notes')
                maintenance_request.save()
                return JsonResponse({'success': True})
            except MaintenanceRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
        
        elif action == 'delete':
            try:
                maintenance_request = MaintenanceRequest.objects.get(id=request_id)
                # Security: Only staff or the tenant who created the request can delete
                if not (request.user.is_staff or maintenance_request.tenant == request.user):
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                if maintenance_request.status == 'completed':
                    maintenance_request.delete()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'error': 'Only completed requests can be deleted'}, status=400)
            except MaintenanceRequest.DoesNotExist:
                return JsonResponse({'error': 'Request not found'}, status=404)
    
    requests = MaintenanceRequest.objects.select_related(
        'property', 'tenant', 'assigned_to'
    ).order_by('-created_at')

    # Apply filters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')

    if status_filter:
        requests = requests.filter(status=status_filter)
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    if category_filter:
        requests = requests.filter(category=category_filter)
    if search_query:
        requests = requests.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Calculate statistics
    total_requests = requests.count()
    pending_count = requests.filter(status='pending').count()
    in_progress_count = requests.filter(status='in_progress').count()
    completed_count = requests.filter(status='completed').count()
    
    # Pagination with fixed page size
    page_size = 5  # Fixed page size for better UX
    paginator = Paginator(requests, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Filter options for the template
    filter_options = {
        'statuses': MaintenanceRequest.STATUS_CHOICES,
        'priorities': MaintenanceRequest.PRIORITY_CHOICES,
        'categories': [],  # Add categories if needed
    }
    
    # Current filter values
    current_filters = {
        'status': status_filter,
        'priority': priority_filter,
        'category': category_filter,
        'search': search_query,
    }
    
    # Get user's properties for the modal
    from properties.models import Property
    from documents.models import Lease
    
    if request.user.is_staff:
        # Staff can see all properties
        user_properties = Property.objects.all()
    else:
        # Check if user has active leases (for tenants)
        active_leases = Lease.objects.filter(tenant=request.user, status='active')
        if active_leases.exists():
            # User is a tenant with active leases
            user_properties = Property.objects.filter(
                leases__tenant=request.user, 
                leases__status='active'
            ).distinct()
        else:
            # User is a property owner
            user_properties = Property.objects.filter(owner=request.user)
    
    context = {
        'page_obj': page_obj,
        'requests': requests,  # For template statistics
        'total_requests': total_requests,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'filter_options': filter_options,
        'current_filters': current_filters,
        'user_properties': user_properties,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
    }
    
    # Handle AJAX requests - check multiple ways
    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.GET.get('ajax') == 'true' or
        'application/json' in request.headers.get('Accept', '')
    )
    
    if is_ajax:
        print(f"AJAX Request - Search: {search_query}, Status: {status_filter}, Priority: {priority_filter}")
        print(f"Filtered requests count: {requests.count()}")
        print(f"Page object count: {page_obj.object_list.count()}")
        print(f"Returning table template for AJAX")
        return render(request, 'maintenance/request_list_table.html', context)
    
    # Debug: Check if ajax parameter is present
    if request.GET.get('ajax') == 'true':
        print(f"DEBUG: ajax=true parameter detected")
        print(f"AJAX Request - Search: {search_query}, Status: {status_filter}, Priority: {priority_filter}")
        print(f"Filtered requests count: {requests.count()}")
        return render(request, 'maintenance/request_list_table.html', context)
    
    return render(request, 'maintenance/request_list.html', context)


@login_required
def test_ajax(request):
    """Test AJAX endpoint"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    print(f"TEST AJAX - Search: {search_query}, Status: {status_filter}, Priority: {priority_filter}")
    print(f"AJAX parameter: {request.GET.get('ajax')}")
    print(f"X-Requested-With header: {request.headers.get('X-Requested-With')}")
    
    requests = MaintenanceRequest.objects.all().order_by('-created_at')
    
    if search_query:
        requests = requests.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    if status_filter:
        requests = requests.filter(status=status_filter)
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    
    print(f"Filtered count: {requests.count()}")
    
    context = {
        'requests': requests,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(requests, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'requests': requests,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
    }
    
    return render(request, 'maintenance/request_list_table.html', context)


@login_required
def request_detail(request, pk):
    """View maintenance request details"""
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
    
    # Security: Only staff, the tenant who created it, or property owner can view
    if not (request.user.is_staff or 
            maintenance_request.tenant == request.user or 
            (hasattr(maintenance_request, 'property') and 
             maintenance_request.property and 
             maintenance_request.property.owner == request.user)):
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('maintenance:request_list')
    
    context = {
        'maintenance_request': maintenance_request,
    }
    return render(request, 'maintenance/request_detail.html', context)


@login_required
def request_create(request):
    """Create new maintenance request"""
    if request.method == 'POST':
        # Simple form processing
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        property_id = request.POST.get('property')
        priority = request.POST.get('priority', 'medium')
        
        if not title or not description or not property_id:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('maintenance:request_form')
        
        # Security: Validate that user has access to this property
        from properties.models import Property
        from documents.models import Lease
        
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            messages.error(request, 'Invalid property selected.')
            return redirect('maintenance:request_form')
        
        # Check if user has access to this property
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
        
        if not has_access:
            messages.error(request, 'You do not have access to this property.')
            return redirect('maintenance:request_form')
        
        # Validate priority
        valid_priorities = [choice[0] for choice in MaintenanceRequest.PRIORITY_CHOICES]
        if priority not in valid_priorities:
            priority = 'medium'
        
        MaintenanceRequest.objects.create(
            title=title,
            description=description,
            property=property_obj,
            tenant=request.user,
            priority=priority
        )
        messages.success(request, 'Maintenance request created successfully!')
        return redirect('maintenance:request_list')
    
    return render(request, 'maintenance/request_form.html')


@login_required
def request_form(request):
    """Display maintenance request form"""
    from properties.models import Property
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        property_id = request.POST.get('property')
        priority = request.POST.get('priority', 'medium')
        
        if title and description and property_id:
            # Security: Validate that user has access to this property
            from properties.models import Property
            from documents.models import Lease
            
            try:
                property_obj = Property.objects.get(id=property_id)
            except Property.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'Invalid property selected.'}, status=400)
                messages.error(request, 'Invalid property selected.')
                return redirect('maintenance:request_form')
            
            # Check if user has access to this property
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
            
            if not has_access:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': 'You do not have access to this property.'}, status=403)
                messages.error(request, 'You do not have access to this property.')
                return redirect('maintenance:request_form')
            
            # Validate priority
            valid_priorities = [choice[0] for choice in MaintenanceRequest.PRIORITY_CHOICES]
            if priority not in valid_priorities:
                priority = 'medium'
            
            try:
                MaintenanceRequest.objects.create(
                    title=title,
                    description=description,
                    property=property_obj,
                    tenant=request.user,
                    priority=priority
                )
                
                # Handle AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Maintenance request submitted successfully!'})
                
                messages.success(request, 'Maintenance request submitted successfully!')
                return redirect('maintenance:request_list')
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': f'Error creating request: {str(e)}'}, status=400)
                messages.error(request, f'Error creating request: {str(e)}')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Please fill in all required fields.'}, status=400)
            messages.error(request, 'Please fill in all required fields.')
    
    # Get user's properties for the form
    from properties.models import Property
    from documents.models import Lease
    
    if request.user.is_staff:
        # Staff can see all properties
        user_properties = Property.objects.all()
    else:
        # Check if user has active leases (for tenants)
        active_leases = Lease.objects.filter(tenant=request.user, status='active')
        if active_leases.exists():
            # User is a tenant with active leases
            user_properties = Property.objects.filter(
                leases__tenant=request.user, 
                leases__status='active'
            ).distinct()
        else:
            # User is a property owner
            user_properties = Property.objects.filter(owner=request.user)
    
    context = {
        'user_properties': user_properties,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
    }
    
    return render(request, 'maintenance/request_form.html', context)