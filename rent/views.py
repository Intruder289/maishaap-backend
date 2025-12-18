from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal

from .models import RentInvoice, LateFee, RentReminder
from payments.models import Payment
from documents.models import Lease
from .forms import RentPaymentForm, RentInvoiceForm


@login_required
def rent_dashboard(request):
    """Rent management dashboard"""
    current_month = timezone.now().date().replace(day=1)
    
    # Base queryset based on user role
    if request.user.is_staff:
        invoices = RentInvoice.objects.all()
        payments = Payment.objects.filter(rent_invoice__isnull=False)
        leases = Lease.objects.filter(status='active')
    else:
        invoices = RentInvoice.objects.filter(tenant=request.user)
        payments = Payment.objects.filter(rent_invoice__isnull=False, tenant=request.user)
        leases = Lease.objects.filter(tenant=request.user, status='active')
    
    # Calculate statistics
    total_monthly_rent = leases.aggregate(Sum('rent_amount'))['rent_amount__sum'] or Decimal('0.00')
    
    collected_this_month = payments.filter(
        paid_date__gte=current_month,
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    outstanding_invoices = invoices.filter(status__in=['sent', 'overdue'])
    outstanding_amount = outstanding_invoices.aggregate(
        total=Sum(F('total_amount') - F('amount_paid'))
    )['total'] or Decimal('0.00')
    
    overdue_invoices = invoices.filter(
        due_date__lt=timezone.now().date(),
        status__in=['sent', 'overdue']
    )
    overdue_amount = overdue_invoices.aggregate(
        total=Sum(F('total_amount') - F('amount_paid'))
    )['total'] or Decimal('0.00')
    
    # Counts
    total_invoices = invoices.count()
    paid_invoices = invoices.filter(status='paid').count()
    overdue_count = overdue_invoices.count()
    active_leases_count = leases.count()
    
    # Collection rate
    if total_monthly_rent > 0:
        collection_rate = float(collected_this_month / total_monthly_rent * 100)
    else:
        collection_rate = 0.0
    
    # Recent data
    recent_payments = payments.filter(status='completed').order_by('-created_at')[:5]
    upcoming_due = invoices.filter(
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timedelta(days=7),
        status__in=['draft', 'sent']
    ).order_by('due_date')[:5]
    
    # Calculate unpaid invoices
    unpaid_invoices = total_invoices - paid_invoices
    
    context = {
        'total_monthly_rent': total_monthly_rent,
        'collected_this_month': collected_this_month,
        'outstanding_amount': outstanding_amount,
        'overdue_amount': overdue_amount,
        'total_invoices': total_invoices,
        'paid_invoices': paid_invoices,
        'unpaid_invoices': unpaid_invoices,
        'overdue_count': overdue_count,
        'active_leases_count': active_leases_count,
        'collection_rate': collection_rate,
        'recent_payments': recent_payments,
        'upcoming_due': upcoming_due,
        'current_month': current_month.strftime('%B %Y'),
    }
    
    return render(request, 'rent/dashboard.html', context)


@login_required
def invoice_list(request):
    """List all rent invoices"""
    invoices = RentInvoice.objects.select_related('lease', 'tenant').prefetch_related('payments')
    
    # Filter based on user role
    if not request.user.is_staff:
        invoices = invoices.filter(tenant=request.user)
    
    # Apply search and filters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(tenant__first_name__icontains=search) |
            Q(tenant__last_name__icontains=search) |
            Q(tenant__username__icontains=search) |
            Q(lease__property_ref__name__icontains=search)
        )
    
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(invoices.order_by('-due_date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'status_choices': RentInvoice.STATUS_CHOICES,
    }
    
    return render(request, 'rent/invoice_list.html', context)


@login_required
def invoice_detail(request, invoice_id):
    """Display invoice details"""
    invoice = get_object_or_404(
        RentInvoice.objects.select_related('lease', 'tenant').prefetch_related('payments'),
        id=invoice_id
    )
    
    # Check permissions
    if not request.user.is_staff and invoice.tenant != request.user:
        messages.error(request, 'You do not have permission to view this invoice.')
        return redirect('rent:invoice_list')
    
    payments = invoice.payments.order_by('-payment_date')
    
    context = {
        'invoice': invoice,
        'payments': payments,
    }
    
    return render(request, 'rent/invoice_detail.html', context)


@login_required
def payment_list(request):
    """List all rent payments"""
    payments = Payment.objects.filter(rent_invoice__isnull=False).select_related('rent_invoice', 'lease', 'tenant')
    
    # Filter based on user role
    if not request.user.is_staff:
        payments = payments.filter(tenant=request.user)
    
    # Apply search and filters
    search = request.GET.get('search', '')
    method_filter = request.GET.get('method', '')
    
    if search:
        payments = payments.filter(
            Q(rent_invoice__invoice_number__icontains=search) |
            Q(tenant__first_name__icontains=search) |
            Q(tenant__last_name__icontains=search) |
            Q(reference_number__icontains=search)
        )
    
    if method_filter:
        payments = payments.filter(payment_method=method_filter)
    
    # Calculate statistics for dashboard cards
    from django.db.models import Sum, Count, Avg
    stats = payments.aggregate(
        total_collected=Sum('amount'),
        total_payments=Count('id'),
        average_payment=Avg('amount')
    )
    
    # Handle None values
    total_collected = stats['total_collected'] or 0
    total_payments = stats['total_payments'] or 0
    average_payment = stats['average_payment'] or 0
    
    # Pagination
    paginator = Paginator(payments.order_by('-paid_date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'method_filter': method_filter,
        'method_choices': Payment.PAYMENT_METHOD_CHOICES,
        'total_collected': total_collected,
        'total_payments': total_payments,
        'average_payment': average_payment,
    }
    
    return render(request, 'rent/payment_list.html', context)


@login_required
def record_payment_general(request):
    """Record a general payment (not tied to specific invoice)"""
    if request.method == 'POST':
        form = RentPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.tenant = request.user
            payment.recorded_by = request.user
            payment.save()
            
            messages.success(request, f'Payment of TZS {payment.amount:,.0f} recorded successfully.')
            return redirect('rent:payment_list')
    else:
        form = RentPaymentForm()
    
    # Get user's active leases for context
    active_leases = Lease.objects.filter(tenant=request.user, status='active')
    
    context = {
        'form': form,
        'active_leases': active_leases,
    }
    
    return render(request, 'rent/record_payment_general.html', context)


@login_required
def record_payment(request, invoice_id):
    """Record a payment for an invoice"""
    invoice = get_object_or_404(RentInvoice, id=invoice_id)
    
    # Check permissions
    if not request.user.is_staff and invoice.tenant != request.user:
        messages.error(request, 'You do not have permission to record payment for this invoice.')
        return redirect('rent:invoice_list')
    
    if request.method == 'POST':
        form = RentPaymentForm(request.POST)
        if form.is_valid():
            # Create unified Payment record
            payment = Payment.objects.create(
                rent_invoice=invoice,
                lease=invoice.lease,
                tenant=invoice.tenant,
                amount=form.cleaned_data['amount'],
                payment_method=form.cleaned_data['payment_method'],
                reference_number=form.cleaned_data.get('reference_number', ''),
                transaction_id=form.cleaned_data.get('transaction_id', ''),
                paid_date=timezone.now().date(),
                status='completed',
                notes=form.cleaned_data.get('notes', ''),
                recorded_by=request.user
            )
            
            messages.success(request, f'Payment of TZS {payment.amount:,.0f} recorded successfully.')
            return redirect('rent:invoice_detail', invoice_id=invoice.id)
    else:
        form = RentPaymentForm(initial={
            'amount': invoice.balance_due,
        })
    
    context = {
        'form': form,
        'invoice': invoice,
    }
    
    return render(request, 'rent/record_payment.html', context)


@login_required
def create_invoice(request):
    """Create a new rent invoice"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to create invoices.')
        return redirect('rent:dashboard')
    
    if request.method == 'POST':
        form = RentInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.tenant = invoice.lease.tenant
            invoice.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('rent:invoice_detail', invoice_id=invoice.id)
    else:
        form = RentInvoiceForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'rent/create_invoice.html', context)


@login_required
def tenant_summary(request, tenant_id=None):
    """Display rent summary for a tenant"""
    if tenant_id:
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to view other tenant summaries.')
            return redirect('rent:dashboard')
        tenant = get_object_or_404(User, id=tenant_id)
    else:
        tenant = request.user
    
    # Get active lease
    active_lease = Lease.objects.filter(tenant=tenant, status='active').first()
    
    if not active_lease:
        messages.warning(request, 'No active lease found for this tenant.')
        return redirect('rent:dashboard')
    
    # Get invoices and payments
    invoices = RentInvoice.objects.filter(tenant=tenant).order_by('-due_date')
    payments = Payment.objects.filter(rent_invoice__isnull=False, tenant=tenant, status='completed').order_by('-paid_date')
    
    # Calculate totals
    current_year = timezone.now().year
    total_paid_this_year = payments.filter(
        paid_date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    outstanding_balance = invoices.filter(
        status__in=['sent', 'overdue']
    ).aggregate(
        total=Sum(F('total_amount') - F('amount_paid'))
    )['total'] or Decimal('0.00')
    
    # Next due date
    next_invoice = invoices.filter(
        status__in=['draft', 'sent'],
        due_date__gte=timezone.now().date()
    ).order_by('due_date').first()
    
    context = {
        'tenant': tenant,
        'active_lease': active_lease,
        'invoices': invoices[:12],  # Last 12 invoices
        'payments': payments[:12],  # Last 12 payments
        'total_paid_this_year': total_paid_this_year,
        'outstanding_balance': outstanding_balance,
        'next_invoice': next_invoice,
        'is_current': outstanding_balance == 0,
    }
    
    return render(request, 'rent/tenant_summary.html', context)


@login_required
def invoice_delete(request, invoice_id):
    """Delete a rent invoice"""
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'You do not have permission to delete invoices.'}, status=403)
        messages.error(request, 'You do not have permission to delete invoices.')
        return redirect('rent:invoice_list')
    
    invoice = get_object_or_404(RentInvoice, id=invoice_id)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Invoice {invoice_number} deleted successfully.'
            })
        
        messages.success(request, f'Invoice {invoice_number} deleted successfully.')
        return redirect('rent:invoice_list')
    
    # GET request - show confirmation
    context = {
        'invoice': invoice,
    }
    
    return render(request, 'rent/invoice_delete_confirm.html', context)