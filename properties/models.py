from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Region(models.Model):
    """Model for property regions/locations"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'regions'
        ordering = ['name']


class District(models.Model):
    """Model for districts within regions"""
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.region.name})"
    
    class Meta:
        db_table = 'districts'
        ordering = ['region', 'name']
        unique_together = ['name', 'region']  # District names must be unique within a region


class PropertyType(models.Model):
    """Model for property types (apartment, house, studio, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Normalize name to lowercase to prevent case-sensitive duplicates"""
        if self.name:
            self.name = self.name.lower().strip()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name.title()  # Display with title case for UI
    
    class Meta:
        db_table = 'property_types'
        ordering = ['name']


class Amenity(models.Model):
    """Model for property amenities"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For mobile app icons
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'amenities'
        ordering = ['name']
        verbose_name_plural = 'Amenities'


class Property(models.Model):
    """Main property model"""
    PROPERTY_STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('under_maintenance', 'Under Maintenance'),
        ('unavailable', 'Unavailable'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('hotel', 'Hotel'),
        ('lodge', 'Lodge'),
        ('venue', 'Venue'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE, related_name='properties')
    
    # Location
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='properties')
    district = models.ForeignKey('District', on_delete=models.SET_NULL, related_name='properties', blank=True, null=True, help_text="District within the selected region")
    address = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    # Property Details - Common fields
    bedrooms = models.PositiveIntegerField(blank=True, null=True, help_text="Number of bedrooms (not applicable for venues)")
    bathrooms = models.PositiveIntegerField(blank=True, null=True, help_text="Number of bathrooms")
    size_sqft = models.PositiveIntegerField(blank=False, null=False, help_text="Size in square feet")
    floor_number = models.PositiveIntegerField(blank=True, null=True)
    total_floors = models.PositiveIntegerField(blank=True, null=True)
    
    # Hotel/Lodge specific fields
    total_rooms = models.PositiveIntegerField(blank=True, null=True, help_text="Total number of rooms (for hotels/lodges)")
    room_types = models.JSONField(blank=True, null=True, help_text="Room types and counts (for hotels/lodges)")
    
    # Venue specific fields
    capacity = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum capacity (for venues)")
    venue_type = models.CharField(max_length=100, blank=True, null=True, help_text="Type of venue (conference, wedding, etc.)")
    
    # Pricing
    RENT_PERIOD_CHOICES = [
        ('month', 'Per Month'),
        ('day', 'Per Day'),
        ('week', 'Per Week'),
        ('year', 'Per Year'),
    ]
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    rent_period = models.CharField(
        max_length=10,
        choices=RENT_PERIOD_CHOICES,
        default='month',
        help_text="Duration for which the rent amount applies (e.g., per month for houses, per day for hotels/lodges)"
    )
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    utilities_included = models.BooleanField(default=False)
    visit_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Cost for visit-only access (house properties only). User pays this to get owner contact and location."
    )
    
    # Property Management
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_properties')
    status = models.CharField(max_length=20, choices=PROPERTY_STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(default=False)
    is_furnished = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Whether the property is active/visible")
    booking_expiration_hours = models.PositiveIntegerField(
        default=12,
        help_text="Hours after booking creation to cancel if no payment (partial or full) is made. Set to 0 to disable auto-cancellation."
    )
    
    # Approval Management
    is_approved = models.BooleanField(default=False, help_text="Whether the property has been approved by admin")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='approved_properties', null=True, blank=True, help_text="Admin who approved this property")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="When the property was approved")
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection if property was rejected")
    admin_comments = models.TextField(blank=True, null=True, help_text="Admin comments/notes about the property")
    
    # Amenities
    amenities = models.ManyToManyField(Amenity, through='PropertyAmenity', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_from = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def get_primary_image(self):
        """
        Return the primary PropertyImage object if available, otherwise the first image.
        This helper is used throughout templates to ensure the correct primary image is shown.
        """
        if hasattr(self, '_primary_image_cache'):
            return self._primary_image_cache

        primary = self.images.filter(is_primary=True).order_by('order', 'created_at').first()
        if not primary:
            primary = self.images.order_by('order', 'created_at').first()

        self._primary_image_cache = primary
        return primary

    def has_active_property_booking(self):
        """Check if there is an active booking in the core Booking model."""
        today = timezone.now().date()
        return self.property_bookings.filter(
            booking_status__in=['confirmed', 'checked_in'],
            check_out_date__gte=today
        ).exists()

    def has_active_document_booking(self):
        """Check if there is an active booking in the documents app."""
        try:
            from documents.models import Booking as DocumentBooking
        except Exception:
            return False

        today = timezone.now().date()
        return DocumentBooking.objects.filter(
            property_ref=self,
            status__in=['confirmed'],
            check_out__gte=today
        ).exists()

    def has_active_lease(self):
        """Check if there is an active lease in the documents app."""
        try:
            from documents.models import Lease
        except Exception:
            return False

        today = timezone.now().date()
        return Lease.objects.filter(
            property_ref=self,
            status='active',
            start_date__lte=today,
            end_date__gte=today
        ).exists()

    def refresh_status_from_activity(self):
        """
        Automatically synchronize the property status based on active bookings or leases.
        Only toggles between 'available' and 'rented' so other manual statuses stay intact.
        """
        has_activity = any([
            self.has_active_property_booking(),
            self.has_active_document_booking(),
            self.has_active_lease()
        ])

        desired_status = 'rented' if has_activity else 'available'

        # If there is no activity and the property is manually marked as unavailable/maintenance, keep it
        if not has_activity and self.status not in ['available', 'rented']:
            return

        if self.status != desired_status:
            Property.objects.filter(pk=self.pk).update(status=desired_status)
            self.status = desired_status

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('properties:property_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure admin-created properties are always active and approved
        """
        # If owner is admin/staff, ensure property is active and approved
        if self.owner and (self.owner.is_staff or self.owner.is_superuser):
            if not self.is_active:
                self.is_active = True
            if not self.is_approved:
                self.is_approved = True
                # Set approved_by and approved_at if not already set
                if not self.approved_by:
                    self.approved_by = self.owner
                if not self.approved_at:
                    from django.utils import timezone
                    self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    @property
    def is_house(self):
        return self.property_type.name.lower() == 'house'
    
    @property
    def is_hotel(self):
        return self.property_type.name.lower() == 'hotel'
    
    @property
    def is_lodge(self):
        return self.property_type.name.lower() == 'lodge'
    
    @property
    def is_venue(self):
        return self.property_type.name.lower() == 'venue'
    
    def is_currently_booked(self):
        """Check if property is currently booked/occupied by active bookings or leases"""
        from django.utils import timezone
        from documents.models import Lease
        today = timezone.now().date()
        
        # Check for active leases
        active_lease = Lease.objects.filter(
            property_ref=self,
            status='active',
            start_date__lte=today,
            end_date__gte=today
        ).exists()
        
        if active_lease:
            return True
        
        # Check for active bookings (properties.Booking)
        active_booking = self.property_bookings.filter(
            booking_status__in=['confirmed', 'checked_in'],
            check_in_date__lte=today,
            check_out_date__gte=today
        ).exists()
        
        if active_booking:
            return True
        
        # Check for active bookings (documents.Booking)
        active_doc_booking = self.bookings.filter(
            status__in=['confirmed'],
            check_in__lte=today,
            check_out__gte=today
        ).exists()
        
        return active_doc_booking
    
    def is_available_for_booking(self, check_in_date=None, check_out_date=None):
        """Check if property is available for booking in a given date range"""
        from django.utils import timezone
        from documents.models import Lease
        
        # If property status is not available, return False
        if self.status not in ['available']:
            return False
        
        # If property is not active, return False
        if not self.is_active:
            return False
        
        # If dates provided, check for conflicts
        if check_in_date and check_out_date:
            # Check for active leases
            conflicting_lease = Lease.objects.filter(
                property_ref=self,
                status='active',
                start_date__lte=check_out_date,
                end_date__gte=check_in_date
            ).exists()
            
            if conflicting_lease:
                return False
            
            # Check for conflicting bookings (properties.Booking)
            conflicting_booking = self.property_bookings.filter(
                booking_status__in=['confirmed', 'checked_in', 'pending'],
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            ).exists()
            
            if conflicting_booking:
                return False
            
            # Check for conflicting bookings (documents.Booking)
            conflicting_doc_booking = self.bookings.filter(
                status__in=['confirmed', 'pending'],
                check_in__lt=check_out_date,
                check_out__gt=check_in_date
            ).exists()
            
            if conflicting_doc_booking:
                return False
        
        # If no dates provided, just check current status
        return not self.is_currently_booked()
    
    class Meta:
        db_table = 'properties'
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'


class PropertyAmenity(models.Model):
    """Through model for Property-Amenity relationship"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_amenities'
        unique_together = ['property', 'amenity']


class PropertyImage(models.Model):
    """Model for property images"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/images/')
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.property.title} - Image {self.order}"
    
    class Meta:
        db_table = 'property_images'
        ordering = ['order', 'created_at']
        unique_together = ['property', 'order']


class PropertyView(models.Model):
    """Model to track property views for analytics"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_views'
        ordering = ['-viewed_at']


class PropertyFavorite(models.Model):
    """Model for user favorite properties"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'property_favorites'
        unique_together = ['user', 'property']
        ordering = ['-created_at']


class PropertyVisitPayment(models.Model):
    """
    Model to track visit-only payments for house properties.
    One-time payment per user per property to access owner contact and location.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visit_payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_visit_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Link to unified Payment model for transaction tracking
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='property_visit_payments'
    )
    
    # Payment gateway transaction details
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'property_visit_payments'
        unique_together = ['property', 'user']  # One-time payment per user per property
        ordering = ['-created_at']
        verbose_name = 'Property Visit Payment'
        verbose_name_plural = 'Property Visit Payments'
    
    def __str__(self):
        return f"Visit Payment - {self.user.username} - {self.property.title} - {self.status}"


# Booking and Customer Management Models

class Customer(models.Model):
    """Model for customers who book properties"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Address Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Identification
    id_type = models.CharField(max_length=50, blank=True, null=True, help_text="ID Type (Passport, Driver's License, etc.)")
    id_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']


class Booking(models.Model):
    """Model for property bookings"""
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    # Basic Information
    property_obj = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_bookings')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_bookings')
    
    # Booking Details
    booking_reference = models.CharField(max_length=20, unique=True, help_text="Unique booking reference")
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.PositiveIntegerField(default=1)
    
    # Room/Unit Information (for hotels/lodges)
    room_number = models.CharField(max_length=20, blank=True, null=True)
    room_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Special Requests
    special_requests = models.TextField(blank=True, null=True)
    
    # Staff Information
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_property_bookings')
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_property_bookings')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_out_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.customer.full_name}"
    
    @property
    def duration_days(self):
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_checked_in(self):
        return self.booking_status == 'checked_in'
    
    @property
    def is_checked_out(self):
        return self.booking_status == 'checked_out'
    
    @property
    def base_rate(self):
        """Get the base rate from property (rent_amount)"""
        if not self.property_obj:
            return 0
        return self.property_obj.rent_amount or 0
    
    @property
    def rent_period(self):
        """Get rent period from property (month/day/week/year)"""
        if not self.property_obj:
            return 'day'  # Default fallback
        return self.property_obj.rent_period or 'day'  # Default to 'day' if not set
    
    @property
    def monthly_rate(self):
        """
        DEPRECATED: Use base_rate instead.
        Kept for backward compatibility with templates.
        Returns base_rate for monthly properties, or calculates approximate monthly rate for others.
        """
        if self.rent_period == 'month':
            return self.base_rate
        elif self.rent_period == 'day':
            # Approximate: daily_rate × 30
            return self.base_rate * 30
        elif self.rent_period == 'week':
            # Approximate: weekly_rate × 4
            return self.base_rate * 4
        elif self.rent_period == 'year':
            # Approximate: yearly_rate / 12
            return self.base_rate / 12
        return self.base_rate
    
    @property
    def duration_months(self):
        """Calculate the number of months for this booking"""
        try:
            from dateutil.relativedelta import relativedelta
            delta = relativedelta(self.check_out_date, self.check_in_date)
            months = delta.years * 12 + delta.months
            # If there are remaining days, count as additional month
            if delta.days > 0:
                months += 1
            return max(1, months)  # Minimum 1 month
        except ImportError:
            # Fallback calculation if dateutil is not available
            from datetime import timedelta
            days = self.duration_days
            # Approximate: 30 days per month
            months = max(1, (days + 29) // 30)  # Round up
            return months
        except Exception:
            # Fallback to 1 month if calculation fails
            return 1
    
    @property
    def calculated_total_amount(self):
        """
        Calculate total amount based on property rent_period:
        - 'day': base_rate × duration_days (hotels, lodges)
        - 'month': base_rate × duration_months (houses)
        - 'week': base_rate × weeks (weekly rentals)
        - 'year': base_rate × years (yearly rentals)
        """
        try:
            base_rate = self.base_rate or 0
            duration_days = self.duration_days or 0
            
            if duration_days <= 0:
                return base_rate  # Return base rate if invalid duration
            
            if self.rent_period == 'day':
                # Hotels, Lodges, Venues: daily_rate × nights
                return base_rate * duration_days
            elif self.rent_period == 'month':
                # Houses: monthly_rate × months
                try:
                    duration_months = self.duration_months
                    return base_rate * duration_months
                except Exception:
                    # Fallback to daily calculation if months calculation fails
                    return base_rate * duration_days
            elif self.rent_period == 'week':
                # Weekly rentals
                weeks = max(1, duration_days // 7)
                if duration_days % 7 > 0:
                    weeks += 1  # Round up partial weeks
                return base_rate * weeks
            elif self.rent_period == 'year':
                # Yearly rentals
                try:
                    duration_months = self.duration_months
                    years = max(1, duration_months // 12)
                    if duration_months % 12 > 0:
                        years += 1  # Round up partial years
                    return base_rate * years
                except Exception:
                    # Fallback to daily calculation if months calculation fails
                    return base_rate * duration_days
            else:
                # Fallback to daily calculation
                return base_rate * duration_days
        except Exception:
            # Ultimate fallback: return the stored total_amount if calculation fails
            return self.total_amount if hasattr(self, 'total_amount') else 0
    
    @property
    def daily_rate(self):
        """
        Calculate daily rate for display purposes.
        For daily rentals, this is the base_rate.
        For other periods, calculate average daily rate.
        """
        if self.rent_period == 'day':
            return self.base_rate
        elif self.duration_days > 0:
            return self.calculated_total_amount / self.duration_days
        else:
            # Fallback calculation
            if self.rent_period == 'month':
                return self.base_rate / 30  # Approximate daily from monthly
            elif self.rent_period == 'week':
                return self.base_rate / 7
            elif self.rent_period == 'year':
                return self.base_rate / 365
            return self.base_rate

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # After every save, ensure the property's status reflects current bookings
        self.property_obj.refresh_status_from_activity()

    def delete(self, *args, **kwargs):
        property_obj = self.property_obj
        super().delete(*args, **kwargs)
        property_obj.refresh_status_from_activity()
    
    @property
    def is_stay_over(self):
        """Check if the stay period is over"""
        from django.utils import timezone
        today = timezone.now().date()
        return today > self.check_out_date
    
    def is_expired(self):
        """Check if booking has expired due to no payment within expiration time"""
        # If booking is already cancelled or checked out, it's not expired
        if self.booking_status in ['cancelled', 'checked_out']:
            return False
        
        # If payment is made (partial or full), booking is not expired
        if self.payment_status in ['paid', 'partial']:
            return False
        
        # Get expiration hours from property (0 means disabled)
        expiration_hours = self.property_obj.booking_expiration_hours
        if expiration_hours == 0:
            return False  # Auto-cancellation disabled
        
        # Calculate expiration time
        from django.utils import timezone
        from datetime import timedelta
        expiration_time = self.created_at + timedelta(hours=expiration_hours)
        current_time = timezone.now()
        
        # Check if expiration time has passed
        return current_time > expiration_time
    
    def cancel_if_expired(self):
        """Cancel booking if expired and return True if cancelled"""
        if self.is_expired():
            self.booking_status = 'cancelled'
            self.save(update_fields=['booking_status'])
            return True
        return False
    
    @property
    def days_remaining(self):
        """Calculate days remaining in the stay"""
        from django.utils import timezone
        today = timezone.now().date()
        if today < self.check_in_date:
            return self.duration_days
        elif today > self.check_out_date:
            return 0
        else:
            return (self.check_out_date - today).days
    
    @property
    def is_payment_valid(self):
        """Check if payment amount matches calculated amount"""
        return self.paid_amount >= self.calculated_total_amount
    
    def calculate_and_update_total(self):
        """Calculate and update the total amount based on duration and monthly rate"""
        self.total_amount = self.calculated_total_amount
        self.save()
        return self.total_amount
    
    def update_payment_status(self):
        """Update payment status based on paid amount"""
        # Use calculated_total_amount if available, otherwise use total_amount
        total = self.calculated_total_amount if self.calculated_total_amount and self.calculated_total_amount > 0 else (self.total_amount or 0)
        paid = self.paid_amount or 0
        
        if total > 0 and paid >= total:
            self.payment_status = 'paid'
        elif paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
        self.save()
    
    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']


class Payment(models.Model):
    """Model for booking payments"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money (AZAM Pay)'),
        ('online', 'Online Payment (AZAM Pay)'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('deposit', 'Deposit'),
        ('partial', 'Partial Payment'),
        ('full', 'Full Payment'),
        ('refund', 'Refund'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic Information
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='active')
    
    # Payment Details
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    
    # Staff Information
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_property_payments')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.booking.booking_reference}"
    
    class Meta:
        db_table = 'property_payments'
        ordering = ['-payment_date']


class Room(models.Model):
    """Model for hotel/lodge rooms"""
    ROOM_STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('out_of_order', 'Out of Order'),
    ]
    
    # Basic Information
    property_obj = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=100)
    floor_number = models.PositiveIntegerField(blank=True, null=True)
    
    # Room Details
    capacity = models.PositiveIntegerField(default=1)
    bed_type = models.CharField(max_length=100, blank=True, null=True)
    amenities = models.TextField(blank=True, null=True)
    
    # Pricing
    base_rate = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    
    # Current Booking
    current_booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_room')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.property.title} - Room {self.room_number}"
    
    @property
    def is_available(self):
        return self.status == 'available' and self.current_booking is None
    
    class Meta:
        db_table = 'property_rooms'
        unique_together = ['property_obj', 'room_number']
        ordering = ['room_number']


