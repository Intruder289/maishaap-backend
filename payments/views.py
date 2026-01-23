from django.shortcuts import render
from . import models
from django.db.models import Sum, Count


def payment_dashboard(request):
    """Payment dashboard with comprehensive analytics and payment records table"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    # Get basic counts
    total_payments = models.Payment.objects.count()
    total_invoices = models.Invoice.objects.count()
    
    # Payment statistics - count 'completed' as successful
    successful_payments = models.Payment.objects.filter(
        status='completed'
    ).count()
    pending_payments = models.Payment.objects.filter(status='pending').count()
    failed_payments = models.Payment.objects.filter(status='failed').count()
    
    # Invoice statistics
    paid_invoices = models.Invoice.objects.filter(status='paid').count()
    unpaid_invoices = models.Invoice.objects.filter(status='unpaid').count()
    cancelled_invoices = models.Invoice.objects.filter(status='cancelled').count()
    
    # Revenue calculations - include 'completed' payments
    total_revenue = models.Payment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    outstanding_amount = models.Invoice.objects.filter(status='unpaid').aggregate(
        total=Sum('amount'))['total'] or 0
    
    # Calculate overdue payments (invoices past due date)
    today = datetime.now().date()
    overdue_invoices = models.Invoice.objects.filter(
        status='unpaid', 
        due_date__lt=today
    ).count()
    
    # Calculate payment success rate
    payment_rate = 0
    if total_payments > 0:
        payment_rate = round((successful_payments / total_payments) * 100, 1)
    
    # Get all payment records for the table with related data
    payment_records = models.Payment.objects.select_related(
        'tenant', 'provider', 'invoice', 'rent_invoice', 'booking', 'lease',
        'booking__property_obj', 'rent_invoice__lease__property_ref'
    ).prefetch_related('invoice__tenant').order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if status_filter:
        payment_records = payment_records.filter(status=status_filter)
    
    if search_query:
        payment_records = payment_records.filter(
            Q(tenant__username__icontains=search_query) |
            Q(tenant__first_name__icontains=search_query) |
            Q(tenant__last_name__icontains=search_query) |
            Q(transaction_ref__icontains=search_query)
        )
    
    # Pagination for Payment Records Table - with page_size support
    page_size = request.GET.get('page_size', '5')
    try:
        page_size = int(page_size)
        if page_size not in [5, 10, 25, 50, 100]:
            page_size = 5
    except (ValueError, TypeError):
        page_size = 5
    
    paginator = Paginator(payment_records, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Recent payments with pagination
    recent_payments_query = models.Payment.objects.select_related(
        'tenant', 'provider').order_by('-created_at')
    recent_payments_search = request.GET.get('recent_payments_search', '')
    if recent_payments_search:
        recent_payments_query = recent_payments_query.filter(
            Q(tenant__username__icontains=recent_payments_search) |
            Q(tenant__first_name__icontains=recent_payments_search) |
            Q(tenant__last_name__icontains=recent_payments_search) |
            Q(transaction_ref__icontains=recent_payments_search)
        )
    recent_payments_paginator = Paginator(recent_payments_query, page_size)
    recent_payments_page = request.GET.get('recent_payments_page', 1)
    recent_payments_page_obj = recent_payments_paginator.get_page(recent_payments_page)
    
    # Recent invoices (keep as is for now, just 5 items)
    recent_invoices = models.Invoice.objects.select_related(
        'tenant').order_by('-created_at')[:5]
    
    # Get all invoices for the table with search and pagination
    all_invoices = models.Invoice.objects.select_related('tenant').order_by('-created_at')
    invoice_search_query = request.GET.get('invoice_search', '')
    invoice_status_filter = request.GET.get('invoice_status', '')
    
    if invoice_search_query:
        all_invoices = all_invoices.filter(
            Q(tenant__username__icontains=invoice_search_query) |
            Q(tenant__first_name__icontains=invoice_search_query) |
            Q(tenant__last_name__icontains=invoice_search_query) |
            Q(id__icontains=invoice_search_query)
        )
    
    if invoice_status_filter:
        all_invoices = all_invoices.filter(status=invoice_status_filter)
    
    # Pagination for Invoice Records Table - with page_size support
    invoice_page_size = request.GET.get('invoice_page_size', '5')
    try:
        invoice_page_size = int(invoice_page_size)
        if invoice_page_size not in [5, 10, 25, 50, 100]:
            invoice_page_size = 5
    except (ValueError, TypeError):
        invoice_page_size = 5
    
    invoice_paginator = Paginator(all_invoices, invoice_page_size)
    invoice_page = request.GET.get('invoice_page', 1)
    invoice_page_obj = invoice_paginator.get_page(invoice_page)
    
    context = {
        'total_payments': total_payments,
        'total_invoices': total_invoices,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'cancelled_invoices': cancelled_invoices,
        'total_revenue': total_revenue,
        'outstanding_amount': outstanding_amount,
        'overdue_payments': overdue_invoices,
        'payment_rate': payment_rate,
        'recent_payments': recent_payments_page_obj,
        'recent_invoices': recent_invoices,
        'page_obj': page_obj,
        'paginator': paginator,
        'payment_records': payment_records,
        'invoice_page_obj': invoice_page_obj,
        'invoice_paginator': invoice_paginator,
        'all_invoices': all_invoices,
        'status_choices': models.Payment.STATUS_CHOICES,
        'invoice_status_choices': models.Invoice.STATUS_CHOICES,
        'status_filter': status_filter,
        'search_query': search_query,
        'recent_payments_search': recent_payments_search,
        'invoice_search_query': invoice_search_query,
        'invoice_status_filter': invoice_status_filter,
        'current_page_size': page_size,
        'invoice_current_page_size': invoice_page_size,
        'today': today,
    }
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        table_type = request.GET.get('table_type', 'payments')
        if table_type == 'recent_payments':
            return render(request, 'payments/recent_payments_table.html', context)
        elif table_type == 'invoices':
            return render(request, 'payments/invoice_dashboard_table.html', context)
        else:
            return render(request, 'payments/payment_dashboard_table.html', context)
    
    return render(request, 'payments/payment_dashboard.html', context)


def invoice_list(request):
    from django.core.paginator import Paginator
    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get all invoices
    invoices = models.Invoice.objects.select_related('tenant').all().order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    if search_query:
        invoices = invoices.filter(
            Q(tenant__username__icontains=search_query) |
            Q(tenant__first_name__icontains=search_query) |
            Q(tenant__last_name__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    # Pagination - with page_size support (default 5)
    page_size = request.GET.get('page_size', '5')
    try:
        page_size = int(page_size)
        if page_size not in [5, 10, 25, 50, 100]:
            page_size = 5
    except (ValueError, TypeError):
        page_size = 5
    
    paginator = Paginator(invoices, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics (from all invoices, not filtered)
    all_invoices = models.Invoice.objects.all()
    total_invoices = all_invoices.count()
    paid_invoices = all_invoices.filter(status='paid').count()
    unpaid_invoices = all_invoices.filter(status='unpaid').count()
    cancelled_invoices = all_invoices.filter(status='cancelled').count()
    
    # Calculate outstanding amount
    outstanding_amount = all_invoices.filter(status='unpaid').aggregate(
        total=Sum('amount'))['total'] or 0
    
    # Month-over-month calculations for invoices
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    
    # Current month invoices
    current_month_invoices = all_invoices.filter(created_at__gte=current_month_start).count()
    # Previous month invoices
    previous_month_invoices = all_invoices.filter(
        created_at__gte=previous_month_start,
        created_at__lt=current_month_start
    ).count()
    
    # Calculate percentage change for total invoices
    if previous_month_invoices > 0:
        invoices_change_percent = ((current_month_invoices - previous_month_invoices) / previous_month_invoices) * 100
    elif current_month_invoices > 0:
        invoices_change_percent = 100.0
    else:
        invoices_change_percent = 0.0
    
    # Calculate payment rate (paid invoices / total invoices * 100)
    if total_invoices > 0:
        payment_rate = (paid_invoices / total_invoices) * 100
    else:
        payment_rate = 0.0
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'invoices': invoices,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'cancelled_invoices': cancelled_invoices,
        'outstanding_amount': outstanding_amount,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': models.Invoice.STATUS_CHOICES,
        'invoices_change_percent': round(invoices_change_percent, 1),
        'payment_rate': round(payment_rate, 1),
        'current_page_size': page_size,
    }
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'payments/invoice_list_table.html', context)
    
    return render(request, 'payments/invoice_list.html', context)


def invoice_detail(request, invoice_id):
    """Display invoice details"""
    from django.shortcuts import get_object_or_404
    
    invoice = get_object_or_404(
        models.Invoice.objects.select_related('tenant').prefetch_related('payments'),
        id=invoice_id
    )
    
    # Check permissions - tenants can only see their own invoices
    if not request.user.is_staff and invoice.tenant != request.user:
        from django.contrib import messages
        messages.error(request, 'You do not have permission to view this invoice.')
        from django.shortcuts import redirect
        return redirect('payments:invoice_list')
    
    # Get related payments
    payments = invoice.payments.all().order_by('-created_at')
    
    context = {
        'invoice': invoice,
        'payments': payments,
    }
    
    return render(request, 'payments/invoice_detail.html', context)


def invoice_edit(request, invoice_id):
    """Edit an invoice"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit invoices.')
        return redirect('payments:invoice_list')
    
    invoice = get_object_or_404(models.Invoice, id=invoice_id)
    
    if request.method == 'POST':
        # Update invoice fields
        invoice.amount = request.POST.get('amount', invoice.amount)
        invoice.due_date = request.POST.get('due_date', invoice.due_date)
        invoice.status = request.POST.get('status', invoice.status)
        
        try:
            invoice.amount = float(request.POST.get('amount', invoice.amount))
            from datetime import datetime
            invoice.due_date = datetime.strptime(request.POST.get('due_date'), '%Y-%m-%d').date()
            invoice.save()
            messages.success(request, f'Invoice #{invoice.id} updated successfully.')
            return redirect('payments:invoice_detail', invoice_id=invoice.id)
        except (ValueError, TypeError) as e:
            messages.error(request, f'Error updating invoice: {str(e)}')
    
    context = {
        'invoice': invoice,
        'status_choices': models.Invoice.STATUS_CHOICES,
    }
    
    return render(request, 'payments/invoice_edit.html', context)


