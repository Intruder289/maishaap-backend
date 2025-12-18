"""
Forms for House Rent Reminder System
"""

from django import forms
from django.contrib.auth.models import User
from properties.models import Property, Booking, Customer, HouseRentReminderSettings, HouseRentReminder, HouseRentReminderTemplate, HouseRentReminderSchedule


class HouseRentReminderSettingsForm(forms.ModelForm):
    """Form for managing rent reminder settings"""
    
    class Meta:
        model = HouseRentReminderSettings
        fields = [
            'days_before_due', 'overdue_reminder_interval', 'max_overdue_reminders',
            'email_enabled', 'sms_enabled', 'push_enabled',
            'grace_period_days', 'auto_escalate_enabled', 'escalation_email',
            'custom_email_template', 'custom_sms_template', 'is_active'
        ]
        
        widgets = {
            'days_before_due': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30',
                'help_text': 'Days before due date to send first reminder'
            }),
            'overdue_reminder_interval': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30',
                'help_text': 'Days between overdue reminders'
            }),
            'max_overdue_reminders': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
                'help_text': 'Maximum number of overdue reminders'
            }),
            'grace_period_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '30',
                'help_text': 'Grace period before late fees apply'
            }),
            'escalation_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'manager@example.com'
            }),
            'custom_email_template': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '8',
                'placeholder': 'Custom email template (optional)'
            }),
            'custom_sms_template': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Custom SMS template (optional)'
            }),
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_escalate_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'days_before_due': 'How many days before the due date should the first reminder be sent?',
            'overdue_reminder_interval': 'How many days should pass between overdue reminders?',
            'max_overdue_reminders': 'Maximum number of overdue reminders to send before escalation',
            'grace_period_days': 'Grace period in days before late fees are applied',
            'escalation_email': 'Email address to notify when reminders are escalated',
            'custom_email_template': 'Custom email template. Use variables like {{tenant_name}}, {{property_title}}, {{due_date}}, {{amount}}',
            'custom_sms_template': 'Custom SMS template. Keep it short and use variables like {{tenant_name}}, {{amount}}, {{due_date}}',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that max_overdue_reminders is reasonable
        max_reminders = cleaned_data.get('max_overdue_reminders')
        if max_reminders and max_reminders > 20:
            raise forms.ValidationError("Maximum overdue reminders cannot exceed 20.")
        
        # Validate escalation email if auto-escalate is enabled
        auto_escalate = cleaned_data.get('auto_escalate_enabled')
        escalation_email = cleaned_data.get('escalation_email')
        
        if auto_escalate and not escalation_email:
            raise forms.ValidationError("Escalation email is required when auto-escalation is enabled.")
        
        return cleaned_data


class HouseRentReminderTemplateForm(forms.ModelForm):
    """Form for managing rent reminder templates"""
    
    class Meta:
        model = HouseRentReminderTemplate
        fields = [
            'name', 'template_type', 'category', 'subject', 'content',
            'variables_help', 'is_active', 'is_default'
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Template name'
            }),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email subject (for email templates)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '12',
                'placeholder': 'Template content'
            }),
            'variables_help': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '4',
                'placeholder': 'Help text for available variables'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'name': 'A descriptive name for this template',
            'template_type': 'Type of template (email, SMS, or push notification)',
            'category': 'When this template should be used',
            'subject': 'Subject line for email templates (leave blank for SMS/push)',
            'content': 'Template content. Use variables like {{tenant_name}}, {{property_title}}, {{due_date}}, {{amount}}',
            'variables_help': 'Documentation for available template variables',
            'is_default': 'Mark as default template for this category',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        template_type = cleaned_data.get('template_type')
        subject = cleaned_data.get('subject')
        
        # Email templates should have a subject
        if template_type == 'email' and not subject:
            raise forms.ValidationError("Email templates must have a subject.")
        
        # SMS templates should not have a subject
        if template_type == 'sms' and subject:
            raise forms.ValidationError("SMS templates should not have a subject.")
        
        return cleaned_data


