from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from complaints.models import Complaint, ComplaintResponse, Feedback
from properties.models import Property

User = get_user_model()


class ComplaintModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_complaint_creation(self):
        complaint = Complaint.objects.create(
            user=self.user,
            title='Test Complaint',
            description='This is a test complaint',
            category='service',
            priority='medium'
        )
        self.assertEqual(complaint.title, 'Test Complaint')
        self.assertEqual(complaint.status, 'pending')
        self.assertFalse(complaint.is_resolved)
        
    def test_complaint_str_method(self):
        complaint = Complaint.objects.create(
            user=self.user,
            title='Test Complaint',
            description='This is a test complaint'
        )
        expected_str = f"Complaint #{complaint.id}: Test Complaint"
        self.assertEqual(str(complaint), expected_str)


class ComplaintAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
    def test_create_complaint_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'API Test Complaint',
            'description': 'This is a test complaint via API',
            'category': 'service',
            'priority': 'high'
        }
        response = self.client.post('/api/v1/complaints/complaints/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Complaint.objects.count(), 1)
        
    def test_create_complaint_unauthenticated(self):
        data = {
            'title': 'API Test Complaint',
            'description': 'This is a test complaint via API'
        }
        response = self.client.post('/api/v1/complaints/complaints/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_user_complaints(self):
        # Create complaints for different users
        Complaint.objects.create(
            user=self.user,
            title='User Complaint',
            description='User complaint description'
        )
        Complaint.objects.create(
            user=self.staff_user,
            title='Staff Complaint',
            description='Staff complaint description'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/complaints/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # User should only see their own complaint
        self.assertEqual(len(response.data['results']), 1)
        
    def test_staff_can_see_all_complaints(self):
        # Create complaints for different users
        Complaint.objects.create(
            user=self.user,
            title='User Complaint',
            description='User complaint description'
        )
        Complaint.objects.create(
            user=self.staff_user,
            title='Staff Complaint',
            description='Staff complaint description'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get('/api/v1/complaints/complaints/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Staff should see all complaints
        self.assertEqual(len(response.data['results']), 2)


class FeedbackAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_create_feedback(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'feedback_type': 'general',
            'message': 'Great app! Love the features.',
            'rating': 5
        }
        response = self.client.post('/api/v1/complaints/feedback/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 1)
        
    def test_feedback_rating_validation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'feedback_type': 'general',
            'message': 'Test feedback',
            'rating': 6  # Invalid rating
        }
        response = self.client.post('/api/v1/complaints/feedback/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ComplaintViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_complaint_list_view(self):
        response = self.client.get(reverse('complaints:complaint_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Complaints')
        
    def test_complaint_create_view_get(self):
        response = self.client.get(reverse('complaints:complaint_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submit New Complaint')
        
    def test_complaint_create_view_post(self):
        data = {
            'title': 'Test Web Complaint',
            'description': 'This is a test complaint from web form',
            'category': 'service',
            'priority': 'medium'
        }
        response = self.client.post(reverse('complaints:complaint_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertEqual(Complaint.objects.count(), 1)