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
# Swagger documentation - using drf-spectacular
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
except ImportError:
    # drf-yasg not installed, use drf-spectacular instead
    from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
    from drf_spectacular.types import OpenApiTypes
    
    # Create a wrapper to convert swagger_auto_schema to extend_schema for drf-spectacular
    def swagger_auto_schema(*args, **kwargs):
        # Handle method parameter - drf-spectacular doesn't need it
        method = kwargs.pop('method', None)
        
        # Extract parameters from manual_parameters if present
        manual_params = kwargs.get('manual_parameters', [])
        spectacular_params = []
        
        if manual_params:
            # Convert drf-yasg parameters to drf-spectacular parameters
            for param in manual_params:
                if param is None:
                    continue
                if callable(param) and not hasattr(param, 'name'):
                    continue
                
                param_name = None
                param_type = OpenApiTypes.STR
                param_location = OpenApiParameter.QUERY
                param_description = ''
                param_required = False
                
                if hasattr(param, 'name') and param.name:
                    param_name = param.name
                    param_description = getattr(param, 'description', '') or ''
                    param_required = getattr(param, 'required', False)
                    
                    param_type_attr = getattr(param, 'type', None)
                    type_str = str(param_type_attr).lower() if param_type_attr else ''
                    
                    if (param_type_attr == openapi.TYPE_INTEGER or 'integer' in type_str):
                        param_type = OpenApiTypes.INT
                    elif (param_type_attr == openapi.TYPE_NUMBER or 'number' in type_str):
                        param_type = OpenApiTypes.NUMBER
                    elif (param_type_attr == openapi.TYPE_BOOLEAN or 'boolean' in type_str):
                        param_type = OpenApiTypes.BOOL
                    else:
                        param_type = OpenApiTypes.STR
                    
                    param_in = getattr(param, 'in_', None)
                    in_str = str(param_in).lower() if param_in else ''
                    
                    if (param_in == openapi.IN_QUERY or 'query' in in_str):
                        param_location = OpenApiParameter.QUERY
                    elif (param_in == openapi.IN_PATH or 'path' in in_str):
                        param_location = OpenApiParameter.PATH
                    else:
                        param_location = OpenApiParameter.QUERY
                    
                    spectacular_params.append(
                        OpenApiParameter(
                            name=param_name,
                            type=param_type,
                            location=param_location,
                            description=param_description,
                            required=param_required
                        )
                    )
        
        # Clean responses to convert serializer instances to classes
        responses = kwargs.get('responses', {})
        cleaned_responses = {}
        if responses:
            for status_code, response_value in responses.items():
                # Handle serializer instances (e.g., Serializer(many=True))
                if hasattr(response_value, '__class__') and 'Serializer' in response_value.__class__.__name__:
                    serializer_class = response_value.__class__
                    many = getattr(response_value, 'many', False)
                    cleaned_responses[status_code] = OpenApiResponse(
                        response=serializer_class,
                        description=f'List of {serializer_class.__name__.replace("Serializer", "").lower()}s' if many else f'{serializer_class.__name__.replace("Serializer", "")} details'
                    )
                # Handle openapi.Response objects with serializer instances
                elif hasattr(response_value, 'schema') and hasattr(response_value.schema, '__class__'):
                    schema_obj = response_value.schema
                    if hasattr(schema_obj, '__class__') and 'Serializer' in schema_obj.__class__.__name__:
                        serializer_class = schema_obj.__class__
                        many = getattr(schema_obj, 'many', False)
                        cleaned_responses[status_code] = OpenApiResponse(
                            response=serializer_class,
                            description=getattr(response_value, 'description', '') or f'{serializer_class.__name__.replace("Serializer", "")} details'
                        )
                    else:
                        cleaned_responses[status_code] = response_value
                # Handle string responses
                elif isinstance(response_value, str):
                    cleaned_responses[status_code] = {'description': response_value}
                # Handle dict responses
                elif isinstance(response_value, dict):
                    cleaned_responses[status_code] = response_value
                # For other types, pass through
                else:
                    cleaned_responses[status_code] = response_value
        
        return extend_schema(
            summary=kwargs.get('operation_summary', ''),
            description=kwargs.get('operation_description', ''),
            tags=kwargs.get('tags', []),
            parameters=spectacular_params if spectacular_params else None,
            responses=cleaned_responses if cleaned_responses else None
        )
    
    class openapi:
        class Response:
            def __init__(self, *args, **kwargs):
                pass
        class Schema:
            def __init__(self, *args, **kwargs):
                pass
        class Items:
            def __init__(self, *args, **kwargs):
                pass
        class Contact:
            def __init__(self, *args, **kwargs):
                pass
        class License:
            def __init__(self, *args, **kwargs):
                pass
        class Info:
            def __init__(self, *args, **kwargs):
                pass
        TYPE_OBJECT = 'object'
        TYPE_STRING = 'string'
        TYPE_INTEGER = 'integer'
        TYPE_NUMBER = 'number'
        TYPE_BOOLEAN = 'boolean'
        TYPE_ARRAY = 'array'
        FORMAT_EMAIL = 'email'
        FORMAT_DATE = 'date'
        FORMAT_DATETIME = 'date-time'
        FORMAT_DECIMAL = 'decimal'
        FORMAT_URI = 'uri'
        FORMAT_UUID = 'uuid'
        IN_QUERY = 'query'
        IN_PATH = 'path'
        IN_BODY = 'body'
        IN_FORM = 'formData'
        IN_HEADER = 'header'
        
        # Create a proper Parameter class that stores arguments
        class Parameter:
            def __init__(self, name, in_, description=None, type=None, required=False, **kwargs):
                self.name = name
                self.in_ = in_
                self.description = description or ''
                self.type = type or 'string'
                self.required = required
                # Store all kwargs for compatibility
                for key, value in kwargs.items():
                    setattr(self, key, value)


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Financial Summary",
    description="Get financial summary for dashboard including total revenue, expenses, net income, rent collected, and pending payments",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Financial summary data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'total_revenue': {'type': 'number'},
                            'total_expenses': {'type': 'number'},
                            'net_income': {'type': 'number'},
                            'rent_collected': {'type': 'number'},
                            'pending_payments': {'type': 'number'}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
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


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Rent Collection Report",
    description="Get rent collection report including collection rate, total collected, pending amount, and overdue amount",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Rent collection report data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'collection_rate': {'type': 'number'},
                            'total_collected': {'type': 'number'},
                            'pending_amount': {'type': 'number'},
                            'overdue_amount': {'type': 'number'}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
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


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Expense Report",
    description="Get expense report including total expenses, breakdown by categories, and monthly trends",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Expense report data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'total_expenses': {'type': 'number'},
                            'categories': {'type': 'array', 'items': {'type': 'object'}},
                            'monthly_trend': {'type': 'array', 'items': {'type': 'object'}}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
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


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Property Occupancy Report",
    description="Get property occupancy report including occupancy rate, occupied units, vacant units, and total units",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Property occupancy report data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'occupancy_rate': {'type': 'number'},
                            'occupied_units': {'type': 'integer'},
                            'vacant_units': {'type': 'integer'},
                            'total_units': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
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


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Maintenance Report",
    description="Get maintenance report including total requests, completed, pending, in progress, and average completion time",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Maintenance report data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'total_requests': {'type': 'integer'},
                            'completed': {'type': 'integer'},
                            'pending': {'type': 'integer'},
                            'in_progress': {'type': 'integer'},
                            'average_completion_time': {'type': 'number'},
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
)
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


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Dashboard Statistics",
    description="Get dashboard statistics including properties count, tenants count, maintenance requests, and monthly revenue",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Dashboard statistics',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'properties': {'type': 'integer'},
                            'tenants': {'type': 'integer'},
                            'maintenance_requests': {'type': 'integer'},
                            'monthly_revenue': {'type': 'number'}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
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


# CRITICAL: @extend_schema must be BEFORE @api_view for drf-spectacular
@extend_schema(
    summary="Get Dashboard Chart Data",
    description="Get dashboard chart data including revenue chart, occupancy chart, and maintenance chart",
    tags=['Reports'],
    responses={
        200: {
            'description': 'Dashboard chart data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'revenue_chart': {'type': 'array', 'items': {'type': 'object'}},
                            'occupancy_chart': {'type': 'array', 'items': {'type': 'object'}},
                            'maintenance_chart': {'type': 'array', 'items': {'type': 'object'}}
                        }
                    }
                }
            }
        },
        401: {'description': 'Authentication required'}
    }
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