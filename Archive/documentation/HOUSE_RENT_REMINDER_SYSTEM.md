# 🏠 Automated Rent Reminder System for House Properties

## Overview

The Automated Rent Reminder System is a comprehensive solution designed to streamline rent collection for house properties in the Maisha backend system. It provides automated, customizable, and intelligent rent payment reminders through multiple channels (email, SMS, push notifications) with advanced scheduling, template management, and analytics capabilities.

## 🚀 Key Features

### 1. **Automated Scheduling**
- **Flexible Timing**: Configure reminders to be sent X days before due date
- **Overdue Management**: Automatic escalation with configurable intervals
- **Multiple Channels**: Email, SMS, and push notification support
- **Grace Periods**: Configurable grace periods before late fees apply

### 2. **Smart Template System**
- **Dynamic Templates**: Use variables like `{{tenant_name}}`, `{{property_title}}`, `{{amount}}`
- **Multiple Categories**: Upcoming, overdue, final notice, escalation templates
- **Custom Messages**: Override default templates with custom content
- **Multi-language Support**: Templates can be localized

### 3. **Advanced Analytics**
- **Success Rates**: Track reminder delivery and response rates
- **Trend Analysis**: Monthly and yearly reminder statistics
- **Channel Performance**: Compare effectiveness of different reminder types
- **Overdue Tracking**: Monitor and analyze overdue payment patterns

### 4. **Comprehensive Management**
- **Dashboard**: Real-time overview of all reminder activities
- **Manual Override**: Send manual reminders when needed
- **Bulk Operations**: Send reminders to multiple tenants at once
- **Escalation Management**: Automatic escalation to property managers

## 📋 System Architecture

### Models

#### 1. `HouseRentReminderSettings`
Configuration settings for each property's reminder system.

```python
class HouseRentReminderSettings(models.Model):
    property_obj = models.ForeignKey(Property, ...)
    days_before_due = models.IntegerField(default=7)
    overdue_reminder_interval = models.IntegerField(default=3)
    max_overdue_reminders = models.IntegerField(default=5)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    grace_period_days = models.IntegerField(default=5)
    auto_escalate_enabled = models.BooleanField(default=True)
    escalation_email = models.EmailField(blank=True)
```

#### 2. `HouseRentReminder`
Individual reminder records with full tracking.

```python
class HouseRentReminder(models.Model):
    booking = models.ForeignKey(Booking, ...)
    customer = models.ForeignKey(Customer, ...)
    property_obj = models.ForeignKey(Property, ...)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    reminder_status = models.CharField(max_length=20, choices=REMINDER_STATUS_CHOICES)
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    reminder_sequence = models.IntegerField(default=1)
    is_overdue = models.BooleanField(default=False)
```

#### 3. `HouseRentReminderTemplate`
Email and SMS templates with variable support.

```python
class HouseRentReminderTemplate(models.Model):
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=REMINDER_CATEGORY_CHOICES)
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    is_default = models.BooleanField(default=False)
```

#### 4. `HouseRentReminderLog`
Detailed activity logging for audit trails.

```python
class HouseRentReminderLog(models.Model):
    reminder = models.ForeignKey(HouseRentReminder, ...)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    performed_by = models.ForeignKey(User, ...)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Views

#### 1. Dashboard Views
- `house_rent_reminders_dashboard`: Main dashboard with statistics and quick actions
- `house_rent_reminders_list`: Comprehensive list view with filtering
- `house_rent_reminder_detail`: Detailed view of individual reminders

#### 2. Management Views
- `house_rent_reminder_settings`: Configure reminder settings per property
- `house_rent_reminder_templates`: Manage email/SMS templates
- `house_rent_reminder_analytics`: Analytics and reporting

#### 3. Action Views
- `send_manual_reminder`: Send manual reminders
- `cancel_reminder`: Cancel scheduled reminders

### Management Commands

#### `send_house_rent_reminders`
Comprehensive management command for automated reminder processing.

```bash
# Basic usage
python manage.py send_house_rent_reminders

# Dry run (preview without sending)
python manage.py send_house_rent_reminders --dry-run

# Specific property
python manage.py send_house_rent_reminders --property-id 1

# Specific reminder type
python manage.py send_house_rent_reminders --reminder-type email

# Create default templates
python manage.py send_house_rent_reminders --create-templates

# Create default schedules
python manage.py send_house_rent_reminders --create-schedules
```

## 🛠 Setup and Configuration

### 1. **Initial Setup**

```bash
# Run migrations (when models are added to main models.py)
python manage.py makemigrations properties
python manage.py migrate

# Create default templates
python manage.py send_house_rent_reminders --create-templates

