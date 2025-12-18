from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import RentInvoice, RentPayment, LateFee
from documents.models import Lease
from properties.models import Property


class RentModelsTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.tenant = User.objects.create_user(
            username='testtenant',
            email='tenant@test.com',
            first_name='Test',
            last_name='Tenant'
        )
        
        # Create test property
        self.property = Property.objects.create(
            name='Test Property',
            address='123 Test St',
            property_type='apartment'
        )
        
        # Create test lease
        self.lease = Lease.objects.create(
            property_ref=self.property,
            tenant=self.tenant,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=330),
            rent_amount=Decimal('1500.00'),
            status='active'
        )
    
    def test_rent_invoice_creation(self):
        """Test rent invoice creation and calculations"""
        invoice = RentInvoice.objects.create(
            lease=self.lease,
            tenant=self.tenant,
            due_date=date.today() + timedelta(days=5),
            period_start=date.today().replace(day=1),
            period_end=date.today().replace(day=28),
            base_rent=Decimal('1500.00')
        )
        
        self.assertEqual(invoice.total_amount, Decimal('1500.00'))
        self.assertEqual(invoice.balance_due, Decimal('1500.00'))
        self.assertFalse(invoice.is_overdue)
        self.assertTrue(invoice.invoice_number.startswith('INV-'))
    
    def test_rent_payment_creation(self):
        """Test rent payment creation and invoice update"""
        # Create invoice
        invoice = RentInvoice.objects.create(
            lease=self.lease,
            tenant=self.tenant,
            due_date=date.today() + timedelta(days=5),
            period_start=date.today().replace(day=1),
            period_end=date.today().replace(day=28),
            base_rent=Decimal('1500.00')
        )
        
        # Create payment
        payment = RentPayment.objects.create(
            invoice=invoice,
            lease=self.lease,
            tenant=self.tenant,
            amount=Decimal('1500.00'),
            payment_method='bank_transfer',
            status='completed'
        )
        
        # Refresh invoice from database
        invoice.refresh_from_db()
        
        self.assertEqual(invoice.amount_paid, Decimal('1500.00'))
        self.assertEqual(invoice.balance_due, Decimal('0.00'))
        self.assertEqual(invoice.status, 'paid')
    
    def test_late_fee_calculation(self):
        """Test late fee calculation"""
        # Create late fee configuration
        late_fee = LateFee.objects.create(
            lease=self.lease,
            fee_type='fixed',
            amount=Decimal('50.00'),
            grace_period_days=5
        )
        
        # Create overdue invoice
        invoice = RentInvoice.objects.create(
            lease=self.lease,
            tenant=self.tenant,
            due_date=date.today() - timedelta(days=10),
            period_start=date.today().replace(day=1),
            period_end=date.today().replace(day=28),
            base_rent=Decimal('1500.00')
        )
        
        # Test late fee calculation
        days_overdue = 10
        calculated_fee = late_fee.calculate_late_fee(invoice, days_overdue)
        
        self.assertEqual(calculated_fee, Decimal('50.00'))
        
        # Test grace period
        grace_period_fee = late_fee.calculate_late_fee(invoice, 3)
        self.assertEqual(grace_period_fee, Decimal('0.00'))
    
    def test_overdue_status(self):
        """Test invoice overdue status"""
        # Create overdue invoice
        invoice = RentInvoice.objects.create(
            lease=self.lease,
            tenant=self.tenant,
            due_date=date.today() - timedelta(days=5),
            period_start=date.today().replace(day=1),
            period_end=date.today().replace(day=28),
            base_rent=Decimal('1500.00')
        )
        
        self.assertTrue(invoice.is_overdue)
        self.assertEqual(invoice.days_overdue, 5)