class Complaint(models.Model):
    """Model for customer complaints"""
    COMPLAINT_STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Basic Information
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booking_complaints')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_complaints')
    
    # Complaint Details
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=COMPLAINT_STATUS_CHOICES, default='open')
    
    # Resolution
    resolution = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_property_complaints')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Complaint {self.id} - {self.subject}"
    
    class Meta:
        db_table = 'property_complaints'
        ordering = ['-created_at']


# =============================================================================
# HOUSE RENT REMINDER MODELS
# =============================================================================

class HouseRentReminderSettings(models.Model):
    """
    Configuration settings for automated rent reminders for house properties
    """
    REMINDER_FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    property_obj = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='reminder_settings',
        limit_choices_to={'property_type__name__iexact': 'house'}
    )
    
    # Reminder timing settings
    days_before_due = models.IntegerField(
        default=7,
        help_text="Days before due date to send first reminder"
    )
    overdue_reminder_interval = models.IntegerField(
        default=3,
        help_text="Days between overdue reminders"
    )
    max_overdue_reminders = models.IntegerField(
        default=5,
        help_text="Maximum number of overdue reminders to send"
    )
    
    # Reminder types enabled
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    
    # Custom messages
    custom_email_template = models.TextField(
        blank=True,
        help_text="Custom email template (optional)"
    )
    custom_sms_template = models.TextField(
        blank=True,
        help_text="Custom SMS template (optional)"
    )
    
    # Grace period settings
    grace_period_days = models.IntegerField(
        default=5,
        help_text="Grace period before late fees apply"
    )
    
    # Auto-escalation settings
    auto_escalate_enabled = models.BooleanField(
        default=True,
        help_text="Automatically escalate to property manager after max reminders"
    )
    escalation_email = models.EmailField(
        blank=True,
        help_text="Email to notify for escalation"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'House Rent Reminder Settings'
        verbose_name_plural = 'House Rent Reminder Settings'
        unique_together = ['property_obj']
    
    def __str__(self):
        return f"Reminder Settings for {self.property_obj.title}"
    
    def get_next_reminder_date(self, due_date, reminder_count=0):
        """Calculate next reminder date based on settings"""
        from datetime import timedelta
        if reminder_count == 0:
            # First reminder - days before due
            return due_date - timedelta(days=self.days_before_due)
        else:
            # Overdue reminders - every X days
            return due_date + timedelta(days=self.overdue_reminder_interval * reminder_count)


class HouseRentReminder(models.Model):
    """
    Enhanced rent reminder tracking for house properties
    """
    REMINDER_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    REMINDER_TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('phone', 'Phone Call'),
    ]
    
    # Core relationships
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name='house_reminders',
        limit_choices_to={'property_obj__property_type__name__iexact': 'house'}
    )
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='house_reminders'
    )
    property_obj = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='house_reminders',
        limit_choices_to={'property_type__name__iexact': 'house'}
    )
    
    # Reminder details
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    reminder_status = models.CharField(max_length=20, choices=REMINDER_STATUS_CHOICES, default='scheduled')
    
    # Timing
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    days_before_due = models.IntegerField()  # Negative for overdue reminders
    
    # Content
    subject = models.CharField(max_length=200, blank=True)
    message_content = models.TextField()
    custom_message = models.TextField(blank=True)
    
    # Tracking
    reminder_sequence = models.IntegerField(
        default=1,
        help_text="Sequence number of this reminder (1st, 2nd, etc.)"
    )
    is_overdue = models.BooleanField(default=False)
    
    # Delivery tracking
    delivery_status = models.CharField(max_length=50, blank=True)
    delivery_error = models.TextField(blank=True)
    delivery_reference = models.CharField(max_length=100, blank=True)
    
    # Response tracking
    tenant_response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    
    # Staff information
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_house_reminders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'House Rent Reminder'
        verbose_name_plural = 'House Rent Reminders'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['booking', 'reminder_sequence']),
            models.Index(fields=['scheduled_date', 'reminder_status']),
            models.Index(fields=['due_date', 'is_overdue']),
        ]
    
    def __str__(self):
        return f"{self.get_reminder_type_display()} reminder #{self.reminder_sequence} for {self.property_obj.title}"
    
    def save(self, *args, **kwargs):
        # Auto-generate subject if not provided
        if not self.subject:
            if self.is_overdue:
                self.subject = f"Overdue Rent Reminder - {self.property_obj.title}"
            else:
                self.subject = f"Rent Payment Reminder - {self.property_obj.title}"
        
        super().save(*args, **kwargs)
    
    @property
    def is_due_for_sending(self):
        """Check if reminder is due to be sent"""
        from django.utils import timezone
        return (
            self.reminder_status == 'scheduled' and 
            self.scheduled_date <= timezone.now()
        )
    
    @property
    def days_overdue(self):
        """Calculate days overdue if applicable"""
        from django.utils import timezone
        if self.is_overdue and self.due_date < timezone.now().date():
            return (timezone.now().date() - self.due_date).days
        return 0
    
    def mark_as_sent(self, delivery_reference=None, delivery_status='delivered'):
        """Mark reminder as sent"""
        from django.utils import timezone
        self.reminder_status = 'sent'
        self.sent_date = timezone.now()
        self.delivery_reference = delivery_reference or ''
        self.delivery_status = delivery_status
        self.save()
    
    def mark_as_failed(self, error_message):
        """Mark reminder as failed"""
        self.reminder_status = 'failed'
        self.delivery_error = error_message
        self.save()


class HouseRentReminderTemplate(models.Model):
    """
    Email and SMS templates for rent reminders
    """
    TEMPLATE_TYPE_CHOICES = [
        ('email', 'Email Template'),
        ('sms', 'SMS Template'),
        ('push', 'Push Notification Template'),
    ]
    
    REMINDER_CATEGORY_CHOICES = [
        ('upcoming', 'Upcoming Payment'),
        ('overdue_1', 'First Overdue'),
        ('overdue_2', 'Second Overdue'),
        ('overdue_3', 'Third Overdue'),
        ('final_notice', 'Final Notice'),
        ('escalation', 'Escalation Notice'),
    ]
    
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=REMINDER_CATEGORY_CHOICES)
    
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Template variables help text
    variables_help = models.TextField(
        blank=True,
        help_text="Available variables: {{tenant_name}}, {{property_title}}, {{due_date}}, {{amount}}, {{days_overdue}}, etc."
    )
    
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Default template for this category"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rent Reminder Template'
        verbose_name_plural = 'Rent Reminder Templates'
        unique_together = ['template_type', 'category', 'is_default']
        ordering = ['template_type', 'category']
    
    def __str__(self):
        return f"{self.get_template_type_display()} - {self.get_category_display()}"
    
    def render_template(self, context):
        """Render template with provided context"""
        try:
            from django.template import Template, Context
            template = Template(self.content)
            return template.render(Context(context))
        except Exception as e:
            return f"Template rendering error: {str(e)}"