def invoice_delete(request, invoice_id):
    """Delete an invoice"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    from django.http import JsonResponse
    
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete invoices.'}, status=403)
        messages.error(request, 'You do not have permission to delete invoices.')
        return redirect('payments:invoice_list')
    
    invoice = get_object_or_404(models.Invoice, id=invoice_id)
    
    if request.method == 'POST':
        invoice_id_str = str(invoice.id)
        invoice.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Invoice #{invoice_id_str} deleted successfully.'
            })
        
        messages.success(request, f'Invoice #{invoice_id_str} deleted successfully.')
        return redirect('payments:invoice_list')
    
    # GET request - show confirmation
    context = {
        'invoice': invoice,
    }
    
    return render(request, 'payments/invoice_delete_confirm.html', context)


def payment_list(request):
    """Payment list with AJAX support and filtering - uses unified Payment model only"""
    from django.core.paginator import Paginator
    from django.db.models import Q, Sum
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Use ONLY the unified Payment model - this handles all payment types
    # (rent payments, booking payments, invoice payments, etc.)
    # Filter out invalid payments: must have tenant and valid amount
    payments = models.Payment.objects.select_related(
        'tenant', 
        'provider', 
        'invoice',
        'rent_invoice',
        'booking',
        'lease',
        'booking__property_obj',
        'rent_invoice__lease__property_ref'
    ).prefetch_related(
        'booking__property_obj__property_type',
        'rent_invoice__lease__property_ref__property_type'
    ).filter(
        tenant__isnull=False,  # Must have a tenant
        amount__gt=0  # Must have a positive amount
    ).order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    method_filter = request.GET.get('method')
    search_query = request.GET.get('search')
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    if search_query:
        payments = payments.filter(
            Q(tenant__username__icontains=search_query) |
            Q(tenant__first_name__icontains=search_query) |
            Q(tenant__last_name__icontains=search_query) |
            Q(transaction_ref__icontains=search_query) |
            Q(reference_number__icontains=search_query) |
            Q(booking__booking_reference__icontains=search_query) |
            Q(rent_invoice__invoice_number__icontains=search_query) |
            Q(booking__property_obj__title__icontains=search_query) |
            Q(rent_invoice__lease__property_ref__title__icontains=search_query)
        )
    
    # Pagination - with page_size support (default 5)
    page_size = request.GET.get('page_size', '5')
    try:
        page_size = int(page_size)
        if page_size not in [5, 10, 25, 50, 100]:
            page_size = 5
    except (ValueError, TypeError):
        page_size = 5
    
    paginator = Paginator(payments, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics from ALL valid payments (not filtered by search/filters)
    # Only count payments with tenant and positive amount
    all_payments = models.Payment.objects.filter(
        tenant__isnull=False,
        amount__gt=0
    )
    total_payments = all_payments.count()
    
    # Count successful payments (use 'completed' status)
    successful_payments = all_payments.filter(
        status='completed'
    ).count()
    pending_payments = all_payments.filter(status='pending').count()
    failed_payments = all_payments.filter(status='failed').count()
    
    # Calculate total revenue from completed payments
    total_revenue = all_payments.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate percentage changes (current month vs previous month)
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Previous month dates
    if current_month_start.month == 1:
        previous_month_start = datetime(current_month_start.year - 1, 12, 1, tzinfo=timezone.get_current_timezone())
        # Last day of December
        previous_month_end = datetime(current_month_start.year - 1, 12, 31, 23, 59, 59, tzinfo=timezone.get_current_timezone())
    else:
        previous_month_start = datetime(current_month_start.year, current_month_start.month - 1, 1, tzinfo=timezone.get_current_timezone())
        # Last day of previous month
        if current_month_start.month == 2:
            previous_month_end = datetime(current_month_start.year, current_month_start.month - 1, 28, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        elif current_month_start.month in [4, 6, 9, 11]:
            previous_month_end = datetime(current_month_start.year, current_month_start.month - 1, 30, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        else:
            previous_month_end = datetime(current_month_start.year, current_month_start.month - 1, 31, 23, 59, 59, tzinfo=timezone.get_current_timezone())
    
    # Current month statistics
    current_month_payments = all_payments.filter(
        created_at__gte=current_month_start
    )
    current_month_count = current_month_payments.count()
    current_month_revenue = current_month_payments.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Previous month statistics
    previous_month_payments = all_payments.filter(
        created_at__gte=previous_month_start,
        created_at__lte=previous_month_end
    )
    previous_month_count = previous_month_payments.count()
    previous_month_revenue = previous_month_payments.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate percentage changes
    payments_change_percent = 0
    if previous_month_count > 0:
        payments_change_percent = round(((current_month_count - previous_month_count) / previous_month_count) * 100, 1)
    elif current_month_count > 0:
        payments_change_percent = 100.0  # 100% increase if no previous data
    
    revenue_change_percent = 0
    if previous_month_revenue > 0:
        revenue_change_percent = round(((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100, 1)
    elif current_month_revenue > 0:
        revenue_change_percent = 100.0  # 100% increase if no previous data
    
    # Use unified Payment model status choices
    status_choices = models.Payment.STATUS_CHOICES
    method_choices = models.Payment.PAYMENT_METHOD_CHOICES
    
    # Calculate success rate
    success_rate = 0
    if total_payments > 0:
        success_rate = round((successful_payments / total_payments) * 100, 1)
    
    # Determine status text based on success rate
    if success_rate >= 90:
        success_status = 'Excellent'
    elif success_rate >= 70:
        success_status = 'Good'
    elif success_rate >= 50:
        success_status = 'Fair'
    else:
        success_status = 'Poor'
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'payments': payments,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'total_revenue': total_revenue,
        'success_rate': success_rate,
        'success_status': success_status,
        'payments_change_percent': payments_change_percent,
        'revenue_change_percent': revenue_change_percent,
        'status_choices': status_choices,
        'method_choices': method_choices,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'search_query': search_query,
        'current_page_size': page_size,
        'use_rent_payments': False,  # Always False - using unified model
    }
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'payments/payment_list_table.html', context)
    
    return render(request, 'payments/payment_list.html', context)


def payment_methods(request):
    """Payment methods management page"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Get payment providers with filters and pagination
    providers = models.PaymentProvider.objects.all().order_by('-created_at')
    
    # Apply filters for providers
    provider_search = request.GET.get('provider_search')
    provider_status = request.GET.get('provider_status')
    
    if provider_search:
        providers = providers.filter(
            Q(name__icontains=provider_search) |
            Q(description__icontains=provider_search)
        )
    
    if provider_status:
        if provider_status == 'active':
            providers = providers.filter(is_active=True)
        elif provider_status == 'inactive':
            providers = providers.filter(is_active=False)
    
    # Pagination for providers - with page_size support (default 5)
    provider_page_size = request.GET.get('provider_page_size', '5')
    try:
        provider_page_size = int(provider_page_size)
        if provider_page_size not in [5, 10, 25, 50, 100]:
            provider_page_size = 5
    except (ValueError, TypeError):
        provider_page_size = 5
    
    provider_paginator = Paginator(providers, provider_page_size)
    provider_page = request.GET.get('provider_page', 1)
    provider_page_obj = provider_paginator.get_page(provider_page)
    
    # Get payment method statistics (from all providers, not filtered)
    all_providers = models.PaymentProvider.objects.all()
    total_providers = all_providers.count()
    active_providers = all_providers.filter(is_active=True).count()
    inactive_providers = all_providers.filter(is_active=False).count()
    
    # Get transactions with pagination
    transactions = models.PaymentTransaction.objects.select_related(
        'provider', 'payment__tenant'
    ).order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    provider_filter = request.GET.get('provider')
    search_query = request.GET.get('search')
    
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    if provider_filter:
        transactions = transactions.filter(provider_id=provider_filter)
    
    if search_query:
        transactions = transactions.filter(
            Q(payment__tenant__username__icontains=search_query) |
            Q(gateway_transaction_id__icontains=search_query) |
            Q(azam_reference__icontains=search_query)
        )
    
    # Pagination for transactions - with page_size support (default 5)
    transaction_page_size = request.GET.get('transaction_page_size', '5')
    try:
        transaction_page_size = int(transaction_page_size)
        if transaction_page_size not in [5, 10, 25, 50, 100]:
            transaction_page_size = 5
    except (ValueError, TypeError):
        transaction_page_size = 5
    
    transaction_paginator = Paginator(transactions, transaction_page_size)
    transaction_page = request.GET.get('page', 1)
    transaction_page_obj = transaction_paginator.get_page(transaction_page)
    
    # Calculate total transactions and revenue by provider
    provider_stats = []
    for provider in all_providers:
        provider_transactions = models.PaymentTransaction.objects.filter(provider=provider)
        transaction_count = provider_transactions.count()
        successful_transactions = provider_transactions.filter(status='successful').count()
        provider_stats.append({
            'provider': provider,
            'transaction_count': transaction_count,
            'successful_count': successful_transactions,
        })
    
    # Calculate overall success rate from all transactions
    all_transactions = models.PaymentTransaction.objects.all()
    total_transactions = all_transactions.count()
    successful_transactions = all_transactions.filter(status='successful').count()
    
    success_rate = 0.0
    if total_transactions > 0:
        success_rate = (successful_transactions / total_transactions) * 100
    
    # Determine status text based on success rate
    if success_rate >= 90:
        success_status = 'Excellent'
    elif success_rate >= 70:
        success_status = 'Good'
    elif success_rate >= 50:
        success_status = 'Fair'
    else:
        success_status = 'Poor'
    
    context = {
        'provider_page_obj': provider_page_obj,
        'provider_paginator': provider_paginator,
        'providers': providers,
        'total_providers': total_providers,
        'active_providers': active_providers,
        'inactive_providers': inactive_providers,
        'page_obj': transaction_page_obj,
        'paginator': transaction_paginator,
        'recent_transactions': transactions[:10],  # For backward compatibility
        'provider_stats': provider_stats,
        'status_filter': status_filter,
        'provider_filter': provider_filter,
        'search_query': search_query,
        'provider_search': provider_search,
        'provider_status': provider_status,
        'provider_current_page_size': provider_page_size,
        'transaction_current_page_size': transaction_page_size,
        'status_choices': [
            ('initiated', 'Initiated'),
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('successful', 'Successful'),
            ('failed', 'Failed'),
        ],
        'provider_type_choices': models.PaymentProvider.PROVIDER_TYPE_CHOICES,
        'success_rate': round(success_rate, 1),
        'success_status': success_status,
    }
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        table_type = request.GET.get('table')
        if table_type == 'transactions':
            return render(request, 'payments/payment_methods_transactions_table.html', context)
        elif table_type == 'providers':
            return render(request, 'payments/payment_methods_providers_table.html', context)
    
    return render(request, 'payments/payment_methods.html', context)


