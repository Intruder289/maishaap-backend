from django import forms
from django.contrib.auth.models import User
from .models import RentInvoice
from payments.models import Payment
from documents.models import Lease


class RentInvoiceForm(forms.ModelForm):
    """Form for creating/editing rent invoices"""
    
    class Meta:
        model = RentInvoice
        fields = [
            'lease', 'due_date', 'period_start', 'period_end',
            'base_rent', 'late_fee', 'other_charges', 'discount', 'notes'
        ]
        widgets = {
            'lease': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'base_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'late_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'other_charges': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lease'].queryset = Lease.objects.filter(status='active').select_related('property_ref', 'tenant')
        self.fields['lease'].empty_label = "Select a lease"
        
        # Set default values
        if not self.instance.pk:
            from django.utils import timezone
            today = timezone.now().date()
            self.fields['period_start'].initial = today.replace(day=1)
            self.fields['due_date'].initial = today.replace(day=5)  # Due on 5th of month


class RentPaymentForm(forms.Form):
    """Form for recording rent payments (using unified Payment model)"""
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    reference_number = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )