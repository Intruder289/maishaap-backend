from django.db import models
from django.conf import settings
from django.contrib.auth.models import Permission


def user_profile_image_path(instance, filename):
	# file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	return f'user_{instance.user.id}/{filename}'


class Profile(models.Model):
	ROLE_CHOICES = [
		('tenant', 'Tenant'),
		('owner', 'Property Owner'),
	]
	
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	phone = models.CharField(max_length=30, blank=True, null=True, unique=True)
	image = models.ImageField(upload_to=user_profile_image_path, null=True, blank=True)
	role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
	is_approved = models.BooleanField(default=False)
	approved_at = models.DateTimeField(null=True, blank=True)
	approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_profiles')
	# Multi-tenancy: Deactivation fields for admin control
	is_deactivated = models.BooleanField(default=False, help_text="If True, user cannot login and will see deactivation message")
	deactivation_reason = models.TextField(blank=True, null=True, help_text="Reason for deactivation (shown to user on login attempt)")
	deactivated_at = models.DateTimeField(null=True, blank=True)
	deactivated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deactivated_profiles')

	def __str__(self):
		return f'Profile for {self.user.get_username()}'

	def get_user_roles(self):
		"""Get all custom roles assigned to this user"""
		return CustomRole.objects.filter(userrole__user=self.user)
	
	def has_role(self, role_name):
		"""Check if user has a specific role"""
		return self.get_user_roles().filter(name=role_name).exists()
	
	def get_primary_role(self):
		"""Get the primary role for display (highest priority)"""
		if self.user.is_superuser:
			return 'Admin'
		
		roles = self.get_user_roles().values_list('name', flat=True)
		
		# Priority order
		for role_name in ['Admin', 'Manager', 'Property owner']:
			if role_name in roles:
				return role_name
		
		# Fallback to Django groups for backward compatibility
		groups = self.user.groups.values_list('name', flat=True)
		for role_name in ['Admin', 'Manager', 'Property manager', 'Property owner']:
			if role_name in groups:
				return role_name if role_name != 'Property manager' else 'Manager'
		
		# Final fallback to profile.role (tenant/owner) for backward compatibility
		if self.role == 'owner':
			return 'Property Owner'
		elif self.role == 'tenant':
			return 'Tenant'
		
		return None


class CustomRole(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)
	permissions = models.ManyToManyField(Permission, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	class Meta:
		ordering = ['name']


class UserRole(models.Model):
	"""Model to track user role assignments"""
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles')
	role = models.ForeignKey(CustomRole, on_delete=models.CASCADE)
	assigned_at = models.DateTimeField(auto_now_add=True)
	assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')

	class Meta:
		unique_together = ['user', 'role']
		ordering = ['assigned_at']

	def __str__(self):
		return f'{self.user.username} - {self.role.name}'


class NavigationItem(models.Model):
	"""Model to define navigation items in the sidebar"""
	name = models.CharField(max_length=100, unique=True)
	display_name = models.CharField(max_length=100)
	url_name = models.CharField(max_length=100, blank=True, help_text="Django URL name")
	icon = models.TextField(help_text="HTML icon code (SVG or FontAwesome)")
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
	order = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['order', 'name']

	def __str__(self):
		return self.display_name


class RoleNavigationPermission(models.Model):
	"""Model to define which navigation items each role can access"""
	role = models.ForeignKey(CustomRole, on_delete=models.CASCADE, related_name='navigation_permissions')
	navigation_item = models.ForeignKey(NavigationItem, on_delete=models.CASCADE, related_name='role_permissions')
	can_access = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ['role', 'navigation_item']
		ordering = ['role__name', 'navigation_item__order']

	def __str__(self):
		access = "can access" if self.can_access else "cannot access"
		return f'{self.role.name} {access} {self.navigation_item.display_name}'


class ActivityLog(models.Model):
	"""Model to track recent activities across the system"""
	ACTION_CHOICES = [
		('create', 'Created'),
		('update', 'Updated'),
		('delete', 'Deleted'),
		('login', 'Login'),
		('logout', 'Logout'),
		('payment', 'Payment'),
		('booking', 'Booking'),
		('complaint', 'Complaint'),
		('maintenance', 'Maintenance'),
		('lease', 'Lease'),
		('document', 'Document'),
	]
	
	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High'),
		('urgent', 'Urgent'),
	]
	
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
	action = models.CharField(max_length=20, choices=ACTION_CHOICES)
	description = models.TextField()
	content_type = models.CharField(max_length=50, help_text="Type of object (Property, Payment, etc.)")
	object_id = models.PositiveIntegerField(null=True, blank=True)
	priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
	amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Amount in TZS")
	metadata = models.JSONField(default=dict, blank=True, help_text="Additional data as JSON")
	timestamp = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)
	
	class Meta:
		ordering = ['-timestamp']
		indexes = [
			models.Index(fields=['-timestamp']),
			models.Index(fields=['user', '-timestamp']),
			models.Index(fields=['action', '-timestamp']),
		]
	
	def __str__(self):
		return f'{self.user.username} - {self.get_action_display()}: {self.description[:50]}'
	
	def get_display_amount(self):
		"""Return formatted amount in TZS"""
		if self.amount:
			return f"TZS {self.amount:,.2f}"
		return None
	
	def get_time_since(self):
		"""Return human-readable time since activity"""
		from django.utils import timezone
		from datetime import timedelta
		
		now = timezone.now()
		diff = now - self.timestamp
		
		if diff < timedelta(minutes=1):
			return "Just now"
		elif diff < timedelta(hours=1):
			return f"{diff.seconds // 60} minutes ago"
		elif diff < timedelta(days=1):
			return f"{diff.seconds // 3600} hours ago"
		elif diff < timedelta(weeks=1):
			return f"{diff.days} days ago"
		else:
			return f"{diff.days // 7} weeks ago"


class Notification(models.Model):
	"""Model for system notifications, including password reset requests"""
	NOTIFICATION_TYPES = [
		('password_reset', 'Password Reset Request'),
		('user_approval', 'User Approval'),
		('payment', 'Payment'),
		('complaint', 'Complaint'),
		('maintenance', 'Maintenance'),
		('system', 'System'),
	]
	
	notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
	title = models.CharField(max_length=200)
	message = models.TextField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications', help_text="User who requested (for password reset)")
	related_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='related_notifications', help_text="Related user (e.g., user requesting password reset)")
	is_read = models.BooleanField(default=False)
	read_at = models.DateTimeField(null=True, blank=True)
	read_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='read_notifications')
	created_at = models.DateTimeField(auto_now_add=True)
	metadata = models.JSONField(default=dict, blank=True, help_text="Additional data as JSON")
	
	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['-created_at']),
			models.Index(fields=['is_read', '-created_at']),
			models.Index(fields=['notification_type', '-created_at']),
		]
	
	def __str__(self):
		return f'{self.get_notification_type_display()}: {self.title}'
	
	def mark_as_read(self, user):
		"""Mark notification as read"""
		from django.utils import timezone
		self.is_read = True
		self.read_at = timezone.now()
		self.read_by = user
		self.save()
	
	def get_time_since(self):
		"""Return human-readable time since notification"""
		from django.utils import timezone
		from datetime import timedelta
		
		now = timezone.now()
		diff = now - self.created_at
		
		if diff < timedelta(minutes=1):
			return "Just now"
		elif diff < timedelta(hours=1):
			return f"{diff.seconds // 60} minutes ago"
		elif diff < timedelta(days=1):
			return f"{diff.seconds // 3600} hours ago"
		elif diff < timedelta(weeks=1):
			return f"{diff.days} days ago"
		else:
			return f"{diff.days // 7} weeks ago"
	
	@classmethod
	def get_unread_count(cls, user=None):
		"""Get count of unread notifications for admins"""
		from django.contrib.auth.models import User
		# Only show notifications to superusers/staff (admins)
		if user and (user.is_superuser or user.is_staff):
			return cls.objects.filter(is_read=False).count()
		return 0