def payment_transactions(request):
    """View all payment transactions with detailed information"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Get all payment transactions with related data
    transactions = models.PaymentTransaction.objects.select_related(
        'payment__tenant', 'provider', 'payment'
    ).order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    provider_filter = request.GET.get('provider')
    search_query = request.GET.get('search')
    
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    if provider_filter:
        transactions = transactions.filter(provider_id=provider_filter)
    
    if search_query:
        transactions = transactions.filter(
            Q(payment__tenant__username__icontains=search_query) |
            Q(payment__tenant__first_name__icontains=search_query) |
            Q(payment__tenant__last_name__icontains=search_query) |
            Q(gateway_transaction_id__icontains=search_query) |
            Q(azam_reference__icontains=search_query) |
            Q(payment__transaction_ref__icontains=search_query)
        )
    
    # Pagination - with page_size support (default 5)
    page_size = request.GET.get('page_size', '5')
    try:
        page_size = int(page_size)
        if page_size not in [5, 10, 25, 50, 100]:
            page_size = 5
    except (ValueError, TypeError):
        page_size = 5
    
    paginator = Paginator(transactions, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    total_transactions = transactions.count()
    successful_transactions = transactions.filter(status='successful').count()
    pending_transactions = transactions.filter(status='pending').count()
    failed_transactions = transactions.filter(status='failed').count()
    initiated_transactions = transactions.filter(status='initiated').count()
    
    # Get all providers for filter dropdown
    providers = models.PaymentProvider.objects.all()
    
    # Status choices
    status_choices = [
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    context = {
        'page_obj': page_obj,
        'paginator': paginator,
        'transactions': transactions,
        'total_transactions': total_transactions,
        'successful_transactions': successful_transactions,
        'pending_transactions': pending_transactions,
        'failed_transactions': failed_transactions,
        'initiated_transactions': initiated_transactions,
        'providers': providers,
        'status_choices': status_choices,
        'status_filter': status_filter,
        'provider_filter': provider_filter,
        'search_query': search_query,
        'current_page_size': page_size,
    }
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'payments/payment_transactions_table.html', context)
    
    return render(request, 'payments/payment_transactions.html', context)


# Payment Action Views
def payment_view_details(request, payment_id):
    """View payment details in a modal"""
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    
    try:
        payment = get_object_or_404(
            models.Payment.objects.select_related('tenant', 'provider', 'invoice'),
            id=payment_id
        )
        
        # Get related transactions
        transactions = payment.transactions.all().order_by('-created_at')
        
        # Extract phone number from the most recent transaction's request_payload
        phone_number_used = None
        if transactions.exists():
            latest_transaction = transactions.first()
            if latest_transaction.request_payload and isinstance(latest_transaction.request_payload, dict):
                phone_number_used = latest_transaction.request_payload.get('accountNumber')
        
        context = {
            'payment': payment,
            'transactions': transactions,
            'phone_number_used': phone_number_used,  # Phone number used in payment
        }
        
        return render(request, 'payments/modals/payment_view_details.html', context)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)}, status=404)
        from django.contrib import messages
        messages.error(request, f'Payment not found: {str(e)}')
        from django.shortcuts import redirect
        return redirect('payments:payment_list')


def payment_edit(request, payment_id):
    """Edit payment - GET shows form, POST updates"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.http import JsonResponse
    from decimal import Decimal
    
    payment = get_object_or_404(models.Payment, id=payment_id)
    
    if request.method == 'POST':
        try:
            payment.amount = Decimal(str(request.POST.get('amount', payment.amount)))
            payment.payment_method = request.POST.get('payment_method', payment.payment_method)
            payment.status = request.POST.get('status', payment.status)
            payment.transaction_ref = request.POST.get('transaction_ref', payment.transaction_ref)
            if request.POST.get('paid_date'):
                from django.utils.dateparse import parse_date
                payment.paid_date = parse_date(request.POST.get('paid_date'))
            payment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Payment updated successfully'})
            
            messages.success(request, f'Payment #{payment.id} updated successfully.')
            return redirect('payments:payment_list')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
            messages.error(request, f'Error updating payment: {str(e)}')
    
    # GET request - show edit form
    context = {
        'payment': payment,
        'status_choices': models.Payment.STATUS_CHOICES,
        'method_choices': models.Payment.PAYMENT_METHOD_CHOICES,
    }
    
    return render(request, 'payments/modals/payment_edit.html', context)


