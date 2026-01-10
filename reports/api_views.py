from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import ReportTemplate, GeneratedReport, FinancialSummary
from payments.models import Payment, Expense
from rent.models import RentInvoice, RentPayment
from maintenance.models import MaintenanceRequest
from properties.models import Property
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='get',
    operation_description="Get financial summary for dashboard including total revenue, expenses, net income, rent collected, and pending payments",
    operation_summary="Get Financial Summary",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Financial summary data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_revenue': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_expenses': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'net_income': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'rent_collected': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'pending_payments': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def FinancialSummaryView(request):
    """Get financial summary for dashboard"""
    user = request.user
    
    # Filter based on user role (multi-tenancy)
    if user.is_staff or user.is_superuser:
        # Staff sees all data
        payments = Payment.objects.filter(status='completed')
        expenses = Expense.objects.all()
        rent_payments = RentPayment.objects.all()
        rent_invoices = RentInvoice.objects.all()
    else:
        # Property owners see their properties' data
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                # Owners see data for their properties
                owner_properties = Property.objects.filter(owner=user)
                payments = Payment.objects.filter(
                    status='completed',
                    property__in=owner_properties
                )
                expenses = Expense.objects.filter(property__in=owner_properties)
                rent_payments = RentPayment.objects.filter(
                    invoice__lease__property_ref__in=owner_properties
                )
                rent_invoices = RentInvoice.objects.filter(
                    lease__property_ref__in=owner_properties
                )
            else:
                # Tenants see only their own data
                payments = Payment.objects.filter(status='completed', tenant=user)
                expenses = Expense.objects.none()  # Tenants don't see expenses
                rent_payments = RentPayment.objects.filter(tenant=user)
                rent_invoices = RentInvoice.objects.filter(tenant=user)
        except Profile.DoesNotExist:
            # Fallback for users without profile
            payments = Payment.objects.filter(status='completed', tenant=user)
            expenses = Expense.objects.none()
            rent_payments = RentPayment.objects.filter(tenant=user)
            rent_invoices = RentInvoice.objects.filter(tenant=user)
    
    # Calculate total revenue (from all completed payments)
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate total expenses
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate net income
    net_income = total_revenue - total_expenses
    
    # Calculate rent collected (from rent payments)
    rent_collected = rent_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate pending payments (invoices that are not paid)
    pending_invoices = rent_invoices.filter(status__in=['sent', 'overdue'])
    pending_payments = pending_invoices.aggregate(
        total=Sum(F('total_amount') - F('amount_paid'))
    )['total'] or Decimal('0.00')
    
    return Response({
        'total_revenue': float(total_revenue),
        'total_expenses': float(total_expenses),
        'net_income': float(net_income),
        'rent_collected': float(rent_collected),
        'pending_payments': float(pending_payments)
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get rent collection report including collection rate, total collected, pending amount, and overdue amount",
    operation_summary="Get Rent Collection Report",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Rent collection report data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'collection_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'total_collected': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'pending_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'overdue_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def RentCollectionReportView(request):
    """Get rent collection report"""
    user = request.user
    
    # Filter based on user role
    if user.is_staff or user.is_superuser:
        invoices = RentInvoice.objects.all()
        payments = RentPayment.objects.all()
    else:
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                owner_properties = Property.objects.filter(owner=user)
                invoices = RentInvoice.objects.filter(
                    lease__property_ref__in=owner_properties
                )
                payments = RentPayment.objects.filter(
                    invoice__lease__property_ref__in=owner_properties
                )
            else:
                invoices = RentInvoice.objects.filter(tenant=user)
                payments = RentPayment.objects.filter(tenant=user)
        except Profile.DoesNotExist:
            invoices = RentInvoice.objects.filter(tenant=user)
            payments = RentPayment.objects.filter(tenant=user)
    
    # Calculate total collected
    total_collected = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Calculate total expected (from all invoices)
    total_expected = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Calculate collection rate
    collection_rate = (float(total_collected) / float(total_expected) * 100) if total_expected > 0 else 0.0
    
    # Calculate pending amount (invoices not fully paid)
    pending_invoices = invoices.filter(status__in=['sent', 'overdue'])
    pending_amount = pending_invoices.aggregate(
        total=Sum(F('total_amount') - F('amount_paid'))
    )['total'] or Decimal('0.00')
    
    # Calculate overdue amount
    overdue_invoices = invoices.filter(
        due_date__lt=timezone.now().date(),
        status__in=['sent', 'overdue']
    )
    overdue_amount = overdue_invoices.aggregate(
        total=Sum(F('total_amount') - F('amount_paid'))
    )['total'] or Decimal('0.00')
    
    return Response({
        'collection_rate': round(collection_rate, 2),
        'total_collected': float(total_collected),
        'pending_amount': float(pending_amount),
        'overdue_amount': float(overdue_amount)
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get expense report including total expenses, breakdown by categories, and monthly trends",
    operation_summary="Get Expense Report",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Expense report data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_expenses': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'categories': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'monthly_trend': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ExpenseReportView(request):
    """Get expense report"""
    user = request.user
    
    # Filter based on user role
    if user.is_staff or user.is_superuser:
        expenses = Expense.objects.all()
    else:
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                owner_properties = Property.objects.filter(owner=user)
                expenses = Expense.objects.filter(property__in=owner_properties)
            else:
                # Tenants don't see expenses
                expenses = Expense.objects.none()
        except Profile.DoesNotExist:
            expenses = Expense.objects.none()
    
    # Calculate total expenses
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Breakdown by property (since Expense model doesn't have category)
    categories = []
    if expenses.exists():
        property_breakdown = expenses.values('property__title', 'property__id').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        for item in property_breakdown:
            categories.append({
                'category': item['property__title'] or 'Unnamed Property',
                'property_id': item['property__id'],
                'total': float(item['total']),
                'count': item['count']
            })
    
    # Monthly trend (last 12 months)
    monthly_trend = []
    current_date = timezone.now().date()
    for i in range(11, -1, -1):  # Last 12 months
        month_start = (current_date - timedelta(days=30*i)).replace(day=1)
        if month_start.month == 12:
            month_end = datetime(month_start.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(month_start.year, month_start.month + 1, 1).date() - timedelta(days=1)
        
        month_expenses = expenses.filter(
            incurred_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        monthly_trend.append({
            'month': month_start.strftime('%Y-%m'),
            'total': float(month_expenses)
        })
    
    return Response({
        'total_expenses': float(total_expenses),
        'categories': categories,
        'monthly_trend': monthly_trend
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get property occupancy report including occupancy rate, occupied units, vacant units, and total units",
    operation_summary="Get Property Occupancy Report",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Property occupancy report data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'occupancy_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'occupied_units': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'vacant_units': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'total_units': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def PropertyOccupancyReportView(request):
    """Get property occupancy report"""
    user = request.user
    
    # Filter based on user role
    if user.is_staff or user.is_superuser:
        properties = Property.objects.filter(is_active=True, is_approved=True)
    else:
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                properties = Property.objects.filter(owner=user, is_active=True, is_approved=True)
            else:
                # Tenants don't see occupancy reports
                properties = Property.objects.none()
        except Profile.DoesNotExist:
            properties = Property.objects.none()
    
    total_units = properties.count()
    
    # Count occupied units (properties with active leases or bookings)
    from documents.models import Lease, Booking
    occupied_properties = properties.filter(
        Q(leases__status='active') | Q(property_bookings__booking_status__in=['confirmed', 'checked_in'])
    ).distinct()
    occupied_units = occupied_properties.count()
    
    vacant_units = total_units - occupied_units
    
    # Calculate occupancy rate
    occupancy_rate = (occupied_units / total_units * 100) if total_units > 0 else 0.0
    
    return Response({
        'occupancy_rate': round(occupancy_rate, 2),
        'occupied_units': occupied_units,
        'vacant_units': vacant_units,
        'total_units': total_units
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get maintenance report including total requests, completed, pending, in progress, and average completion time",
    operation_summary="Get Maintenance Report",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Maintenance report data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_requests': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'pending': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'in_progress': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'average_completion_time': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def MaintenanceReportView(request):
    """Get maintenance report"""
    user = request.user
    
    # Filter based on user role
    if user.is_staff or user.is_superuser:
        requests = MaintenanceRequest.objects.all()
    else:
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                owner_properties = Property.objects.filter(owner=user)
                requests = MaintenanceRequest.objects.filter(property__in=owner_properties)
            else:
                requests = MaintenanceRequest.objects.filter(tenant=user)
        except Profile.DoesNotExist:
            requests = MaintenanceRequest.objects.filter(tenant=user)
    
    total_requests = requests.count()
    completed = requests.filter(status='completed').count()
    pending = requests.filter(status='pending').count()
    in_progress = requests.filter(status='in_progress').count()
    
    # Calculate average completion time (in days)
    completed_requests = requests.filter(
        status='completed',
        completed_at__isnull=False,
        created_at__isnull=False
    )
    
    if completed_requests.exists():
        completion_times = []
        for req in completed_requests:
            if req.completed_at and req.created_at:
                delta = req.completed_at - req.created_at
                completion_times.append(delta.total_seconds() / 86400)  # Convert to days
        
        average_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    else:
        average_completion_time = 0
    
    return Response({
        'total_requests': total_requests,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'average_completion_time': round(average_completion_time, 2)
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get dashboard statistics including properties count, tenants count, maintenance requests, and monthly revenue",
    operation_summary="Get Dashboard Statistics",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Dashboard statistics",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'properties': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'tenants': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'maintenance_requests': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'monthly_revenue': openapi.Schema(type=openapi.TYPE_NUMBER),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def DashboardStatsView(request):
    """Get dashboard statistics"""
    user = request.user
    
    # Get current month date range
    current_month_start = timezone.now().date().replace(day=1)
    if current_month_start.month == 12:
        current_month_end = datetime(current_month_start.year + 1, 1, 1).date() - timedelta(days=1)
    else:
        current_month_end = datetime(current_month_start.year, current_month_start.month + 1, 1).date() - timedelta(days=1)
    
    # Filter based on user role
    if user.is_staff or user.is_superuser:
        properties = Property.objects.filter(is_active=True, is_approved=True)
        tenants = User.objects.filter(profile__role='tenant', is_active=True)
        maintenance_requests = MaintenanceRequest.objects.all()
        monthly_payments = Payment.objects.filter(
            status='completed',
            paid_date__range=[current_month_start, current_month_end]
        )
    else:
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                owner_properties = Property.objects.filter(owner=user, is_active=True, is_approved=True)
                properties = owner_properties
                # Owners see tenants for their properties
                from documents.models import Lease
                tenant_ids = Lease.objects.filter(
                    property_ref__in=owner_properties,
                    status='active'
                ).values_list('tenant_id', flat=True).distinct()
                tenants = User.objects.filter(id__in=tenant_ids, is_active=True)
                maintenance_requests = MaintenanceRequest.objects.filter(property__in=owner_properties)
                monthly_payments = Payment.objects.filter(
                    status='completed',
                    property__in=owner_properties,
                    paid_date__range=[current_month_start, current_month_end]
                )
            else:
                # Tenants see limited stats
                properties = Property.objects.none()
                tenants = User.objects.none()
                maintenance_requests = MaintenanceRequest.objects.filter(tenant=user)
                monthly_payments = Payment.objects.filter(
                    status='completed',
                    tenant=user,
                    paid_date__range=[current_month_start, current_month_end]
                )
        except Profile.DoesNotExist:
            properties = Property.objects.none()
            tenants = User.objects.none()
            maintenance_requests = MaintenanceRequest.objects.filter(tenant=user)
            monthly_payments = Payment.objects.filter(
                status='completed',
                tenant=user,
                paid_date__range=[current_month_start, current_month_end]
            )
    
    properties_count = properties.count()
    tenants_count = tenants.count()
    maintenance_requests_count = maintenance_requests.count()
    monthly_revenue = monthly_payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return Response({
        'properties': properties_count,
        'tenants': tenants_count,
        'maintenance_requests': maintenance_requests_count,
        'monthly_revenue': float(monthly_revenue)
    })


@swagger_auto_schema(
    method='get',
    operation_description="Get dashboard chart data including revenue chart, occupancy chart, and maintenance chart",
    operation_summary="Get Dashboard Chart Data",
    tags=['Reports'],
    responses={
        200: openapi.Response(
            description="Dashboard chart data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'revenue_chart': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'occupancy_chart': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                    'maintenance_chart': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                }
            )
        ),
        401: "Authentication required"
    },
    security=[{'Bearer': []}]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def DashboardChartsView(request):
    """Get dashboard chart data"""
    user = request.user
    
    # Filter based on user role
    if user.is_staff or user.is_superuser:
        payments = Payment.objects.filter(status='completed')
        properties = Property.objects.filter(is_active=True, is_approved=True)
        maintenance_requests = MaintenanceRequest.objects.all()
    else:
        from accounts.models import Profile
        try:
            profile = user.profile
            if profile.role == 'owner':
                owner_properties = Property.objects.filter(owner=user, is_active=True, is_approved=True)
                payments = Payment.objects.filter(status='completed', property__in=owner_properties)
                properties = owner_properties
                maintenance_requests = MaintenanceRequest.objects.filter(property__in=owner_properties)
            else:
                payments = Payment.objects.filter(status='completed', tenant=user)
                properties = Property.objects.none()
                maintenance_requests = MaintenanceRequest.objects.filter(tenant=user)
        except Profile.DoesNotExist:
            payments = Payment.objects.filter(status='completed', tenant=user)
            properties = Property.objects.none()
            maintenance_requests = MaintenanceRequest.objects.filter(tenant=user)
    
    # Revenue chart (last 12 months)
    revenue_chart = []
    current_date = timezone.now().date()
    for i in range(11, -1, -1):  # Last 12 months
        month_start = (current_date - timedelta(days=30*i)).replace(day=1)
        if month_start.month == 12:
            month_end = datetime(month_start.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(month_start.year, month_start.month + 1, 1).date() - timedelta(days=1)
        
        month_revenue = payments.filter(
            paid_date__range=[month_start, month_end]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        revenue_chart.append({
            'month': month_start.strftime('%Y-%m'),
            'revenue': float(month_revenue)
        })
    
    # Occupancy chart (last 12 months)
    occupancy_chart = []
    for i in range(11, -1, -1):
        month_start = (current_date - timedelta(days=30*i)).replace(day=1)
        if month_start.month == 12:
            month_end = datetime(month_start.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(month_start.year, month_start.month + 1, 1).date() - timedelta(days=1)
        
        from documents.models import Lease, Booking
        total_props = properties.count()
        occupied_props = properties.filter(
            Q(leases__status='active', leases__start_date__lte=month_end, leases__end_date__gte=month_start) |
            Q(property_bookings__booking_status__in=['confirmed', 'checked_in'],
              property_bookings__check_in_date__lte=month_end,
              property_bookings__check_out_date__gte=month_start)
        ).distinct().count()
        
        occupancy_rate = (occupied_props / total_props * 100) if total_props > 0 else 0.0
        
        occupancy_chart.append({
            'month': month_start.strftime('%Y-%m'),
            'occupancy_rate': round(occupancy_rate, 2),
            'occupied': occupied_props,
            'total': total_props
        })
    
    # Maintenance chart (last 12 months by status)
    maintenance_chart = []
    for i in range(11, -1, -1):
        month_start = (current_date - timedelta(days=30*i)).replace(day=1)
        if month_start.month == 12:
            month_end = datetime(month_start.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(month_start.year, month_start.month + 1, 1).date() - timedelta(days=1)
        
        month_requests = maintenance_requests.filter(created_at__date__range=[month_start, month_end])
        
        maintenance_chart.append({
            'month': month_start.strftime('%Y-%m'),
            'total': month_requests.count(),
            'completed': month_requests.filter(status='completed').count(),
            'pending': month_requests.filter(status='pending').count(),
            'in_progress': month_requests.filter(status='in_progress').count()
        })
    
    return Response({
        'revenue_chart': revenue_chart,
        'occupancy_chart': occupancy_chart,
        'maintenance_chart': maintenance_chart
    })