from django.db import models
from django.conf import settings
from django.utils import timezone


class Complaint(models.Model):
    """
    Complaint model for tracking user complaints
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]
    
    CATEGORY_CHOICES = [
        ('property', 'Property Issue'),
        ('service', 'Service Quality'),
        ('payment', 'Payment Issue'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        help_text="User who submitted the complaint"
    )
    property = models.ForeignKey(
        'properties.Property', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Property related to the complaint (if applicable)"
    )
    title = models.CharField(max_length=200, help_text="Brief title of the complaint")
    description = models.TextField(help_text="Detailed description of the complaint")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='other',
        help_text="Category of the complaint"
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        help_text="Priority level of the complaint"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the complaint"
    )
    rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Rating given by the user (1-5 stars)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date when the complaint was resolved"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_complaints',
        help_text="Staff member who resolved the complaint"
    )
    status_change_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for changing status from resolved (required when changing from resolved status)"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Complaint #{self.id}: {self.title}"


class ComplaintResponse(models.Model):
    """
    Model for tracking responses to complaints
    """
    RESPONSE_TYPE_CHOICES = [
        ('internal', 'Internal Note'),
        ('user', 'Response to User'),
        ('update', 'Status Update'),
    ]
    
    complaint = models.ForeignKey(
        Complaint, 
        on_delete=models.CASCADE, 
        related_name='responses',
        help_text="The complaint this response is for"
    )
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        help_text="Staff member providing the response"
    )
    response_type = models.CharField(
        max_length=20, 
        choices=RESPONSE_TYPE_CHOICES, 
        default='user',
        help_text="Type of response"
    )
    message = models.TextField(help_text="Response content")
    is_visible_to_user = models.BooleanField(
        default=True,
        help_text="Whether this response is visible to the complaint submitter"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response to Complaint #{self.complaint.id} by {self.responder.username}"


class Feedback(models.Model):
    """
    General feedback model for app ratings and suggestions
    """
    FEEDBACK_TYPE_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('general', 'General Feedback'),
        ('rating', 'App Rating'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        help_text="User providing feedback"
    )
    property = models.ForeignKey(
        'properties.Property', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Property this feedback is about (if applicable)"
    )
    feedback_type = models.CharField(
        max_length=20, 
        choices=FEEDBACK_TYPE_CHOICES, 
        default='general'
    )
    title = models.CharField(max_length=200, blank=True)
    message = models.TextField(help_text="Feedback content")
    rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Rating from 1-5 stars"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.title:
            return f"Feedback: {self.title}"
        return f"Feedback from {self.user.username} on {self.created_at.date()}"