def payment_delete(request, payment_id):
    """Delete payment - GET shows confirmation, POST deletes"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.http import JsonResponse
    
    payment = get_object_or_404(models.Payment, id=payment_id)
    
    if request.method == 'POST':
        payment_id_str = str(payment.id)
        payment.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Payment #{payment_id_str} deleted successfully.'
            })
        
        messages.success(request, f'Payment #{payment_id_str} deleted successfully.')
        return redirect('payments:payment_list')
    
    # GET request - show confirmation
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/modals/payment_delete_confirm.html', context)


def payment_generate_receipt(request, payment_id):
    """Generate payment receipt"""
    from django.shortcuts import get_object_or_404
    
    payment = get_object_or_404(
        models.Payment.objects.select_related('tenant', 'provider', 'invoice'),
        id=payment_id
    )
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'payments/modals/payment_receipt.html', context)


def transaction_view_details(request, transaction_id):
    """View transaction details in a modal"""
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    import json
    
    try:
        transaction = get_object_or_404(
            models.PaymentTransaction.objects.select_related(
                'payment__tenant', 'provider', 'payment'
            ),
            id=transaction_id
        )
        
        # Format JSON payloads for display
        request_payload_formatted = None
        response_payload_formatted = None
        
        if transaction.request_payload:
            try:
                request_payload_formatted = json.dumps(transaction.request_payload, indent=2)
            except:
                request_payload_formatted = str(transaction.request_payload)
        
        if transaction.response_payload:
            try:
                response_payload_formatted = json.dumps(transaction.response_payload, indent=2)
            except:
                response_payload_formatted = str(transaction.response_payload)
        
        context = {
            'transaction': transaction,
            'request_payload_formatted': request_payload_formatted,
            'response_payload_formatted': response_payload_formatted,
        }
        
        return render(request, 'payments/modals/transaction_view_details.html', context)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)}, status=404)
        from django.contrib import messages
        messages.error(request, f'Transaction not found: {str(e)}')
        from django.shortcuts import redirect
        return redirect('payments:payment_transactions')


def transaction_delete(request, transaction_id):
    """Delete transaction - GET shows confirmation, POST deletes"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.http import JsonResponse
    
    transaction = get_object_or_404(
        models.PaymentTransaction.objects.select_related('payment__tenant', 'provider', 'payment'),
        id=transaction_id
    )
    
    if request.method == 'POST':
        transaction_id_str = str(transaction.id)
        transaction.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Transaction #{transaction_id_str} deleted successfully.'
            })
        
        messages.success(request, f'Transaction #{transaction_id_str} deleted successfully.')
        return redirect('payments:payment_transactions')
    
    # GET request - show confirmation
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'payments/modals/transaction_delete_confirm.html', context)


