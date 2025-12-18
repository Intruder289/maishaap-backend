from django.db import models
from django.conf import settings
from properties.models import Property


class Lease(models.Model):
    """
    Lease model for long-term property rentals
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('terminated', 'Terminated'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    ]
    
    property_ref = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leases')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leases')
    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lease'
        verbose_name_plural = 'Leases'
    
    def __str__(self):
        return f"Lease {self.id} - {self.property_ref.title} ({self.tenant.username})"
    
    @property
    def is_active(self):
        """Check if lease is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date
    
    @property
    def duration_days(self):
        """Calculate lease duration in days"""
        return (self.end_date - self.start_date).days


class Booking(models.Model):
    """
    Booking model for short-term property reservations (hotels, lodges, venues)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    property_ref = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    
    def __str__(self):
        return f"Booking {self.id} - {self.property_ref.title} ({self.tenant.username})"
    
    @property
    def nights(self):
        """Calculate number of nights"""
        return (self.check_out - self.check_in).days
    
    @property
    def is_upcoming(self):
        """Check if booking is in the future"""
        from django.utils import timezone
        return self.check_in > timezone.now().date()


class Document(models.Model):
    """
    Document model for storing files related to leases, bookings, properties, or users
    """
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    property_ref = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='documents')
    file_name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
    
    def __str__(self):
        return f"{self.file_name or 'Document'} - {self.uploaded_at.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        """Auto-set file_name from uploaded file if not provided"""
        if not self.file_name and self.file:
            self.file_name = self.file.name
        super().save(*args, **kwargs)
    
    @property
    def file_url(self):
        """Get the full URL of the file"""
        if self.file:
            return self.file.url
        return None
    
    @property
    def file_size(self):
        """Get file size in bytes"""
        if self.file:
            return self.file.size
        return 0
