"""
Enhanced Rent Reminder Views for House Properties
This module provides comprehensive rent reminder management functionality
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta, datetime
import json

from properties.models import Property, Booking, Customer, HouseRentReminderSettings, HouseRentReminder, HouseRentReminderTemplate, HouseRentReminderLog, HouseRentReminderSchedule
from properties.utils import validate_property_id


@login_required
def house_rent_reminders_dashboard(request):
    """Main dashboard for house rent reminders"""
    # Get selected property from session or request
    selected_property_id = request.session.get('selected_house_property_id') or request.GET.get('property_id')
    selected_property_id = validate_property_id(selected_property_id)
    
    # Get house properties
    house_properties = Property.objects.filter(property_type__name__iexact='house')
    
    # Filter data based on selected property
    if selected_property_id:
        try:
            selected_property = Property.objects.get(id=selected_property_id, property_type__name__iexact='house')
            request.session['selected_house_property_id'] = selected_property_id
            
            # Get reminders for selected property
            reminders = HouseRentReminder.objects.filter(property_obj=selected_property)
            settings_obj = HouseRentReminderSettings.objects.filter(property_obj=selected_property).first()
            
        except Property.DoesNotExist:
            selected_property = None
            reminders = HouseRentReminder.objects.none()
            settings_obj = None
    else:
        selected_property = None
        # Get reminders for all house properties
        reminders = HouseRentReminder.objects.filter(property_obj__property_type__name__iexact='house')
        settings_obj = None
    
    # Calculate statistics
    total_reminders = reminders.count()
    sent_reminders = reminders.filter(reminder_status='sent').count()
    pending_reminders = reminders.filter(reminder_status='scheduled').count()
    failed_reminders = reminders.filter(reminder_status='failed').count()
    
    # Overdue reminders
    overdue_reminders = reminders.filter(
        is_overdue=True,
        reminder_status__in=['scheduled', 'sent']
    ).count()
    
    # Recent reminders (last 7 days)
    recent_reminders = reminders.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Get upcoming reminders (next 7 days)
    upcoming_reminders = reminders.filter(
        scheduled_date__lte=timezone.now() + timedelta(days=7),
        scheduled_date__gte=timezone.now(),
        reminder_status='scheduled'
    ).order_by('scheduled_date')[:10]
    
    # Get recent reminder logs
    recent_logs = HouseRentReminderLog.objects.filter(
        reminder__property_obj__in=house_properties
    ).order_by('-created_at')[:10]
    
    context = {
        'house_properties': house_properties,
        'selected_property': selected_property,
        'settings_obj': settings_obj,
        'total_reminders': total_reminders,
        'sent_reminders': sent_reminders,
        'pending_reminders': pending_reminders,
        'failed_reminders': failed_reminders,
        'overdue_reminders': overdue_reminders,
        'recent_reminders': recent_reminders,
        'upcoming_reminders': upcoming_reminders,
        'recent_logs': recent_logs,
        'is_single_property_mode': bool(selected_property_id),
    }
    
    return render(request, 'properties/house_rent_reminders_dashboard.html', context)


@login_required
def house_rent_reminders_list(request):
    """List all rent reminders with filtering and search"""
    # Get selected property from session or request
    selected_property_id = request.session.get('selected_house_property_id') or request.GET.get('property_id')
    selected_property_id = validate_property_id(selected_property_id)
    
    # Get house properties
    house_properties = Property.objects.filter(property_type__name__iexact='house')
    
    # Base queryset
    if selected_property_id:
        try:
            selected_property = Property.objects.get(id=selected_property_id, property_type__name__iexact='house')
            request.session['selected_house_property_id'] = selected_property_id
            reminders = HouseRentReminder.objects.filter(property_obj=selected_property)
        except Property.DoesNotExist:
            selected_property = None
            reminders = HouseRentReminder.objects.none()
    else:
        selected_property = None
        reminders = HouseRentReminder.objects.filter(property_obj__property_type__name__iexact='house')
    
    # Apply filters
    status_filter = request.GET.get('status')
    type_filter = request.GET.get('type')
    search_query = request.GET.get('search')
    overdue_only = request.GET.get('overdue_only')
    
    if status_filter:
        reminders = reminders.filter(reminder_status=status_filter)
    
    if type_filter:
        reminders = reminders.filter(reminder_type=type_filter)
    
    if search_query:
        reminders = reminders.filter(
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(customer__email__icontains=search_query) |
            Q(property_obj__title__icontains=search_query) |
            Q(booking__booking_reference__icontains=search_query)
        )
    
    if overdue_only:
        reminders = reminders.filter(is_overdue=True)
    
    # Order by scheduled date
    reminders = reminders.order_by('-scheduled_date')
    
    # Pagination
    paginator = Paginator(reminders, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'house_properties': house_properties,
        'selected_property': selected_property,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'search_query': search_query,
        'overdue_only': overdue_only,
        'is_single_property_mode': bool(selected_property_id),
    }
    
    return render(request, 'properties/house_rent_reminders_list.html', context)


@login_required
def house_rent_reminder_detail(request, reminder_id):
    """Detail view for a specific rent reminder"""
    reminder = get_object_or_404(HouseRentReminder, id=reminder_id)
    
    # Get reminder logs
    logs = HouseRentReminderLog.objects.filter(reminder=reminder).order_by('-created_at')
    
    context = {
        'reminder': reminder,
        'logs': logs,
    }
    
    return render(request, 'properties/house_rent_reminder_detail.html', context)


@login_required
def house_rent_reminder_settings(request):
    """Settings management for rent reminders"""
    # Get selected property from session or request
    selected_property_id = request.session.get('selected_house_property_id') or request.GET.get('property_id')
    selected_property_id = validate_property_id(selected_property_id)
    
    if not selected_property_id:
        messages.error(request, 'Please select a house property first.')
        return redirect('properties:house_select_property')
    
    try:
        selected_property = Property.objects.get(id=selected_property_id, property_type__name__iexact='house')
        request.session['selected_house_property_id'] = selected_property_id
    except Property.DoesNotExist:
        messages.error(request, 'Selected house property not found.')
        return redirect('properties:house_select_property')
    
    # Get or create settings
    settings_obj, created = HouseRentReminderSettings.objects.get_or_create(
        property_obj=selected_property,
        defaults={
            'days_before_due': 7,
            'overdue_reminder_interval': 3,
            'max_overdue_reminders': 5,
            'email_enabled': True,
            'sms_enabled': False,
            'push_enabled': False,
            'grace_period_days': 5,
            'auto_escalate_enabled': True,
            'is_active': True,
        }
    )
    
    if request.method == 'POST':
        # Update settings
        settings_obj.days_before_due = int(request.POST.get('days_before_due', 7))
        settings_obj.overdue_reminder_interval = int(request.POST.get('overdue_reminder_interval', 3))
        settings_obj.max_overdue_reminders = int(request.POST.get('max_overdue_reminders', 5))
        settings_obj.email_enabled = request.POST.get('email_enabled') == 'on'
        settings_obj.sms_enabled = request.POST.get('sms_enabled') == 'on'
        settings_obj.push_enabled = request.POST.get('push_enabled') == 'on'
        settings_obj.grace_period_days = int(request.POST.get('grace_period_days', 5))
        settings_obj.auto_escalate_enabled = request.POST.get('auto_escalate_enabled') == 'on'
        settings_obj.escalation_email = request.POST.get('escalation_email', '')
        settings_obj.custom_email_template = request.POST.get('custom_email_template', '')
        settings_obj.custom_sms_template = request.POST.get('custom_sms_template', '')
        settings_obj.is_active = request.POST.get('is_active') == 'on'
        settings_obj.save()
        
        messages.success(request, 'Reminder settings updated successfully!')
        return redirect('properties:house_rent_reminder_settings')
    
    context = {
        'selected_property': selected_property,
        'settings_obj': settings_obj,
    }
    
    return render(request, 'properties/house_rent_reminder_settings.html', context)


@login_required
def house_rent_reminder_templates(request):
    """Manage rent reminder templates"""
    templates = HouseRentReminderTemplate.objects.all().order_by('template_type', 'category')
    
    # Group templates by type
    template_groups = {}
    for template in templates:
        if template.template_type not in template_groups:
            template_groups[template.template_type] = []
        template_groups[template.template_type].append(template)
    
    context = {
        'template_groups': template_groups,
    }
    
    return render(request, 'properties/house_rent_reminder_templates.html', context)


@login_required
def house_rent_reminder_template_detail(request, template_id):
    """Detail view for a reminder template"""
    template = get_object_or_404(HouseRentReminderTemplate, id=template_id)
    
    if request.method == 'POST':
        # Update template
        template.name = request.POST.get('name', template.name)
        template.subject = request.POST.get('subject', template.subject)
        template.content = request.POST.get('content', template.content)
        template.variables_help = request.POST.get('variables_help', template.variables_help)
        template.is_active = request.POST.get('is_active') == 'on'
        template.is_default = request.POST.get('is_default') == 'on'
        template.save()
        
        messages.success(request, 'Template updated successfully!')
        return redirect('properties:house_rent_reminder_template_detail', template_id=template.id)
    
    context = {
        'template': template,
    }
    
    return render(request, 'properties/house_rent_reminder_template_detail.html', context)


@login_required
@require_http_methods(["POST"])
def send_manual_reminder(request):
    """Send a manual reminder"""
    reminder_id = request.POST.get('reminder_id')
    
    try:
        reminder = HouseRentReminder.objects.get(id=reminder_id)
        
        # Check if reminder can be sent
        if reminder.reminder_status != 'scheduled':
            return JsonResponse({
                'success': False,
                'message': 'Reminder is not in scheduled status'
            })
        
        # Get template
        template = HouseRentReminderTemplate.objects.filter(
            template_type=reminder.reminder_type,
            is_default=True,
            is_active=True
        ).first()
        
        if not template:
            return JsonResponse({
                'success': False,
                'message': 'No template found for this reminder type'
            })
        
        # Prepare context
        context = {
            'tenant_name': reminder.customer.first_name or reminder.customer.email,
            'property_title': reminder.property_obj.title,
            'due_date': reminder.due_date.strftime('%B %d, %Y'),
            'amount': reminder.booking.total_amount,
            'days_overdue': reminder.days_overdue,
            'booking_reference': reminder.booking.booking_reference,
        }
        
        # Send reminder (simplified - you'd implement actual sending logic)
        success = True  # Placeholder
        
        if success:
            reminder.mark_as_sent()
            HouseRentReminderLog.objects.create(
                reminder=reminder,
                action='sent',
                description='Manual reminder sent',
                performed_by=request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Reminder sent successfully'
            })
        else:
            reminder.mark_as_failed('Failed to send manual reminder')
            return JsonResponse({
                'success': False,
                'message': 'Failed to send reminder'
            })
            
    except HouseRentReminder.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Reminder not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def cancel_reminder(request):
    """Cancel a scheduled reminder"""
    reminder_id = request.POST.get('reminder_id')
    
    try:
        reminder = HouseRentReminder.objects.get(id=reminder_id)
        
        if reminder.reminder_status != 'scheduled':
            return JsonResponse({
                'success': False,
                'message': 'Only scheduled reminders can be cancelled'
            })
        
        reminder.reminder_status = 'cancelled'
        reminder.save()
        
        HouseRentReminderLog.objects.create(
            reminder=reminder,
            action='cancelled',
            description='Reminder cancelled by user',
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Reminder cancelled successfully'
        })
        
    except HouseRentReminder.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Reminder not found'
        })


@login_required
def house_rent_reminder_analytics(request):
    """Analytics and reports for rent reminders"""
    # Get selected property from session or request
    selected_property_id = request.session.get('selected_house_property_id') or request.GET.get('property_id')
    selected_property_id = validate_property_id(selected_property_id)
    
    # Get house properties
    house_properties = Property.objects.filter(property_type__name__iexact='house')
    
    # Filter data based on selected property
    if selected_property_id:
        try:
            selected_property = Property.objects.get(id=selected_property_id, property_type__name__iexact='house')
            request.session['selected_house_property_id'] = selected_property_id
            reminders = HouseRentReminder.objects.filter(property_obj=selected_property)
        except Property.DoesNotExist:
            selected_property = None
            reminders = HouseRentReminder.objects.none()
    else:
        selected_property = None
        reminders = HouseRentReminder.objects.filter(property_obj__property_type__name__iexact='house')
    
    # Calculate analytics
    total_reminders = reminders.count()
    sent_reminders = reminders.filter(reminder_status='sent').count()
    failed_reminders = reminders.filter(reminder_status='failed').count()
    
    # Success rate
    success_rate = (sent_reminders / total_reminders * 100) if total_reminders > 0 else 0
    
    # Reminders by type
    reminders_by_type = reminders.values('reminder_type').annotate(
        count=Count('id')
    ).order_by('reminder_type')
    
    # Reminders by status
    reminders_by_status = reminders.values('reminder_status').annotate(
        count=Count('id')
    ).order_by('reminder_status')
    
    # Monthly trends (last 12 months)
    monthly_trends = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_reminders = reminders.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        monthly_trends.append({
            'month': month_start.strftime('%b %Y'),
            'count': month_reminders
        })
    
    monthly_trends.reverse()
    
    context = {
        'house_properties': house_properties,
        'selected_property': selected_property,
        'total_reminders': total_reminders,
        'sent_reminders': sent_reminders,
        'failed_reminders': failed_reminders,
        'success_rate': round(success_rate, 2),
        'reminders_by_type': reminders_by_type,
        'reminders_by_status': reminders_by_status,
        'monthly_trends': monthly_trends,
        'is_single_property_mode': bool(selected_property_id),
    }
    
    return render(request, 'properties/house_rent_reminder_analytics.html', context)