def transaction_verify(request, transaction_id):
    """Verify transaction status with payment gateway"""
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    from payments.gateway_service import PaymentGatewayService
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'}, status=405)
    
    try:
        transaction = get_object_or_404(
            models.PaymentTransaction.objects.select_related('provider', 'payment'),
            id=transaction_id
        )
        
        # Get transaction reference (AZAM reference or gateway transaction ID)
        reference_id = transaction.azam_reference or transaction.gateway_transaction_id
        
        if not reference_id:
            return JsonResponse({
                'success': False,
                'message': 'Transaction reference not found. Cannot verify transaction.'
            }, status=400)
        
        # Get provider name
        provider_name = 'azam pay'
        if transaction.provider:
            provider_name = transaction.provider.name.lower()
        
        # Verify with gateway
        verification_result = PaymentGatewayService.verify_payment(
            transaction_id=reference_id,
            provider_name=provider_name
        )
        
        if not verification_result.get('success'):
            return JsonResponse({
                'success': False,
                'message': verification_result.get('error', 'Failed to verify transaction')
            }, status=400)
        
        # Update transaction status
        gateway_status = verification_result.get('status', '').lower()
        if gateway_status == 'successful':
            transaction.status = 'successful'
            transaction.payment.status = 'completed'
            transaction.payment.save()
        elif gateway_status == 'failed':
            transaction.status = 'failed'
            transaction.payment.status = 'failed'
            transaction.payment.save()
        elif gateway_status in ['pending', 'processing']:
            transaction.status = 'processing'
        
        # Update response payload with verification result
        transaction.response_payload = verification_result
        transaction.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Transaction verified successfully',
            'transaction_id': transaction.id,
            'status': transaction.status,
            'payment_status': transaction.payment.status,
            'verification_result': verification_result
        })
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error verifying transaction {transaction_id}: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'Error verifying transaction: {str(e)}'
        }, status=500)


