from django import forms
from django.contrib.auth import get_user_model
from .models import (
    MaintenanceRequest, MaintenanceSchedule, MaintenanceVendor,
    MaintenanceWorkOrder, MaintenanceExpense
)
from properties.models import Property

User = get_user_model()


class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = [
            'property', 'title', 'description', 'category', 'priority',
            'location_details', 'access_instructions', 'tenant_availability',
            'is_emergency', 'requires_tenant_presence', 'tenant_notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a brief title for the maintenance issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the maintenance issue in detail'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'property': forms.Select(attrs={'class': 'form-control'}),
            'location_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Specific location within the property (e.g., kitchen sink, bedroom 2)'
            }),
            'access_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'How to access the area (keys, codes, special instructions)'
            }),
            'tenant_availability': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'When are you available for repairs? (e.g., weekdays 9-5, weekends)'
            }),
            'tenant_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes or information'
            }),
            'is_emergency': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_tenant_presence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_emergency': 'This is an emergency',
            'requires_tenant_presence': 'I need to be present during repairs',
            'tenant_notes': 'Additional Notes',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter properties based on user role
            if hasattr(user, 'role') and user.role.name.lower() == 'tenant':
                # Tenants can only see properties they're associated with
                from documents.models import Lease
                tenant_properties = Property.objects.filter(
                    leases__tenant=user, leases__status='active'
                ).distinct()
                self.fields['property'].queryset = tenant_properties
            elif hasattr(user, 'role') and user.role.name.lower() == 'landlord':
                # Landlords can see their own properties
                self.fields['property'].queryset = Property.objects.filter(landlord=user)


class AdminMaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = [
            'property', 'tenant', 'title', 'description', 'category', 'priority',
            'status', 'assigned_to', 'due_date', 'estimated_cost', 'actual_cost',
            'location_details', 'access_instructions', 'tenant_availability',
            'is_emergency', 'requires_tenant_presence', 'tenant_notes', 'admin_notes'
        ]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'actual_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to to only show staff users
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class MaintenanceScheduleForm(forms.ModelForm):
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'property', 'title', 'description', 'category', 'schedule_type',
            'next_due_date', 'assigned_to', 'estimated_duration', 'estimated_cost',
            'requires_tenant_presence'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'schedule_type': forms.Select(attrs={'class': 'form-control'}),
            'property': forms.Select(attrs={'class': 'form-control'}),
            'next_due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'estimated_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'requires_tenant_presence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class MaintenanceVendorForm(forms.ModelForm):
    class Meta:
        model = MaintenanceVendor
        fields = [
            'name', 'company_name', 'vendor_type', 'phone', 'email', 'address',
            'license_number', 'insurance_expiry', 'hourly_rate', 'is_preferred', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_preferred': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MaintenanceWorkOrderForm(forms.ModelForm):
    class Meta:
        model = MaintenanceWorkOrder
        fields = [
            'maintenance_request', 'assigned_to', 'vendor', 'scheduled_date',
            'estimated_duration', 'work_description', 'labor_cost', 'material_cost'
        ]
        widgets = {
            'maintenance_request': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'work_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'labor_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'material_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['vendor'].queryset = MaintenanceVendor.objects.filter(is_active=True)


class MaintenanceExpenseForm(forms.ModelForm):
    class Meta:
        model = MaintenanceExpense
        fields = [
            'maintenance_request', 'work_order', 'description', 'expense_type',
            'amount', 'vendor', 'invoice_number', 'receipt_image', 'expense_date', 'notes'
        ]
        widgets = {
            'maintenance_request': forms.Select(attrs={'class': 'form-control'}),
            'work_order': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'expense_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt_image': forms.FileInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = MaintenanceVendor.objects.filter(is_active=True)


class MaintenanceFeedbackForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['tenant_rating', 'tenant_feedback']
        widgets = {
            'tenant_rating': forms.Select(
                choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'tenant_feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please share your feedback about the maintenance work...'
            }),
        }
        labels = {
            'tenant_rating': 'Rate the service (1-5 stars)',
            'tenant_feedback': 'Your feedback',
        }