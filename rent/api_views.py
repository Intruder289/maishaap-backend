from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import RentInvoice, LateFee, RentReminder
from payments.models import Payment, PaymentTransaction, PaymentProvider
from payments.gateway_service import PaymentGatewayService
from .serializers import (
    RentInvoiceSerializer, RentInvoiceCreateSerializer,
    RentPaymentSerializer, RentPaymentCreateSerializer,
    LateFeeSerializer, RentReminderSerializer,
    RentDashboardSerializer, TenantRentSummarySerializer
)
from documents.models import Lease


class RentInvoiceViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Rent Invoice management
    
    list: Get all rent invoices (filtered by user role)
    retrieve: Get a specific rent invoice
    create: Create a new rent invoice
    update: Update a rent invoice
    partial_update: Partially update a rent invoice
    destroy: Delete a rent invoice
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RentInvoiceCreateSerializer
        return RentInvoiceSerializer
    
    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return RentInvoice.objects.none()
            
        queryset = RentInvoice.objects.select_related('lease', 'tenant').prefetch_related('unified_payments')
        
        # Filter based on user role
        if not self.request.user.is_staff:
            queryset = queryset.filter(tenant=self.request.user)
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id and self.request.user.is_staff:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        lease_id = self.request.query_params.get('lease_id')
        if lease_id:
            queryset = queryset.filter(lease_id=lease_id)
        
        # Date range filters
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        if from_date:
            queryset = queryset.filter(due_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(due_date__lte=to_date)
        
        return queryset.order_by('-due_date')
    
    @swagger_auto_schema(
        method='post',
        operation_description="Mark a rent invoice as paid. Creates a payment record and updates invoice status.",
        operation_summary="Mark Invoice as Paid",
        tags=['Rent'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Payment amount (defaults to balance due)'),
                'payment_method': openapi.Schema(type=openapi.TYPE_STRING, description='Payment method (cash, mobile_money, bank_transfer)'),
                'reference_number': openapi.Schema(type=openapi.TYPE_STRING, description='Payment reference number')
            }
        ),
        responses={
            200: openapi.Response(
                description="Payment recorded successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'invoice_status': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: "Authentication required",
            403: "Permission denied"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark an invoice as paid"""
        invoice = self.get_object()
        amount = request.data.get('amount', invoice.balance_due)
        payment_method = request.data.get('payment_method', 'cash')
        reference = request.data.get('reference_number', '')
        
        # Create payment record using unified Payment model
        payment = Payment.objects.create(
            rent_invoice=invoice,
            lease=invoice.lease,
            tenant=invoice.tenant,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference,
            paid_date=timezone.now().date(),
            status='completed',
            recorded_by=request.user
        )
        
        return Response({
            'message': 'Payment recorded successfully',
            'payment_id': payment.id,
            'invoice_status': invoice.status
        })
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get all overdue rent invoices (invoices past due date with status 'sent' or 'overdue')",
        operation_summary="Get Overdue Invoices",
        tags=['Rent'],
        responses={
            200: RentInvoiceSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False)
    def overdue(self, request):
        """Get overdue invoices"""
        queryset = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status__in=['sent', 'overdue']
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Generate monthly rent invoices for all active leases. Admin/staff only.",
        operation_summary="Generate Monthly Invoices",
        tags=['Rent'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'month': openapi.Schema(type=openapi.TYPE_INTEGER, description='Month (1-12), defaults to current month'),
                'year': openapi.Schema(type=openapi.TYPE_INTEGER, description='Year, defaults to current year')
            }
        ),
        responses={
            200: openapi.Response(
                description="Invoices generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            403: "Permission denied (admin/staff only)",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False, methods=['post'])
    def generate_monthly(self, request):
        """Generate monthly invoices for all active leases"""
        if not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        month = request.data.get('month', timezone.now().month)
        year = request.data.get('year', timezone.now().year)
        
        # Get active leases
        period_start = datetime(year, month, 1).date()
        if month == 12:
            period_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            period_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        active_leases = Lease.objects.filter(
            status='active',
            start_date__lte=period_end,
            end_date__gte=period_start
        )
        
        created_count = 0
        for lease in active_leases:
            # Check if invoice already exists for this period
            existing = RentInvoice.objects.filter(
                lease=lease,
                period_start=period_start,
                period_end=period_end
            ).exists()
            
            if not existing:
                due_date = period_start + timedelta(days=5)  # Due 5 days after period start
                RentInvoice.objects.create(
                    lease=lease,
                    tenant=lease.tenant,
                    due_date=due_date,
                    period_start=period_start,
                    period_end=period_end,
                    base_rent=lease.rent_amount
                )
                created_count += 1
        
        return Response({
            'message': f'Generated {created_count} invoices for {period_start.strftime("%B %Y")}',
            'created_count': created_count
        })


class RentPaymentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Rent Payment management (using unified Payment model)
    
    list: Get all rent payments (filtered by user role)
    retrieve: Get a specific rent payment
    create: Create a new rent payment
    update: Update a rent payment
    partial_update: Partially update a rent payment
    destroy: Delete a rent payment
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RentPaymentCreateSerializer
        return RentPaymentSerializer
    
    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()
            
        # Filter only rent payments (those with rent_invoice set)
        queryset = Payment.objects.filter(rent_invoice__isnull=False).select_related('rent_invoice', 'lease', 'tenant')
        
        # Filter based on user role
        if not self.request.user.is_staff:
            queryset = queryset.filter(tenant=self.request.user)
        
        # Apply filters
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id and self.request.user.is_staff:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        invoice_id = self.request.query_params.get('invoice_id')
        if invoice_id:
            queryset = queryset.filter(rent_invoice_id=invoice_id)
        
        payment_method = self.request.query_params.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        return queryset.order_by('-paid_date')
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get recent rent payments. Returns the most recent payments, limited by 'limit' query parameter (default: 10).",
        operation_summary="Get Recent Rent Payments",
        tags=['Rent'],
        manual_parameters=[
            openapi.Parameter('limit', openapi.IN_QUERY, description="Number of recent payments to return (default: 10)", type=openapi.TYPE_INTEGER, required=False)
        ],
        responses={
            200: RentPaymentSerializer(many=True),
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False)
    def recent(self, request):
        """Get recent payments"""
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Initiate payment with payment gateway (AZAM Pay). Creates PaymentTransaction and returns payment link for mobile app.",
        operation_summary="Initiate Gateway Payment",
        tags=['Rent'],
        responses={
            201: openapi.Response(
                description="Payment initiated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'transaction_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'payment_link': openapi.Schema(type=openapi.TYPE_STRING, description='URL to redirect user for payment'),
                        'transaction_reference': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Payment already completed or gateway error",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def initiate_gateway(self, request, pk=None):
        """
        Initiate payment with payment gateway (AZAM Pay)
        
        Flow:
        1. Creates Payment record (status='pending')
        2. Creates PaymentTransaction
        3. Calls AZAM Pay API
        4. Returns payment link to mobile app
        """
        payment = self.get_object()
        
        # Check if payment is already completed
        if payment.status == 'completed':
            return Response({
                'error': 'Payment already completed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create AZAM Pay provider
        provider, _ = PaymentProvider.objects.get_or_create(
            name='AZAM Pay',
            defaults={'description': 'AZAM Pay Payment Gateway'}
        )
        
        # Get callback URL - use configured webhook URL (production) instead of localhost
        from django.conf import settings
        callback_url = getattr(settings, 'AZAM_PAY_WEBHOOK_URL', None)
        if not callback_url:
            # Fallback to BASE_URL if webhook URL not configured
            base_domain = getattr(settings, 'BASE_URL', 'https://portal.maishaapp.co.tz')
            callback_url = f"{base_domain}/api/v1/payments/webhook/azam-pay/"
        
        # Initiate payment with gateway
        gateway_result = PaymentGatewayService.initiate_payment(
            payment=payment,
            provider_name='azam pay',
            callback_url=callback_url
        )
        
        if not gateway_result['success']:
            return Response({
                'error': gateway_result.get('error', 'Failed to initiate payment'),
                'details': gateway_result
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create PaymentTransaction record
        transaction = PaymentTransaction.objects.create(
            payment=payment,
            provider=provider,
            azam_reference=gateway_result.get('reference'),
            gateway_transaction_id=gateway_result.get('transaction_id'),
            request_payload={'amount': str(payment.amount), 'callback_url': callback_url},
            response_payload=gateway_result,
            status='initiated'
        )
        
        # Update payment with transaction ID
        payment.transaction_id = gateway_result.get('transaction_id')
        payment.provider = provider
        payment.status = 'pending'
        payment.save()
        
        return Response({
            'success': True,
            'payment_id': payment.id,
            'transaction_id': transaction.id,
            'payment_link': gateway_result.get('payment_link'),
            'transaction_reference': gateway_result.get('reference'),
            'message': 'Payment initiated successfully. Redirect user to payment_link.'
        }, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Verify payment status with payment gateway. Mobile app should call this after user completes payment on gateway.",
        operation_summary="Verify Payment",
        tags=['Rent'],
        responses={
            200: openapi.Response(
                description="Payment verification result",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'transaction_status': openapi.Schema(type=openapi.TYPE_STRING),
                        'verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Verification failed or no transaction found",
            404: "Transaction not found",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify payment status with payment gateway
        
        Mobile app calls this after user completes payment on gateway
        """
        payment = self.get_object()
        
        # Get the latest transaction
        transaction = payment.transactions.order_by('-created_at').first()
        
        if not transaction:
            return Response({
                'error': 'No transaction found for this payment'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not transaction.gateway_transaction_id:
            return Response({
                'error': 'No gateway transaction ID found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify with gateway
        verify_result = PaymentGatewayService.verify_payment(
            transaction_id=transaction.gateway_transaction_id,
            provider_name='azam pay'
        )
        
        if not verify_result['success']:
            return Response({
                'error': verify_result.get('error', 'Failed to verify payment'),
                'details': verify_result
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update transaction status
        transaction.status = verify_result.get('status', 'processing')
        transaction.response_payload = verify_result
        transaction.save()
        
        # Update payment status if successful
        if verify_result.get('status') == 'successful':
            payment.status = 'completed'
            payment.paid_date = timezone.now().date()
            payment.save()
        
        return Response({
            'success': True,
            'payment_id': payment.id,
            'status': payment.status,
            'transaction_status': transaction.status,
            'verified': verify_result.get('status') == 'successful'
        })


class LateFeeViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Late Fee management
    
    list: Get all late fees (filtered by user role)
    retrieve: Get a specific late fee
    create: Create a new late fee
    update: Update a late fee
    partial_update: Partially update a late fee
    destroy: Delete a late fee
    """
    serializer_class = LateFeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return LateFee.objects.none()
            
        queryset = LateFee.objects.select_related('lease')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(lease__tenant=self.request.user)
        
        return queryset.order_by('-created_at')


class RentReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Rent Reminder management (Read-only)
    
    list: Get all rent reminders (filtered by user role)
    retrieve: Get a specific rent reminder
    """
    serializer_class = RentReminderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Handle schema generation (swagger_fake_view)
        if getattr(self, 'swagger_fake_view', False):
            return RentReminder.objects.none()
            
        queryset = RentReminder.objects.select_related('invoice', 'tenant')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(tenant=self.request.user)
        
        return queryset.order_by('-sent_at')


class RentDashboardViewSet(viewsets.ViewSet):
    """
    API ViewSet for Rent Dashboard and Statistics
    
    Provides dashboard statistics and tenant summaries for rent management.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get rent dashboard statistics including total monthly rent, collected amount, outstanding amount, overdue amount, collection rate, and recent data.",
        operation_summary="Get Rent Dashboard Statistics",
        tags=['Rent'],
        responses={
            200: RentDashboardSerializer,
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False)
    def stats(self, request):
        """Get rent dashboard statistics"""
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
        active_leases = leases.count()
        
        # Collection rate
        if total_monthly_rent > 0:
            collection_rate = float(collected_this_month / total_monthly_rent * 100)
        else:
            collection_rate = 0.0
        
        # Recent data
        recent_payments = payments.filter(status='completed').order_by('-created_at')[:5]
        overdue_list = overdue_invoices.order_by('due_date')[:10]
        
        data = {
            'total_monthly_rent': total_monthly_rent,
            'collected_this_month': collected_this_month,
            'outstanding_amount': outstanding_amount,
            'overdue_amount': overdue_amount,
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_count,
            'active_leases': active_leases,
            'collection_rate': collection_rate,
            'recent_payments': recent_payments,
            'overdue_invoices_list': overdue_list
        }
        
        serializer = RentDashboardSerializer(data)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get rent summary for a specific tenant. Includes active lease, current invoice, payment history, outstanding balance, and next due date.",
        operation_summary="Get Tenant Rent Summary",
        tags=['Rent'],
        manual_parameters=[
            openapi.Parameter('tenant_id', openapi.IN_QUERY, description="Tenant user ID (required for staff, optional for tenants)", type=openapi.TYPE_INTEGER, required=False)
        ],
        responses={
            200: TenantRentSummarySerializer,
            403: "Permission denied",
            404: "No active lease found",
            401: "Authentication required"
        },
        security=[{'Bearer': []}]
    )
    @action(detail=False)
    def tenant_summary(self, request):
        """Get rent summary for a specific tenant"""
        tenant_id = request.query_params.get('tenant_id')
        
        if not request.user.is_staff and str(request.user.id) != tenant_id:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        tenant = get_object_or_404(User, id=tenant_id) if tenant_id else request.user
        
        # Get active lease
        active_lease = Lease.objects.filter(tenant=tenant, status='active').first()
        
        if not active_lease:
            return Response({'error': 'No active lease found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get current invoice
        current_invoice = RentInvoice.objects.filter(
            tenant=tenant,
            due_date__gte=timezone.now().date()
        ).order_by('due_date').first()
        
        # Payment history (last 12 payments) - only rent payments
        payment_history = Payment.objects.filter(
            rent_invoice__isnull=False,
            tenant=tenant,
            status='completed'
        ).order_by('-paid_date')[:12]
        
        # Calculate totals
        current_year = timezone.now().year
        total_paid_this_year = Payment.objects.filter(
            rent_invoice__isnull=False,
            tenant=tenant,
            paid_date__year=current_year,
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        outstanding_balance = RentInvoice.objects.filter(
            tenant=tenant,
            status__in=['sent', 'overdue']
        ).aggregate(
            total=Sum(F('total_amount') - F('amount_paid'))
        )['total'] or Decimal('0.00')
        
        # Next due date
        next_invoice = RentInvoice.objects.filter(
            tenant=tenant,
            status__in=['draft', 'sent'],
            due_date__gte=timezone.now().date()
        ).order_by('due_date').first()
        
        next_due_date = next_invoice.due_date if next_invoice else None
        is_current = outstanding_balance == 0
        
        data = {
            'tenant': tenant,
            'active_lease': active_lease,
            'current_invoice': current_invoice,
            'payment_history': payment_history,
            'total_paid_this_year': total_paid_this_year,
            'outstanding_balance': outstanding_balance,
            'next_due_date': next_due_date,
            'is_current': is_current
        }
        
        serializer = TenantRentSummarySerializer(data)
        return Response(serializer.data)