# Payment Provider Action Views
def provider_view_details(request, provider_id):
    """View provider details in a modal"""
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    
    try:
        provider = get_object_or_404(models.PaymentProvider, id=provider_id)
        
        # Get provider statistics
        provider_transactions = models.PaymentTransaction.objects.filter(provider=provider)
        transaction_count = provider_transactions.count()
        successful_count = provider_transactions.filter(status='successful').count()
        failed_count = provider_transactions.filter(status='failed').count()
        pending_count = provider_transactions.filter(status__in=['pending', 'initiated', 'processing']).count()
        
        # Calculate total revenue
        from django.db.models import Sum
        total_revenue = provider_transactions.filter(
            status='successful'
        ).aggregate(total=Sum('payment__amount'))['total'] or 0
        
        # Calculate success rate
        success_rate = 0
        if transaction_count > 0:
            success_rate = round((successful_count / transaction_count) * 100, 2)
        
        # Get recent transactions
        recent_transactions = provider_transactions.select_related('payment__tenant').order_by('-created_at')[:5]
        
        context = {
            'provider': provider,
            'transaction_count': transaction_count,
            'successful_count': successful_count,
            'failed_count': failed_count,
            'pending_count': pending_count,
            'total_revenue': total_revenue,
            'success_rate': success_rate,
            'recent_transactions': recent_transactions,
        }
        
        return render(request, 'payments/modals/provider_view_details.html', context)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': str(e)}, status=404)
        from django.contrib import messages
        messages.error(request, f'Provider not found: {str(e)}')
        from django.shortcuts import redirect
        return redirect('payments:payment_methods')