class HouseRentReminderLog(models.Model):
    """
    Detailed logging for rent reminder activities
    """
    ACTION_CHOICES = [
        ('created', 'Reminder Created'),
        ('scheduled', 'Reminder Scheduled'),
        ('sent', 'Reminder Sent'),
        ('failed', 'Reminder Failed'),
        ('cancelled', 'Reminder Cancelled'),
        ('escalated', 'Escalated'),
        ('payment_received', 'Payment Received'),
        ('tenant_response', 'Tenant Response'),
    ]
    
    reminder = models.ForeignKey(
        HouseRentReminder, 
        on_delete=models.CASCADE, 
        related_name='logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    # User who performed the action
    performed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='reminder_logs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Rent Reminder Log'
        verbose_name_plural = 'Rent Reminder Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.reminder}"


class HouseRentReminderSchedule(models.Model):
    """
    Automated scheduling for rent reminders
    """
    SCHEDULE_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),
        ('custom', 'Custom'),
    ]
    
    property_obj = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='reminder_schedules',
        limit_choices_to={'property_type__name__iexact': 'house'}
    )
    
    schedule_name = models.CharField(max_length=100)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES)
    
    # Timing settings
    days_before_due = models.IntegerField(default=7)
    overdue_interval_days = models.IntegerField(default=3)
    max_reminders = models.IntegerField(default=5)
    
    # Enabled reminder types
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    
    # Schedule timing
    send_time = models.TimeField(default='09:00:00')
    timezone = models.CharField(max_length=50, default='Africa/Dar_es_Salaam')
    
    # Custom schedule settings
    custom_days = models.JSONField(
        default=list, 
        blank=True,
        help_text="Custom days for custom schedule type"
    )
    
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rent Reminder Schedule'
        verbose_name_plural = 'Rent Reminder Schedules'
        ordering = ['property_obj', 'schedule_name']
    
    def __str__(self):
        return f"{self.schedule_name} for {self.property_obj.title}"
    
    def calculate_next_run(self):
        """Calculate next run time based on schedule type"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.schedule_type == 'daily':
            next_run = now.replace(
                hour=self.send_time.hour,
                minute=self.send_time.minute,
                second=0,
                microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif self.schedule_type == 'weekly':
            # Run on Mondays
            days_ahead = 7 - now.weekday()
            if days_ahead == 7:
                days_ahead = 0
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(
                hour=self.send_time.hour,
                minute=self.send_time.minute,
                second=0,
                microsecond=0
            )
        
        elif self.schedule_type == 'monthly':
            # Run on 1st of each month
            if now.day == 1:
                next_run = now.replace(
                    hour=self.send_time.hour,
                    minute=self.send_time.minute,
                    second=0,
                    microsecond=0
                )
            else:
                # Next month's 1st
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=1)
                else:
                    next_run = now.replace(month=now.month + 1, day=1)
                next_run = next_run.replace(
                    hour=self.send_time.hour,
                    minute=self.send_time.minute,
                    second=0,
                    microsecond=0
                )
        
        else:  # custom
            # For custom schedules, you'd implement custom logic here
            next_run = now + timedelta(days=1)
        
        self.next_run = next_run
        self.save()
        return next_run