from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import (
    MaintenanceRequest, MaintenanceSchedule, MaintenanceVendor,
    MaintenanceWorkOrder, MaintenanceExpense, MaintenanceImage
)
from properties.models import Property, PropertyType, PropertyCategory
from accounts.models import Role

User = get_user_model()


class MaintenanceRequestModelTest(TestCase):
    def setUp(self):
        # Create roles
        self.tenant_role = Role.objects.create(name='Tenant')
        self.landlord_role = Role.objects.create(name='Landlord')
        
        # Create users
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@test.com',
            password='testpass123',
            role=self.landlord_role
        )
        
        self.tenant = User.objects.create_user(
            username='tenant',
            email='tenant@test.com',
            password='testpass123',
            role=self.tenant_role
        )
        
        # Create property type and category
        self.property_type = PropertyType.objects.create(name='House')
        self.property_category = PropertyCategory.objects.create(name='Residential')
        
        # Create property
        self.property = Property.objects.create(
            name='Test Property',
            landlord=self.landlord,
            type=self.property_type,
            category=self.property_category,
            address='123 Test St',
            description='Test property description'
        )

    def test_maintenance_request_creation(self):
        """Test creating a maintenance request"""
        request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Leaky Faucet',
            description='The kitchen faucet is leaking',
            category='plumbing',
            priority='medium'
        )
        
        self.assertEqual(request.title, 'Leaky Faucet')
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.tenant, self.tenant)
        self.assertEqual(request.property, self.property)
        self.assertFalse(request.is_emergency)

    def test_maintenance_request_str(self):
        """Test string representation of maintenance request"""
        request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Broken Window',
            description='Window won\'t close',
            category='other',
            priority='low'
        )
        
        expected_str = f"Broken Window - {self.property.name} (Pending)"
        self.assertEqual(str(request), expected_str)

    def test_days_since_request(self):
        """Test days_since_request property"""
        past_date = timezone.now() - timedelta(days=5)
        request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Old Request',
            description='Old maintenance request',
            category='other',
            priority='low'
        )
        
        # Manually set the requested_date to test the property
        request.requested_date = past_date
        request.save()
        
        self.assertEqual(request.days_since_request, 5)

    def test_is_overdue_property(self):
        """Test is_overdue property"""
        past_due_date = timezone.now().date() - timedelta(days=2)
        request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Overdue Request',
            description='This should be overdue',
            category='other',
            priority='high',
            due_date=past_due_date
        )
        
        self.assertTrue(request.is_overdue)
        self.assertEqual(request.days_overdue, 2)

    def test_status_auto_update_on_save(self):
        """Test that status is automatically updated when assigned"""
        request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Test Assignment',
            description='Test automatic status update',
            category='other',
            priority='medium'
        )
        
        # Initially pending
        self.assertEqual(request.status, 'pending')
        
        # Assign to someone - should update status
        staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        request.assigned_to = staff_user
        request.save()
        
        self.assertEqual(request.status, 'assigned')
        self.assertIsNotNone(request.assigned_date)


class MaintenanceVendorModelTest(TestCase):
    def test_vendor_creation(self):
        """Test creating a maintenance vendor"""
        vendor = MaintenanceVendor.objects.create(
            name='John Smith',
            company_name='Smith Plumbing',
            vendor_type='plumber',
            phone='+255123456789',
            email='john@smithplumbing.com',
            hourly_rate=Decimal('50000.00')
        )
        
        self.assertEqual(vendor.name, 'John Smith')
        self.assertEqual(vendor.vendor_type, 'plumber')
        self.assertTrue(vendor.is_active)
        self.assertFalse(vendor.is_preferred)

    def test_vendor_str(self):
        """Test string representation of vendor"""
        vendor = MaintenanceVendor.objects.create(
            name='Jane Doe',
            vendor_type='electrician',
            phone='+255987654321'
        )
        
        expected_str = "Jane Doe - Electrician"
        self.assertEqual(str(vendor), expected_str)

    def test_completion_rate_property(self):
        """Test completion rate calculation"""
        vendor = MaintenanceVendor.objects.create(
            name='Test Vendor',
            vendor_type='handyman',
            phone='+255123456789',
            total_jobs=10,
            completed_jobs=8
        )
        
        self.assertEqual(vendor.completion_rate, 80.0)

    def test_completion_rate_zero_jobs(self):
        """Test completion rate with zero jobs"""
        vendor = MaintenanceVendor.objects.create(
            name='New Vendor',
            vendor_type='painter',
            phone='+255123456789',
            total_jobs=0,
            completed_jobs=0
        )
        
        self.assertEqual(vendor.completion_rate, 0)