def provider_edit(request, provider_id):
    """Edit provider - GET shows form, POST updates"""
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.http import JsonResponse
    from decimal import Decimal
    
    provider = get_object_or_404(models.PaymentProvider, id=provider_id)
    
    if request.method == 'POST':
        try:
            provider.name = request.POST.get('name', provider.name)
            provider.description = request.POST.get('description', provider.description)
            provider.provider_type = request.POST.get('provider_type', provider.provider_type)
            provider.transaction_fee = Decimal(str(request.POST.get('transaction_fee', provider.transaction_fee)))
            provider.is_active = request.POST.get('is_active') == 'on' or request.POST.get('is_active') == 'true'
            provider.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Provider updated successfully'})
            
            messages.success(request, f'Provider "{provider.name}" updated successfully.')
            return redirect('payments:payment_methods')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
            messages.error(request, f'Error updating provider: {str(e)}')
    
    # GET request - show edit form
    context = {
        'provider': provider,
        'provider_type_choices': models.PaymentProvider.PROVIDER_TYPE_CHOICES,
    }
    
    return render(request, 'payments/modals/provider_edit.html', context)


def provider_toggle_status(request, provider_id):
    """Toggle provider active/inactive status"""
    from django.shortcuts import get_object_or_404
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required'}, status=405)
    
    try:
        provider = get_object_or_404(models.PaymentProvider, id=provider_id)
        provider.is_active = not provider.is_active
        provider.save()
        
        status_text = 'enabled' if provider.is_active else 'disabled'
        
        return JsonResponse({
            'success': True,
            'message': f'Provider "{provider.name}" {status_text} successfully.',
            'is_active': provider.is_active
        })
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error toggling provider {provider_id}: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': f'Error updating provider: {str(e)}'
        }, status=500)