class HouseRentReminderScheduleForm(forms.ModelForm):
    """Form for managing rent reminder schedules"""
    
    class Meta:
        model = HouseRentReminderSchedule
        fields = [
            'schedule_name', 'schedule_type', 'days_before_due',
            'overdue_interval_days', 'max_reminders',
            'email_enabled', 'sms_enabled', 'push_enabled',
            'send_time', 'timezone', 'custom_days', 'is_active'
        ]
        
        widgets = {
            'schedule_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Schedule name'
            }),
            'schedule_type': forms.Select(attrs={'class': 'form-control'}),
            'days_before_due': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'overdue_interval_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '30'
            }),
            'max_reminders': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'send_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'timezone': forms.Select(attrs={'class': 'form-control'}),
            'custom_days': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3',
                'placeholder': 'JSON array of custom days, e.g., [1, 15, 30]'
            }),
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'schedule_name': 'A descriptive name for this schedule',
            'schedule_type': 'How often reminders should be processed',
            'days_before_due': 'Days before due date to send first reminder',
            'overdue_interval_days': 'Days between overdue reminders',
            'max_reminders': 'Maximum number of reminders to send',
            'send_time': 'Time of day to send reminders',
            'timezone': 'Timezone for the send time',
            'custom_days': 'Custom days for custom schedule type (JSON format)',
        }
    
    def clean_custom_days(self):
        custom_days = self.cleaned_data.get('custom_days')
        schedule_type = self.cleaned_data.get('schedule_type')
        
        if schedule_type == 'custom' and custom_days:
            try:
                import json
                days = json.loads(custom_days)
                if not isinstance(days, list):
                    raise forms.ValidationError("Custom days must be a JSON array.")
                if not all(isinstance(day, int) and 1 <= day <= 31 for day in days):
                    raise forms.ValidationError("Custom days must be integers between 1 and 31.")
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for custom days.")
        
        return custom_days


class ManualReminderForm(forms.Form):
    """Form for sending manual reminders"""
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    booking = forms.ModelChoiceField(
        queryset=Booking.objects.filter(property_obj__property_type__name__iexact='house'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the booking/rental to send reminder for"
    )
    
    reminder_type = forms.ChoiceField(
        choices=REMINDER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Type of reminder to send"
    )
    
    custom_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Custom message (optional - will use template if empty)'
        }),
        help_text="Custom message to include with the reminder"
    )
    
    send_immediately = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Send immediately instead of scheduling"
    )
    
    def __init__(self, *args, **kwargs):
        property_obj = kwargs.pop('property_obj', None)
        super().__init__(*args, **kwargs)
        
        if property_obj:
            self.fields['booking'].queryset = Booking.objects.filter(
                property_obj=property_obj,
                booking_status__in=['confirmed', 'checked_in']
            )


class ReminderFilterForm(forms.Form):
    """Form for filtering reminders"""
    
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('', 'All Types'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('phone', 'Phone Call'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    reminder_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by tenant name, property, or booking reference'
        })
    )
    
    overdue_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Overdue Only'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )


class BulkReminderForm(forms.Form):
    """Form for sending bulk reminders"""
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    CATEGORY_CHOICES = [
        ('upcoming', 'Upcoming Payment'),
        ('overdue_1', 'First Overdue'),
        ('overdue_2', 'Second Overdue'),
        ('overdue_3', 'Third Overdue'),
        ('final_notice', 'Final Notice'),
    ]
    
    reminder_type = forms.ChoiceField(
        choices=REMINDER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    property_obj = forms.ModelChoiceField(
        queryset=Property.objects.filter(property_type__name__iexact='house'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Leave blank to send to all house properties"
    )
    
    custom_message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '4',
            'placeholder': 'Custom message (optional)'
        })
    )
    
    dry_run = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Preview what would be sent without actually sending"
    )