class MaintenanceWorkOrderModelTest(TestCase):
    def setUp(self):
        # Create necessary objects for work order
        self.tenant_role = Role.objects.create(name='Tenant')
        self.landlord_role = Role.objects.create(name='Landlord')
        
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@test.com',
            password='testpass123',
            role=self.landlord_role
        )
        
        self.tenant = User.objects.create_user(
            username='tenant',
            email='tenant@test.com',
            password='testpass123',
            role=self.tenant_role
        )
        
        self.property_type = PropertyType.objects.create(name='House')
        self.property_category = PropertyCategory.objects.create(name='Residential')
        
        self.property = Property.objects.create(
            name='Test Property',
            landlord=self.landlord,
            type=self.property_type,
            category=self.property_category,
            address='123 Test St'
        )
        
        self.maintenance_request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Test Request',
            description='Test maintenance request',
            category='plumbing',
            priority='medium'
        )

    def test_work_order_creation(self):
        """Test creating a work order"""
        work_order = MaintenanceWorkOrder.objects.create(
            maintenance_request=self.maintenance_request,
            work_description='Fix the leaky pipe',
            labor_cost=Decimal('100000.00'),
            material_cost=Decimal('50000.00')
        )
        
        self.assertEqual(work_order.maintenance_request, self.maintenance_request)
        self.assertEqual(work_order.total_cost, Decimal('150000.00'))
        self.assertEqual(work_order.status, 'created')
        self.assertIsNotNone(work_order.work_order_number)

    def test_work_order_number_generation(self):
        """Test automatic work order number generation"""
        work_order = MaintenanceWorkOrder.objects.create(
            maintenance_request=self.maintenance_request,
            work_description='Test work order'
        )
        
        self.assertTrue(work_order.work_order_number.startswith('WO-'))
        self.assertIn(timezone.now().strftime('%Y%m'), work_order.work_order_number)


class MaintenanceExpenseModelTest(TestCase):
    def setUp(self):
        # Setup similar to WorkOrderModelTest
        self.tenant_role = Role.objects.create(name='Tenant')
        self.landlord_role = Role.objects.create(name='Landlord')
        
        self.landlord = User.objects.create_user(
            username='landlord',
            email='landlord@test.com',
            password='testpass123',
            role=self.landlord_role
        )
        
        self.tenant = User.objects.create_user(
            username='tenant',
            email='tenant@test.com',
            password='testpass123',
            role=self.tenant_role
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.property_type = PropertyType.objects.create(name='House')
        self.property_category = PropertyCategory.objects.create(name='Residential')
        
        self.property = Property.objects.create(
            name='Test Property',
            landlord=self.landlord,
            type=self.property_type,
            category=self.property_category,
            address='123 Test St'
        )
        
        self.maintenance_request = MaintenanceRequest.objects.create(
            property=self.property,
            tenant=self.tenant,
            title='Test Request',
            description='Test maintenance request',
            category='plumbing',
            priority='medium'
        )

    def test_expense_creation(self):
        """Test creating a maintenance expense"""
        expense = MaintenanceExpense.objects.create(
            maintenance_request=self.maintenance_request,
            description='Pipe replacement materials',
            expense_type='materials',
            amount=Decimal('75000.00'),
            recorded_by=self.staff_user
        )
        
        self.assertEqual(expense.description, 'Pipe replacement materials')
        self.assertEqual(expense.amount, Decimal('75000.00'))
        self.assertEqual(expense.recorded_by, self.staff_user)

    def test_expense_str(self):
        """Test string representation of expense"""
        expense = MaintenanceExpense.objects.create(
            maintenance_request=self.maintenance_request,
            description='Labor costs',
            expense_type='labor',
            amount=Decimal('120000.00'),
            recorded_by=self.staff_user
        )
        
        expected_str = "Labor costs - TZS 120,000"
        self.assertEqual(str(expense), expected_str)