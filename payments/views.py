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
    
    # Payment statistics
    successful_payments = models.Payment.objects.filter(status='successful').count()
    pending_payments = models.Payment.objects.filter(status='pending').count()
    failed_payments = models.Payment.objects.filter(status='failed').count()
    
    # Invoice statistics
    paid_invoices = models.Invoice.objects.filter(status='paid').count()
    unpaid_invoices = models.Invoice.objects.filter(status='unpaid').count()
    cancelled_invoices = models.Invoice.objects.filter(status='cancelled').count()
    
    # Revenue calculations
    total_revenue = models.Payment.objects.filter(status='successful').aggregate(
        total=Sum('amount'))['total'] or 0
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
        'tenant', 'provider', 'invoice'
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
    
    # Pagination
    paginator = Paginator(payment_records, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Recent payments and invoices
    recent_payments = models.Payment.objects.select_related(
        'tenant', 'provider').order_by('-created_at')[:5]
    recent_invoices = models.Invoice.objects.select_related(
        'tenant').order_by('-created_at')[:5]
    
    # Get all invoices for the table
    all_invoices = models.Invoice.objects.select_related('tenant').order_by('-created_at')
    
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
        'recent_payments': recent_payments,
        'recent_invoices': recent_invoices,
        'page_obj': page_obj,
        'payment_records': payment_records,
        'all_invoices': all_invoices,
        'status_choices': models.Payment.STATUS_CHOICES,
        'invoice_status_choices': models.Invoice.STATUS_CHOICES,
    }
    
    return render(request, 'payments/payment_dashboard.html', context)


def invoice_list(request):
    invoices = models.Invoice.objects.select_related('tenant').all().order_by('-created_at')
    
    # Calculate statistics
    total_invoices = invoices.count()
    paid_invoices = invoices.filter(status='paid').count()
    unpaid_invoices = invoices.filter(status='unpaid').count()
    cancelled_invoices = invoices.filter(status='cancelled').count()
    
    # Calculate outstanding amount
    outstanding_amount = invoices.filter(status='unpaid').aggregate(
        total=Sum('amount'))['total'] or 0
    
    context = {
        'invoices': invoices,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'cancelled_invoices': cancelled_invoices,
        'outstanding_amount': outstanding_amount,
    }
    
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
    """Payment list with AJAX support and filtering - uses both RentPayment and Payment data"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    from rent.models import RentPayment
    
    # Try to get RentPayment data first, fall back to Payment if none exists
    rent_payments = RentPayment.objects.select_related('tenant', 'lease', 'lease__property', 'invoice').order_by('-payment_date')
    
    if rent_payments.exists():
        # Use RentPayment data
        payments = rent_payments
        use_rent_payments = True
    else:
        # Fall back to regular Payment data
        payments = models.Payment.objects.select_related('tenant', 'provider', 'invoice').order_by('-created_at')
        use_rent_payments = False
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    method_filter = request.GET.get('method')
    search_query = request.GET.get('search')
    
    if status_filter:
        if use_rent_payments:
            payments = payments.filter(status=status_filter)
        else:
            payments = payments.filter(status=status_filter)
    
    if method_filter:
        if use_rent_payments:
            payments = payments.filter(payment_method=method_filter)
        else:
            payments = payments.filter(payment_method=method_filter)
    
    if search_query:
        if use_rent_payments:
            payments = payments.filter(
                Q(tenant__username__icontains=search_query) |
                Q(tenant__first_name__icontains=search_query) |
                Q(tenant__last_name__icontains=search_query) |
                Q(reference_number__icontains=search_query) |
                Q(transaction_id__icontains=search_query) |
                Q(lease__property__name__icontains=search_query)
            )
        else:
            payments = payments.filter(
                Q(tenant__username__icontains=search_query) |
                Q(tenant__first_name__icontains=search_query) |
                Q(tenant__last_name__icontains=search_query) |
                Q(transaction_ref__icontains=search_query) |
                Q(reference_number__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(payments, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    total_payments = payments.count()
    if use_rent_payments:
        successful_payments = payments.filter(status='completed').count()
        pending_payments = payments.filter(status='pending').count()
        failed_payments = payments.filter(status='failed').count()
        total_revenue = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
        status_choices = RentPayment.PAYMENT_STATUS_CHOICES
        method_choices = RentPayment.PAYMENT_METHOD_CHOICES
    else:
        successful_payments = payments.filter(status='successful').count()
        pending_payments = payments.filter(status='pending').count()
        failed_payments = payments.filter(status='failed').count()
        total_revenue = payments.filter(status='successful').aggregate(total=Sum('amount'))['total'] or 0
        status_choices = models.Payment.STATUS_CHOICES
        method_choices = models.Payment.PAYMENT_METHOD_CHOICES
    
    # Calculate success rate
    success_rate = 0
    if total_payments > 0:
        success_rate = round((successful_payments / total_payments) * 100, 1)
    
    context = {
        'page_obj': page_obj,
        'payments': payments,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'total_revenue': total_revenue,
        'success_rate': success_rate,
        'status_choices': status_choices,
        'method_choices': method_choices,
        'use_rent_payments': use_rent_payments,
    }
    
    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print(f"AJAX Payment Request - Search: {search_query}, Status: {status_filter}, Method: {method_filter}")
        print(f"Filtered payments count: {payments.count()}")
        print(f"Using RentPayments: {use_rent_payments}")
        return render(request, 'payments/payment_list_table.html', context)
    
    return render(request, 'payments/payment_list.html', context)


def payment_methods(request):
    """Payment methods management page"""
    # Get all payment providers
    providers = models.PaymentProvider.objects.all()
    
    # Get payment method statistics
    total_providers = providers.count()
    active_providers = providers.filter(is_active=True).count()
    inactive_providers = providers.filter(is_active=False).count()
    
    # Get recent transactions by provider
    recent_transactions = models.PaymentTransaction.objects.select_related(
        'provider', 'payment__tenant'
    ).order_by('-created_at')[:10]
    
    # Calculate total transactions and revenue by provider
    provider_stats = []
    for provider in providers:
        provider_transactions = models.PaymentTransaction.objects.filter(provider=provider)
        transaction_count = provider_transactions.count()
        successful_transactions = provider_transactions.filter(status='successful').count()
        provider_stats.append({
            'provider': provider,
            'transaction_count': transaction_count,
            'successful_count': successful_transactions,
        })
    
    context = {
        'providers': providers,
        'total_providers': total_providers,
        'active_providers': active_providers,
        'inactive_providers': inactive_providers,
        'recent_transactions': recent_transactions,
        'provider_stats': provider_stats,
    }
    
    return render(request, 'payments/payment_methods.html', context)