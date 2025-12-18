from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.utils import log_activity
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Populate sample activities for dashboard testing'

    def handle(self, *args, **options):
        # Get or create a test user
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No users found. Please create a user first.')
                )
                return

        # Sample activities
        activities = [
            {
                'action': 'create',
                'description': f'{user.get_full_name() or user.username} added new property "Luxury Apartment 4B"',
                'content_type': 'Property',
                'object_id': 1,
                'priority': 'medium',
                'amount': Decimal('850000.00')
            },
            {
                'action': 'payment',
                'description': f'Rent payment received from Sarah Johnson',
                'content_type': 'Payment',
                'object_id': 2,
                'priority': 'high',
                'amount': Decimal('1200000.00')
            },
            {
                'action': 'complaint',
                'description': f'New complaint submitted: Kitchen faucet leak',
                'content_type': 'Complaint',
                'object_id': 1,
                'priority': 'urgent',
            },
            {
                'action': 'maintenance',
                'description': f'Maintenance request: Air conditioning repair - Unit 3C',
                'content_type': 'MaintenanceRequest',
                'object_id': 3,
                'priority': 'high',
                'amount': Decimal('250000.00')
            },
            {
                'action': 'booking',
                'description': f'New booking request for property viewing',
                'content_type': 'Booking',
                'object_id': 4,
                'priority': 'medium',
            },
            {
                'action': 'lease',
                'description': f'Lease agreement signed with John Doe for Apartment 2A',
                'content_type': 'Lease',
                'object_id': 5,
                'priority': 'high',
                'amount': Decimal('900000.00')
            },
            {
                'action': 'update',
                'description': f'Property information updated: Swimming pool maintenance',
                'content_type': 'Property',
                'object_id': 6,
                'priority': 'low',
            },
            {
                'action': 'payment',
                'description': f'Security deposit received from Maria Garcia',
                'content_type': 'Payment',
                'object_id': 7,
                'priority': 'medium',
                'amount': Decimal('500000.00')
            },
            {
                'action': 'document',
                'description': f'Contract document uploaded for Apartment 1B',
                'content_type': 'Document',
                'object_id': 8,
                'priority': 'medium',
            },
            {
                'action': 'create',
                'description': f'New tenant profile created: Michael Thompson',
                'content_type': 'User',
                'object_id': 9,
                'priority': 'low',
            },
        ]

        # Create activities with different timestamps
        for i, activity_data in enumerate(activities):
            # Create activities with timestamps spread over the last week
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            timestamp = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
            
            # Create the activity
            from accounts.models import ActivityLog
            ActivityLog.objects.create(
                user=user,
                action=activity_data['action'],
                description=activity_data['description'],
                content_type=activity_data['content_type'],
                object_id=activity_data.get('object_id'),
                priority=activity_data['priority'],
                amount=activity_data.get('amount'),
                timestamp=timestamp
            )
            
            self.stdout.write(f'Created activity: {activity_data["description"][:50]}...')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(activities)} sample activities!')
        )