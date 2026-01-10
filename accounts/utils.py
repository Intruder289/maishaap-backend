from django.contrib.auth.models import User
from .models import ActivityLog
from decimal import Decimal


def log_activity(user, action, description, content_type=None, object_id=None, 
                priority='medium', amount=None, metadata=None):
    """
    Utility function to log user activities
    
    Args:
        user: User instance
        action: Action type (from ActivityLog.ACTION_CHOICES)
        description: Human-readable description
        content_type: Type of object (Property, Payment, etc.)
        object_id: ID of the related object
        priority: Priority level (low, medium, high, urgent)
        amount: Amount in TZS
        metadata: Additional data as dictionary
    """
    if metadata is None:
        metadata = {}
    
    # Convert amount to Decimal if provided
    if amount is not None:
        amount = Decimal(str(amount))
    
    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        content_type=content_type or '',
        object_id=object_id,
        priority=priority,
        amount=amount,
        metadata=metadata
    )


def get_recent_activities(user=None, limit=10, days=7):
    """
    Get recent activities for dashboard display
    
    Args:
        user: User instance (if None, gets all activities for staff)
        limit: Number of activities to return
        days: Number of days to look back
    """
    from django.utils import timezone
    from datetime import timedelta
    
    since = timezone.now() - timedelta(days=days)
    
    activities = ActivityLog.objects.filter(timestamp__gte=since)
    
    if user and not (user.is_staff or user.is_superuser):
        # Regular users see only their activities
        activities = activities.filter(user=user)
    
    return activities.select_related('user')[:limit]