# Create default schedules
python manage.py send_house_rent_reminders --create-schedules
```

### 2. **Email Configuration**

Add to your Django settings:

```python
# Email settings for reminders
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'Property Management <noreply@yourdomain.com>'
```

### 3. **SMS Configuration**

Implement SMS service integration:

```python
# In the management command, implement actual SMS sending
def send_sms_reminder(self, reminder, template, context):
    # Integrate with your SMS service (Twilio, AWS SNS, etc.)
    phone_number = reminder.customer.phone
    message = template.render_template(context)
    
    # Example with Twilio
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(
    #     body=message,
    #     from_='+1234567890',
    #     to=phone_number
    # )
    
    return True
```

### 4. **Cron Job Setup**

Set up automated execution:

```bash
# Add to crontab for daily execution at 9 AM
0 9 * * * cd /path/to/your/project && python manage.py send_house_rent_reminders

# Or for more frequent execution (every 6 hours)
0 */6 * * * cd /path/to/your/project && python manage.py send_house_rent_reminders
```

## 📊 Usage Examples

### 1. **Basic Configuration**

```python
# Configure reminder settings for a property
settings = HouseRentReminderSettings.objects.create(
    property_obj=house_property,
    days_before_due=7,
    overdue_reminder_interval=3,
    max_overdue_reminders=5,
    email_enabled=True,
    sms_enabled=False,
    grace_period_days=5,
    auto_escalate_enabled=True,
    escalation_email='manager@company.com'
)
```

### 2. **Custom Template Creation**

```python
# Create custom email template
template = HouseRentReminderTemplate.objects.create(
    name='Custom Upcoming Payment',
    template_type='email',
    category='upcoming',
    subject='Rent Due Soon - {{property_title}}',
    content='''
Dear {{tenant_name}},

Your rent payment of TZS {{amount:,.0f}} for {{property_title}} 
is due on {{due_date}}.

Please ensure payment is made on time to avoid late fees.

Best regards,
Property Management Team
    ''',
    is_default=True
)
```

### 3. **Manual Reminder Sending**

```python
# Send manual reminder
reminder = HouseRentReminder.objects.create(
    booking=booking,
    customer=customer,
    property_obj=property_obj,
    reminder_type='email',
    scheduled_date=timezone.now(),
    due_date=due_date,
    days_before_due=7,
    subject='Manual Rent Reminder',
    message_content='Custom reminder message',
    reminder_sequence=1,
    is_overdue=False
)

# Process the reminder
if reminder.is_due_for_sending:
    success = send_reminder_notification(reminder, template, context)
    if success:
        reminder.mark_as_sent()
    else:
        reminder.mark_as_failed('Failed to send')
```

## 📈 Analytics and Reporting

### 1. **Dashboard Statistics**

The dashboard provides real-time statistics:
- Total reminders sent
- Success/failure rates
- Overdue reminders count
- Recent activity logs
- Upcoming reminders

### 2. **Analytics Views**

Access detailed analytics at:
- `/properties/house/rent-reminders/analytics/`

Features:
- Monthly trend analysis
- Channel performance comparison
- Success rate tracking
- Overdue pattern analysis

### 3. **Custom Reports**

Generate custom reports using the analytics data:

```python
# Example analytics query
from django.db.models import Count, Avg
from datetime import timedelta

# Monthly reminder trends
monthly_trends = HouseRentReminder.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=365)
).extra(
    select={'month': "DATE_TRUNC('month', created_at)"}
).values('month').annotate(
    total=Count('id'),
    sent=Count('id', filter=Q(reminder_status='sent')),
    failed=Count('id', filter=Q(reminder_status='failed'))
).order_by('month')
```

## 🔧 Advanced Features

### 1. **Escalation Management**

When max reminders are reached, automatic escalation occurs:

```python
# Check if escalation is needed
if reminder_count >= settings.max_overdue_reminders:
    if settings.auto_escalate_enabled:
        # Send escalation email to manager
        send_escalation_notification(settings.escalation_email, reminder)
```

### 2. **Template Variables**

Available template variables:
- `{{tenant_name}}` - Tenant's full name
- `{{property_title}}` - Property title
- `{{due_date}}` - Payment due date
- `{{amount}}` - Rent amount
- `{{days_overdue}}` - Days overdue (for overdue reminders)
- `{{late_fee}}` - Late fee amount
- `{{booking_reference}}` - Booking reference number
- `{{payment_method}}` - Preferred payment method

### 3. **Bulk Operations**

Send reminders to multiple tenants:

```python
# Bulk reminder for all overdue tenants
overdue_bookings = Booking.objects.filter(
    property_obj__property_type__name__iexact='house',
    payment_status__in=['pending', 'partial'],
    check_in_date__lt=timezone.now().date() - timedelta(days=30)
)

for booking in overdue_bookings:
    create_overdue_reminder(booking)
```

## 🚨 Troubleshooting

### Common Issues

1. **Reminders not sending**
   - Check email configuration
   - Verify reminder settings are active
   - Check cron job execution

2. **Templates not rendering**
   - Verify template variables are correct
   - Check template syntax
   - Test with simple templates first

3. **Analytics not updating**
   - Ensure reminders are being marked as sent/failed
   - Check log entries are being created
   - Verify database queries

### Debug Mode

Enable debug mode in management command:

```bash
python manage.py send_house_rent_reminders --dry-run --verbose
```

## 🔒 Security Considerations

1. **Email Security**
   - Use secure SMTP connections
   - Implement rate limiting
   - Validate email addresses

2. **Data Privacy**
   - Encrypt sensitive tenant data
   - Implement access controls
   - Regular security audits

3. **Template Security**
   - Sanitize template variables
   - Prevent template injection
   - Validate template content

## 📚 API Integration

The system can be integrated with external services:

### 1. **Payment Gateways**
- Integrate with payment processors
- Update reminder status on payment
- Send payment confirmations

### 2. **Communication Services**
- Twilio for SMS
- SendGrid for email
- Firebase for push notifications

### 3. **Analytics Platforms**
- Google Analytics
- Custom dashboards
- Business intelligence tools

## 🎯 Future Enhancements

1. **AI-Powered Reminders**
   - Machine learning for optimal timing
   - Personalized message content
   - Predictive analytics

2. **Multi-language Support**
   - Automatic language detection
   - Localized templates
   - Cultural customization

3. **Mobile App Integration**
   - Push notifications
   - In-app reminders
   - Payment integration

4. **Advanced Scheduling**
   - Tenant preference learning
   - Optimal send time calculation
   - Frequency optimization

## 📞 Support

For technical support or feature requests:
- Create an issue in the project repository
- Contact the development team
- Check the documentation wiki

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Compatibility**: Django 4.0+, Python 3.8+