def get_dashboard_stats(user):
    """
    Get dynamic dashboard statistics with comprehensive real-time data
    Respects navigation permissions - only shows stats for sections user has access to
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Sum, Q
    from accounts.context_processors import user_has_navigation_permission
    
    # Base stats structure
    stats = {
        'total_properties': 0,
        'active_tenants': 0,
        'monthly_revenue': Decimal('0.00'),
        'unpaid_invoices': 0,
        'active_leases': 0,
        'pending_bookings': 0,
        'recent_complaints': 0,
        'maintenance_requests': 0,
        'total_users': 0,
        'available_properties': 0,
        'rented_properties': 0,
        'overdue_payments': 0,
    }
    
    # Get current month start and other time periods
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Check if user has permission to view properties
    # For admin/staff users, always show stats regardless of navigation permissions
    # This ensures superusers and staff can always see dashboard stats
    has_property_permission = (user.is_superuser or 
                              user.is_staff or
                              user_has_navigation_permission(user, 'property_list') or
                              user_has_navigation_permission(user, 'properties') or
                              user_has_navigation_permission(user, 'manage_properties'))
    
    try:
        # Properties count and status breakdown
        from properties.models import Property
        if has_property_permission:
            if user.is_staff or user.is_superuser:
                # Admin/staff: count all properties (excluding unavailable)
                # Use distinct() to avoid any duplicate counting issues
                all_properties = Property.objects.exclude(status='unavailable')
                stats['total_properties'] = all_properties.count()
                stats['available_properties'] = Property.objects.filter(status='available').count()
                stats['rented_properties'] = Property.objects.filter(status='rented').count()
            else:
                # Property owner: only count their own properties
                owner_properties = Property.objects.filter(owner=user).exclude(status='unavailable')
                stats['total_properties'] = owner_properties.count()
                stats['available_properties'] = Property.objects.filter(owner=user, status='available').count()
                stats['rented_properties'] = Property.objects.filter(owner=user, status='rented').count()
        else:
            # Even without explicit permission, if user is staff/superuser, show stats
            # This is a fallback to ensure admins always see stats
            if user.is_staff or user.is_superuser:
                all_properties = Property.objects.exclude(status='unavailable')
                stats['total_properties'] = all_properties.count()
                stats['available_properties'] = Property.objects.filter(status='available').count()
                stats['rented_properties'] = Property.objects.filter(status='rented').count()
    except ImportError:
        pass
    except Exception as e:
        # Log error but don't break dashboard
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error calculating property stats: {str(e)}")
        pass
    
    # Check permissions for different sections
    has_tenant_permission = (user.is_superuser or 
                            user_has_navigation_permission(user, 'house_tenants') or
                            has_property_permission)
    
    has_payment_permission = (user.is_superuser or 
                             user_has_navigation_permission(user, 'house_payments') or
                             user_has_navigation_permission(user, 'hotel_payments') or
                             user_has_navigation_permission(user, 'lodge_payments') or
                             user_has_navigation_permission(user, 'venue_payments'))
    
    has_booking_permission = (user.is_superuser or 
                             user_has_navigation_permission(user, 'house_bookings') or
                             user_has_navigation_permission(user, 'hotel_bookings') or
                             user_has_navigation_permission(user, 'lodge_bookings') or
                             user_has_navigation_permission(user, 'venue_bookings'))
    
    has_complaint_permission = (user.is_superuser or 
                               user_has_navigation_permission(user, 'complaint_list') or
                               user_has_navigation_permission(user, 'complaints'))
    
    has_maintenance_permission = (user.is_superuser or 
                                  user_has_navigation_permission(user, 'request_list') or
                                  user_has_navigation_permission(user, 'maintenance'))
    
    has_user_management_permission = (user.is_superuser or 
                                      user_has_navigation_permission(user, 'user_list') or
                                      user_has_navigation_permission(user, 'user_management'))
    
    try:
        # Active tenants (users with active leases)
        if has_tenant_permission:
            from documents.models import Lease
            if user.is_staff or user.is_superuser:
                stats['active_tenants'] = Lease.objects.filter(status='active').values('tenant').distinct().count()
            else:
                stats['active_tenants'] = Lease.objects.filter(property_ref__owner=user, status='active').values('tenant').distinct().count()
    except ImportError:
        pass
    
    try:
        # Monthly revenue from completed payments
        if has_payment_permission:
            from payments.models import Payment
            payments_query = Payment.objects.filter(
                created_at__gte=month_start,
                status='completed'  # Payment model uses 'completed' not 'successful'
            )
            if not (user.is_staff or user.is_superuser):
                # For property owners, filter by their properties
                payments_query = payments_query.filter(
                    Q(booking__property_obj__owner=user) | 
                    Q(rent_invoice__lease__property_ref__owner=user)
                )
            
            revenue = payments_query.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            stats['monthly_revenue'] = revenue
    except ImportError:
        pass
    
    try:
        # Unpaid invoices
        if has_payment_permission:
            from payments.models import Invoice
            invoices_query = Invoice.objects.filter(status='unpaid')
            if not (user.is_staff or user.is_superuser):
                invoices_query = invoices_query.filter(tenant=user)
            stats['unpaid_invoices'] = invoices_query.count()
            
            # Overdue payments (invoices past due date)
            overdue_query = invoices_query.filter(due_date__lt=now.date())
            stats['overdue_payments'] = overdue_query.count()
    except ImportError:
        pass
    
    try:
        # Active leases
        if has_tenant_permission:
            from documents.models import Lease
            leases_query = Lease.objects.filter(status='active')
            if not (user.is_staff or user.is_superuser):
                leases_query = leases_query.filter(property_ref__owner=user)
            stats['active_leases'] = leases_query.count()
    except ImportError:
        pass
    
    try:
        # Pending bookings - check both Booking models
        if has_booking_permission:
            pending_count = 0
            
            # Check documents.Booking model
            try:
                from documents.models import Booking as DocumentBooking
                doc_bookings_query = DocumentBooking.objects.filter(status='pending')
                if not (user.is_staff or user.is_superuser):
                    doc_bookings_query = doc_bookings_query.filter(property_ref__owner=user)
                pending_count += doc_bookings_query.count()
            except ImportError:
                pass
            
            # Check properties.Booking model
            try:
                from properties.models import Booking as PropertyBooking
                prop_bookings_query = PropertyBooking.objects.filter(booking_status='pending')
                if not (user.is_staff or user.is_superuser):
                    prop_bookings_query = prop_bookings_query.filter(property_obj__owner=user)
                pending_count += prop_bookings_query.count()
            except ImportError:
                pass
            
            stats['pending_bookings'] = pending_count
    except Exception:
        pass
    
    try:
        # Recent complaints (last 30 days)
        if has_complaint_permission:
            from complaints.models import Complaint
            complaints_query = Complaint.objects.filter(created_at__gte=month_ago)
            if not (user.is_staff or user.is_superuser):
                complaints_query = complaints_query.filter(user=user)
            stats['recent_complaints'] = complaints_query.count()
    except ImportError:
        pass
    
    try:
        # Maintenance requests (all requests)
        if has_maintenance_permission:
            from maintenance.models import MaintenanceRequest
            maintenance_query = MaintenanceRequest.objects.all()
            if not (user.is_staff or user.is_superuser):
                maintenance_query = maintenance_query.filter(tenant=user)
            stats['maintenance_requests'] = maintenance_query.count()
    except ImportError:
        pass
    
    try:
        # Total users (for admin/staff only)
        if has_user_management_permission:
            from django.contrib.auth.models import User
            stats['total_users'] = User.objects.filter(is_active=True).count()
    except ImportError:
        pass
    
    return stats


def format_currency_tzs(amount):
    """
    Format amount as Tanzania Shillings
    """
    if amount is None:
        return "TZS 0.00"
    
    amount = Decimal(str(amount))
    return f"TZS {amount:,.2f}"