from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group, Permission
from .models import Profile, CustomRole, UserRole, Notification
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django import forms
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import os

# DRF imports for API views
try:
    from rest_framework.decorators import api_view
    from rest_framework.response import Response
    from rest_framework import status
    DRF_AVAILABLE = True
except ImportError:
    DRF_AVAILABLE = False
    
# Firebase integration removed (unused)



def login_view(request):
	"""Allow users to log in using email and password."""
	# Check if session was expired
	if request.session.get('session_expired'):
		messages.warning(request, 'Your session has expired due to inactivity. Please log in again.')
		del request.session['session_expired']
	
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')

		# Find user by email
		try:
			user_obj = User.objects.get(email__iexact=email)
			username = user_obj.get_username()
		except User.DoesNotExist:
			username = None
		except User.MultipleObjectsReturned:
			# Handle multiple users with same email - get the most recent one
			user_obj = User.objects.filter(email__iexact=email).order_by('-date_joined').first()
			username = user_obj.get_username() if user_obj else None
			messages.warning(request, 'Multiple accounts found with this email. Using the most recent account.')

		if username:
			user = authenticate(request, username=username, password=password)
			if user is not None:
				# Check if user is deactivated (MULTI-TENANCY: Admin control)
				if hasattr(user, 'profile') and user.profile.is_deactivated:
					reason = user.profile.deactivation_reason or "due to contract issues or some disagreement"
					messages.error(request, f"Your account has been deactivated. {reason}. Please contact the administrator for more information.")
					return render(request, 'accounts/login.html')
				
				login(request, user)
				# Set initial last activity time on login
				from django.utils import timezone
				request.session['last_activity'] = timezone.now().isoformat()
				return redirect('accounts:dashboard')

		messages.error(request, 'Invalid email or password')

	return render(request, 'accounts/login.html')


def logout_view(request):
	# Clear all existing messages before logout
	storage = messages.get_messages(request)
	for message in storage:
		pass  # Consume all messages
	
	# Logout clears the session, which should also clear messages
	logout(request)
	
	# Flush the session to ensure everything is cleared
	request.session.flush()
	
	# Don't add any success message - just redirect to clean login page
	return redirect('accounts:login')


@login_required
def dashboard(request):
	from .utils import get_dashboard_stats, get_recent_activities, format_currency_tzs, log_activity
	from django.core.paginator import Paginator
	from django.db.models import Q
	from django.shortcuts import redirect
	
	# Get or create profile
	profile, created = Profile.objects.get_or_create(user=request.user)
	
	# Get primary role using the new role system
	role = profile.get_primary_role()
	
	# Check if user is a property owner (not admin/staff) and has properties
	# If so, redirect to their property-specific dashboard
	if not (request.user.is_staff or request.user.is_superuser):
		# Check if user is a Property Owner
		from accounts.models import UserRole
		is_property_owner = UserRole.objects.filter(
			user=request.user,
			role__name__in=['Property Owner', 'Property owner']
		).exists()
		
		# Also check profile role for backward compatibility
		if not is_property_owner and hasattr(request.user, 'profile'):
			is_property_owner = request.user.profile.role == 'owner'
		
		if is_property_owner:
			# Check what property types the owner has
			try:
				from properties.models import Property
				owner_properties = Property.objects.filter(owner=request.user)
				
				if owner_properties.exists():
					# Get the first property type (prioritize hotel > lodge > venue > house)
					property_types = owner_properties.values_list('property_type__name', flat=True).distinct()
					
					# Priority order: hotel > lodge > venue > house
					if any(pt and pt.lower() == 'hotel' for pt in property_types):
						return redirect('properties:hotel_dashboard')
					elif any(pt and pt.lower() == 'lodge' for pt in property_types):
						return redirect('properties:lodge_dashboard')
					elif any(pt and pt.lower() == 'venue' for pt in property_types):
						return redirect('properties:venue_dashboard')
					elif any(pt and pt.lower() == 'house' for pt in property_types):
						return redirect('properties:house_dashboard')
			except ImportError as e:
				import logging
				logger = logging.getLogger(__name__)
				logger.warning(f"Properties app not available: {str(e)}. Continuing to regular dashboard.")
	
	# Log dashboard access activity
	log_activity(
		user=request.user,
		action='login',
		description=f'{request.user.get_full_name() or request.user.username} accessed dashboard',
		content_type='Dashboard',
		priority='low'
	)
	
	# Get dynamic dashboard statistics
	stats = get_dashboard_stats(request.user)
	
	# Get recent activities for display
	recent_activities = get_recent_activities(request.user, limit=10)
	
	# Get properties with pagination and search
	properties = []
	page_obj = None
	
	try:
		from properties.models import Property
		
		# Base queryset
		if request.user.is_staff or request.user.is_superuser:
			properties = Property.objects.select_related('property_type', 'region', 'owner').prefetch_related('images').exclude(status='unavailable')
		else:
			properties = Property.objects.filter(owner=request.user).select_related('property_type', 'region', 'owner').prefetch_related('images').exclude(status='unavailable')
		
		# Search functionality
		search_query = request.GET.get('search', '')
		if search_query:
			properties = properties.filter(
				Q(title__icontains=search_query) |
				Q(property_type__name__icontains=search_query) |
				Q(region__name__icontains=search_query) |
				Q(address__icontains=search_query)
			)
		
		# Order by creation date (most recent first)
		properties = properties.order_by('-created_at')
		
		# Pagination
		per_page = request.GET.get('per_page', '5')
		try:
			per_page = int(per_page)
			if per_page not in [5, 10, 25, 50]:
				per_page = 5
		except (ValueError, TypeError):
			per_page = 5
		
		paginator = Paginator(properties, per_page)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		
	except ImportError:
		pass
	
	# Calculate pending requests (maintenance + complaints)
	pending_requests = stats['maintenance_requests'] + stats['recent_complaints']
	
	# Calculate growth percentages (mock for now - you can implement real calculations)
	property_growth = "+12%" if stats['total_properties'] > 0 else "0%"
	tenant_growth = "+5 new this week" if stats['active_tenants'] > 0 else "No new tenants"
	revenue_growth = "+8.2% vs last month" if stats['monthly_revenue'] > 0 else "No revenue"

	return render(request, 'accounts/dashboard.html', {
		'user_role': role,
		'profile': profile,
		'stats': stats,
		'recent_activities': recent_activities,
		'page_obj': page_obj,
		'pending_requests': pending_requests,
		'property_growth': property_growth,
		'tenant_growth': tenant_growth,
		'revenue_growth': revenue_growth,
		'format_currency': format_currency_tzs,
		'per_page': per_page,
		'per_page_options': [5, 10, 25, 50],
		'search_query': request.GET.get('search', ''),
		# Backward compatibility
		'unpaid_invoices_count': stats['unpaid_invoices'],
		'active_leases_count': stats['active_leases'],
		'pending_bookings_count': stats['pending_bookings'],
	})


def has_role(user, role_name):
	"""Check if user has a specific role"""
	if not user.is_authenticated:
		return False
	
	if user.is_superuser and role_name == 'Admin':
		return True
		
	try:
		# Check CustomRole assignments
		role_assigned = UserRole.objects.filter(
			user=user, 
			role__name=role_name
		).exists()
		
		if role_assigned:
			return True
		
		# Fallback to Django groups for backward compatibility
		return user.groups.filter(name=role_name).exists()
	except Exception as e:
		import logging
		logger = logging.getLogger(__name__)
		logger.error(f"Error checking role '{role_name}' for user {user.username}: {str(e)}")
		return False


def is_admin(user):
	"""Check if user has admin or manager role - Managers have restricted access inside views"""
	if not user.is_authenticated:
		return False
	# Allow both Admin and Manager - restrictions are applied inside individual views
	return has_role(user, 'Admin') or is_manager(user)


def is_manager(user):
	"""Check if user has manager role (standardized - checks both 'Manager' and 'Property manager' for backward compatibility)"""
	if not user.is_authenticated:
		return False
	# Check both 'Manager' and 'Property manager' for backward compatibility
	return has_role(user, 'Manager') or has_role(user, 'Property manager')


def is_property_owner(user):
	"""Check if user has property owner role"""
	return has_role(user, 'Property owner')


@login_required
def dashboard_properties_ajax(request):
	"""AJAX endpoint for dashboard properties search and pagination"""
	from django.core.paginator import Paginator
	from django.db.models import Q
	from django.http import JsonResponse
	import json
	
	try:
		from properties.models import Property
		
		# Base queryset
		if request.user.is_staff or request.user.is_superuser:
			properties = Property.objects.select_related('property_type', 'region', 'owner').prefetch_related('images').exclude(status='unavailable')
		else:
			properties = Property.objects.filter(owner=request.user).select_related('property_type', 'region', 'owner').prefetch_related('images').exclude(status='unavailable')
		
		# Search functionality
		search_query = request.GET.get('search', '')
		if search_query:
			properties = properties.filter(
				Q(title__icontains=search_query) |
				Q(property_type__name__icontains=search_query) |
				Q(region__name__icontains=search_query) |
				Q(address__icontains=search_query)
			)
		
		# Order by creation date (most recent first)
		properties = properties.order_by('-created_at')
		
		# Pagination
		per_page = request.GET.get('per_page', '5')
		try:
			per_page = int(per_page)
			if per_page not in [5, 10, 25, 50]:
				per_page = 5
		except (ValueError, TypeError):
			per_page = 5
		
		paginator = Paginator(properties, per_page)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		
		# Prepare response data
		properties_data = []
		for property in page_obj:
			property_data = {
				'id': property.id,
				'title': property.title,
				'property_type': property.property_type.name,
				'region': property.region.name,
				'rent_amount': float(property.rent_amount),
				'status': property.status,
				'image_url': property.images.first().image.url if property.images.exists() else None,
				'created_at': property.created_at.strftime('%Y-%m-%d %H:%M'),
			}
			properties_data.append(property_data)
		
		response_data = {
			'properties': properties_data,
			'pagination': {
				'current_page': page_obj.number,
				'total_pages': paginator.num_pages,
				'has_previous': page_obj.has_previous(),
				'has_next': page_obj.has_next(),
				'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
				'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
				'start_index': page_obj.start_index(),
				'end_index': page_obj.end_index(),
				'total_count': paginator.count,
				'per_page': per_page,
			},
			'search_query': search_query,
		}
		
		return JsonResponse(response_data)
		
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)


def require_role(role_name):
	"""Decorator to require a specific role"""
	def decorator(view_func):
		@wraps(view_func)
		def wrapper(request, *args, **kwargs):
			if not request.user.is_authenticated:
				return redirect('accounts:login')
			
			if not has_role(request.user, role_name):
				messages.error(request, f'Access denied. {role_name} role required.')
				return redirect('accounts:dashboard')
			
			return view_func(request, *args, **kwargs)
		return wrapper
	return decorator


def require_any_role(*role_names):
	"""Decorator to require any of the specified roles"""
	def decorator(view_func):
		@wraps(view_func)
		def wrapper(request, *args, **kwargs):
			if not request.user.is_authenticated:
				return redirect('accounts:login')
			
			user_has_role = any(has_role(request.user, role) for role in role_names)
			
			if not user_has_role:
				roles_str = ', '.join(role_names)
				messages.error(request, f'Access denied. One of these roles required: {roles_str}')
				return redirect('accounts:dashboard')
			
			return view_func(request, *args, **kwargs)
		return wrapper
	return decorator


@login_required
@user_passes_test(is_admin)
def user_list(request):
	# Get search and filter parameters
	search_query = request.GET.get('search', '')
	status_filter = request.GET.get('status', '')
	role_filter = request.GET.get('role', '')
	
	# Check if user is Manager (not Admin)
	is_manager_user = is_manager(request.user)
	
	# Start with all users with their profiles
	# Managers can only see users they created (via UserRole.assigned_by or Profile.approved_by)
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		# Get users created by this Manager
		# Users where Manager assigned a role OR approved the profile
		users_created_by_manager = User.objects.filter(
			Q(user_roles__assigned_by=request.user) |
			Q(profile__approved_by=request.user)
		).distinct()
		users = users_created_by_manager.select_related('profile').prefetch_related('user_roles__role')
	else:
		# Admin/Staff: see all users (but filter inactive by default)
		users = User.objects.select_related('profile').prefetch_related('user_roles__role').all()
	
	# Apply search filter
	if search_query:
		users = users.filter(
			Q(first_name__icontains=search_query) |
			Q(last_name__icontains=search_query) |
			Q(username__icontains=search_query) |
			Q(email__icontains=search_query)
		)
	
	# Apply status filter
	# Default: show only active users unless explicitly filtering for inactive
	if status_filter == 'inactive':
		users = users.filter(is_active=False)
	elif status_filter == 'active':
		users = users.filter(is_active=True)
	elif status_filter == 'approved':
		users = users.filter(profile__is_approved=True, is_active=True)
	elif status_filter == 'pending':
		users = users.filter(profile__is_approved=False, is_active=True)
	else:
		# Default: only show active users
		users = users.filter(is_active=True)
	
	# Apply role filter
	if role_filter:
		if role_filter == 'tenant':
			users = users.filter(profile__role='tenant')
		elif role_filter == 'owner':
			users = users.filter(profile__role='owner')
		elif role_filter == 'admin':
			users = users.filter(is_superuser=True)
		elif role_filter == 'staff':
			users = users.filter(is_staff=True)
	
	# Order by date joined (newest first)
	users = users.order_by('-date_joined')
	
	# Pagination
	from django.core.paginator import Paginator
	paginator = Paginator(users, 5)  # 5 users per page
	page_obj = paginator.get_page(request.GET.get('page'))
	
	# Get user's profile
	profile, created = Profile.objects.get_or_create(user=request.user)
	
	# Get statistics - Managers only see stats for their created users
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		manager_users = users
		total_users = manager_users.count()
		active_users = manager_users.filter(is_active=True).count()
		approved_users = manager_users.filter(profile__is_approved=True).count()
		pending_users = manager_users.filter(profile__is_approved=False).count()
	else:
		# Admin/Staff: see all stats
		total_users = User.objects.count()
		active_users = User.objects.filter(is_active=True).count()
		approved_users = User.objects.filter(profile__is_approved=True).count()
		pending_users = User.objects.filter(profile__is_approved=False).count()
	
	return render(request, 'accounts/user_list.html', {
		'users': page_obj,
		'page_obj': page_obj,
		'profile': profile,
		'total_users': total_users,
		'active_users': active_users,
		'approved_users': approved_users,
		'pending_users': pending_users,
		'search_query': search_query,
		'status_filter': status_filter,
		'role_filter': role_filter,
	})


@login_required
@user_passes_test(is_admin)
def create_user(request):
	# Managers cannot create users via web interface - only via API
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		messages.error(request, 'Managers can only create Property Owner accounts via the mobile API.')
		return redirect('accounts:user_list')
	
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip().lower()
		first_name = request.POST.get('first_name', '').strip()
		last_name = request.POST.get('last_name', '').strip()
		password = request.POST.get('password', '')
		confirm_password = request.POST.get('confirm_password', '')
		is_active = request.POST.get('is_active') == 'on'
		is_staff = request.POST.get('is_staff') == 'on'
		selected_roles = request.POST.getlist('roles')
		
		# Validation
		errors = []
		
		# Required fields
		if not username:
			errors.append('Username is required.')
		elif len(username) < 3:
			errors.append('Username must be at least 3 characters long.')
		elif len(username) > 150:
			errors.append('Username must be less than 150 characters.')
		elif not username.replace('_', '').replace('.', '').isalnum():
			errors.append('Username can only contain letters, numbers, underscores, and periods.')
		
		if not email:
			errors.append('Email is required.')
		else:
			# Email format validation
			from django.core.validators import validate_email
			from django.core.exceptions import ValidationError
			try:
				validate_email(email)
			except ValidationError:
				errors.append('Please enter a valid email address.')
		
		if not password:
			errors.append('Password is required.')
		elif len(password) < 8:
			errors.append('Password must be at least 8 characters long.')
		elif password != confirm_password:
			errors.append('Passwords do not match.')
		else:
			# Password strength validation
			has_upper = any(c.isupper() for c in password)
			has_lower = any(c.islower() for c in password)
			has_digit = any(c.isdigit() for c in password)
			has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
			
			if not (has_upper and has_lower and has_digit):
				errors.append('Password must contain at least one uppercase letter, one lowercase letter, and one number.')
		
		# Check for existing username
		if username and User.objects.filter(username=username).exists():
			errors.append('Username already exists.')
		
		# Check for existing email
		if email and User.objects.filter(email__iexact=email).exists():
			errors.append('Email already exists.')
		
		# Validate role IDs
		if selected_roles:
			from .models import CustomRole
			valid_role_ids = set(CustomRole.objects.values_list('id', flat=True))
			selected_role_ids = [int(rid) for rid in selected_roles if rid.isdigit()]
			invalid_roles = [rid for rid in selected_role_ids if rid not in valid_role_ids]
			if invalid_roles:
				errors.append(f'Invalid role IDs selected: {invalid_roles}')
		
		if errors:
			for error in errors:
				messages.error(request, error)
		else:
			try:
				with transaction.atomic():
					# Create user
					user = User.objects.create_user(
						username=username,
						email=email,
						password=password,
						first_name=first_name,
						last_name=last_name,
						is_active=is_active,
						is_staff=is_staff
					)
					
					# Create profile
					Profile.objects.create(user=user)
					
					# Assign roles
					for role_id in selected_roles:
						try:
							role = CustomRole.objects.get(id=role_id)
							UserRole.objects.create(
								user=user,
								role=role,
								assigned_by=request.user
							)
						except CustomRole.DoesNotExist:
							continue
					
					messages.success(request, f'User "{username}" created successfully.')
					return redirect('accounts:user_list')
			except Exception as e:
				messages.error(request, f'Error creating user: {str(e)}')
	
	# Get all available roles except Admin (only superusers can assign Admin)
	if request.user.is_superuser:
		available_roles = CustomRole.objects.all()
	else:
		available_roles = CustomRole.objects.exclude(name='Admin')
	
	profile, created = Profile.objects.get_or_create(user=request.user)
	return render(request, 'accounts/create_user.html', {
		'available_roles': available_roles,
		'profile': profile
	})


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
	"""Edit user profile information"""
	user_obj = get_object_or_404(User, pk=user_id)
	profile, created = Profile.objects.get_or_create(user=user_obj)
	
	# Check if user is Manager (not Admin)
	is_manager_user = is_manager(request.user)
	
	# Managers can only edit users they created
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		# Check if this user was created by the Manager
		user_created_by_manager = (
			UserRole.objects.filter(user=user_obj, assigned_by=request.user).exists() or
			(hasattr(user_obj, 'profile') and user_obj.profile.approved_by == request.user)
		)
		
		if not user_created_by_manager:
			messages.error(request, 'You can only edit users you created.')
			return redirect('accounts:user_list')
	
	if request.method == 'POST':
		errors = []
		
		# Update user fields with validation
		first_name = request.POST.get('first_name', '').strip()
		last_name = request.POST.get('last_name', '').strip()
		email = request.POST.get('email', '').strip().lower()
		
		if first_name:
			user_obj.first_name = first_name
		if last_name:
			user_obj.last_name = last_name
		
		if email:
			# Email format validation
			from django.core.validators import validate_email
			from django.core.exceptions import ValidationError
			try:
				validate_email(email)
				# Check if email is taken by another user
				if User.objects.filter(email__iexact=email).exclude(id=user_obj.id).exists():
					errors.append('Email is already taken by another user.')
				else:
					user_obj.email = email
			except ValidationError:
				errors.append('Please enter a valid email address.')
		
		# Prevent non-superusers from making users superuser
		if request.POST.get('is_staff') == 'on':
			if not request.user.is_superuser and user_obj.is_superuser:
				errors.append('Only superusers can modify superuser status.')
			else:
				user_obj.is_staff = True
		else:
			# Prevent removing superuser status unless current user is superuser
			if user_obj.is_superuser and not request.user.is_superuser:
				errors.append('You cannot modify superuser accounts.')
			else:
				user_obj.is_staff = False
		
		user_obj.is_active = request.POST.get('is_active') == 'on'
		
		# Update profile fields
		phone = request.POST.get('phone', '').strip()
		if phone:
			profile.phone = phone
		
		role = request.POST.get('role', '').strip()
		if role in ['tenant', 'owner', 'admin']:
			profile.role = role
		
		# Handle profile image upload with validation
		if 'image' in request.FILES:
			image = request.FILES['image']
			# Validate file size (max 5MB)
			if image.size > 5 * 1024 * 1024:
				errors.append('Profile image size must be less than 5MB.')
			else:
				# Validate file type
				allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
				if image.content_type not in allowed_types:
					errors.append('Please upload a valid image file (JPEG, PNG, GIF, WebP).')
				else:
					profile.image = image
		
		if errors:
			for error in errors:
				messages.error(request, error)
		else:
			user_obj.save()
			profile.save()
			messages.success(request, f'User {user_obj.username} updated successfully!')
		
		return redirect('accounts:user_list')
	
	# Get available roles for assignment
	if request.user.is_superuser:
		available_roles = CustomRole.objects.all()
	else:
		available_roles = CustomRole.objects.exclude(name='Admin')
	
	current_user_profile, created = Profile.objects.get_or_create(user=request.user)
	return render(request, 'accounts/edit_user.html', {
		'user_obj': user_obj,
		'profile': profile,
		'available_roles': available_roles,
		'current_user_profile': current_user_profile
	})


@login_required
@user_passes_test(is_admin)
def user_profile_view(request, user_id):
	"""View user profile details"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Check if user is Manager - Managers can only view users they created
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		# Check if this user was created by the Manager
		user_created_by_manager = (
			UserRole.objects.filter(user=user_obj, assigned_by=request.user).exists() or
			(hasattr(user_obj, 'profile') and user_obj.profile.approved_by == request.user)
		)
		
		if not user_created_by_manager:
			messages.error(request, 'You can only view users you created.')
			return redirect('accounts:user_list')
	
	# Use select_related to ensure we get the latest profile data
	try:
		profile = user_obj.profile
	except Profile.DoesNotExist:
		profile = Profile.objects.create(user=user_obj)
	
	# Refresh profile from database to ensure latest data
	profile.refresh_from_db()
	
	# Get user's roles
	from .models import UserRole
	user_roles = UserRole.objects.filter(user=user_obj)
	
	# Get recent activities (if ActivityLog model exists)
	recent_activities = []
	try:
		from .models import ActivityLog
		recent_activities = ActivityLog.objects.filter(user=user_obj).order_by('-timestamp')[:10]
	except Exception as e:
		import logging
		logger = logging.getLogger(__name__)
		logger.debug(f"ActivityLog model not available or error loading activities: {str(e)}")
		recent_activities = []
	
	# Get properties owned by this user (if they are a property owner)
	owner_properties = []
	is_property_owner = False
	try:
		# Check if user is a property owner
		is_property_owner = (
			UserRole.objects.filter(user=user_obj, role__name__in=['Property Owner', 'Property owner']).exists() or
			(hasattr(user_obj, 'profile') and user_obj.profile.role == 'owner')
		)
		
		if is_property_owner:
			from properties.models import Property
			owner_properties = Property.objects.filter(owner=user_obj).select_related(
				'property_type', 'region'
			).prefetch_related('images').order_by('-created_at')
	except Exception as e:
		import logging
		logger = logging.getLogger(__name__)
		logger.debug(f"Error loading properties: {str(e)}")
		owner_properties = []
	
	current_user_profile, created = Profile.objects.get_or_create(user=request.user)
	return render(request, 'accounts/user_profile.html', {
		'user_obj': user_obj,
		'profile': profile,
		'user_roles': user_roles,
		'recent_activities': recent_activities,
		'current_user_profile': current_user_profile,
		'owner_properties': owner_properties,
		'is_property_owner': is_property_owner,
		'properties_count': len(owner_properties) if owner_properties else 0
	})


@login_required
@user_passes_test(is_admin)
def edit_user_roles(request, user_id):
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Check if user is Manager - Managers cannot assign/update roles
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		messages.error(request, 'Managers cannot assign or update user roles.')
		return redirect('accounts:user_list')
	
	# Get all available roles except Admin (only superusers can assign Admin)
	if request.user.is_superuser:
		available_roles = CustomRole.objects.all()
	else:
		available_roles = CustomRole.objects.exclude(name='Admin')
	
	# Get currently assigned roles
	from .models import UserRole
	current_roles = UserRole.objects.filter(user=user_obj)

	if request.method == 'POST':
		selected_role_ids = request.POST.getlist('roles')
		
		# Clear existing role assignments
		UserRole.objects.filter(user=user_obj).delete()
		
		# Add new role assignments
		for role_id in selected_role_ids:
			try:
				role = CustomRole.objects.get(pk=role_id)
				UserRole.objects.get_or_create(
					user=user_obj,
					role=role,
					defaults={'assigned_by': request.user}
				)
			except CustomRole.DoesNotExist:
				messages.warning(request, f'Invalid role selected.')
		
		# Also sync with Django groups for backward compatibility
		selected_roles = CustomRole.objects.filter(pk__in=selected_role_ids)
		role_names = [role.name for role in selected_roles]
		
		# Handle Manager -> Property manager mapping
		group_names = []
		for name in role_names:
			group_names.append(name)
			if name == 'Manager':
				group_names.append('Property manager')
		
		user_obj.groups.clear()
		for name in group_names:
			group, _ = Group.objects.get_or_create(name=name)
			user_obj.groups.add(group)
		
		messages.success(request, f'Roles updated for {user_obj.username}')
		return redirect('accounts:user_list')

	profile, created = Profile.objects.get_or_create(user=request.user)
	template_name = 'accounts/user_roles_modal.html'
	return render(request, template_name, {
		'user_obj': user_obj, 
		'available_roles': available_roles,
		'current_roles': current_roles,
		'profile': profile
	})


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
	"""Delete a user (admin only - Managers cannot delete)"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Managers cannot delete users
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		messages.error(request, 'Managers cannot delete users.')
		return redirect('accounts:user_list')
	
	# Prevent deletion of superusers by non-superusers
	# Allow superusers to delete other accounts (including other superusers)
	if user_obj.is_superuser and not request.user.is_superuser:
		messages.error(request, 'You cannot delete a superuser. Only superusers can delete superuser accounts.')
		return redirect('accounts:user_list')
	
	# Prevent users from deleting themselves
	if user_obj == request.user:
		messages.error(request, 'You cannot delete your own account.')
		return redirect('accounts:user_list')
	
	if request.method == 'POST':
		try:
			username = user_obj.username
			user_obj.delete()
			messages.success(request, f'User "{username}" has been deleted successfully.')
		except Exception as e:
			messages.error(request, f'Error deleting user: {str(e)}')
	
	return redirect('accounts:user_list')


@login_required
@user_passes_test(is_admin)
def activate_user(request, user_id):
	"""Activate a user account (admin only - Managers can only activate their created users)"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Check if user is Manager - Managers can only activate users they created
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		# Check if this user was created by the Manager
		user_created_by_manager = (
			UserRole.objects.filter(user=user_obj, assigned_by=request.user).exists() or
			(hasattr(user_obj, 'profile') and user_obj.profile.approved_by == request.user)
		)
		
		if not user_created_by_manager:
			messages.error(request, 'You can only activate users you created.')
			return redirect('accounts:user_list')
	
	if request.method == 'POST':
		from django.utils import timezone
		
		user_obj.is_active = True
		user_obj.save()
		
		# Create profile if it doesn't exist and approve it
		profile, created = Profile.objects.get_or_create(user=user_obj)
		profile.is_approved = True
		profile.approved_at = timezone.now()
		profile.approved_by = request.user
		profile.save()
		
		messages.success(request, f'User "{user_obj.username}" has been activated and approved successfully.')
	
	return redirect('accounts:user_list')


@login_required
@user_passes_test(is_admin)
def deactivate_user(request, user_id):
	"""Deactivate a user account (admin only - Managers can only deactivate their created users)"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Check if user is Manager - Managers can only deactivate users they created
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		# Check if this user was created by the Manager
		user_created_by_manager = (
			UserRole.objects.filter(user=user_obj, assigned_by=request.user).exists() or
			(hasattr(user_obj, 'profile') and user_obj.profile.approved_by == request.user)
		)
		
		if not user_created_by_manager:
			messages.error(request, 'You can only deactivate users you created.')
			return redirect('accounts:user_list')
	
	# Prevent deactivation of superusers by non-superusers
	if user_obj.is_superuser and not request.user.is_superuser:
		messages.error(request, 'You cannot deactivate a superuser.')
		return redirect('accounts:user_list')
	
	# Prevent users from deactivating themselves
	if user_obj == request.user:
		messages.error(request, 'You cannot deactivate your own account.')
		return redirect('accounts:user_list')
	
	if request.method == 'POST':
		user_obj.is_active = False
		user_obj.save()
		
		# Also revoke profile approval when deactivating
		try:
			profile = user_obj.profile
			profile.is_approved = False
			profile.approved_at = None
			profile.approved_by = None
			profile.save()
		except Profile.DoesNotExist:
			pass
		
		messages.success(request, f'User "{user_obj.username}" has been deactivated successfully.')
	
	return redirect('accounts:user_list')


class ProfileForm(forms.ModelForm):
	first_name = forms.CharField(max_length=150, required=False)
	last_name = forms.CharField(max_length=150, required=False)
	email = forms.EmailField(required=False)
	
	class Meta:
		model = Profile
		fields = ['phone', 'image']
		widgets = {
			'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter phone number'}),
			'image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
		}
	
	def __init__(self, *args, **kwargs):
		user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)
		if user:
			self.fields['first_name'].initial = user.first_name
			self.fields['last_name'].initial = user.last_name
			self.fields['email'].initial = user.email


@login_required
def profile_view(request):
	profile, created = Profile.objects.get_or_create(user=request.user)
	
	if request.method == 'POST':
		form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
		if form.is_valid():
			# Update user fields
			request.user.first_name = form.cleaned_data.get('first_name', '')
			request.user.last_name = form.cleaned_data.get('last_name', '')
			request.user.email = form.cleaned_data.get('email', '')
			request.user.save()
			
			# Save profile
			form.save()
			messages.success(request, 'Profile updated successfully!')
			return redirect('accounts:profile')
	else:
		form = ProfileForm(instance=profile, user=request.user)
	
	return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def profile_update(request):
	"""AJAX profile update view"""
	if request.method != 'POST':
		return JsonResponse({'success': False, 'message': 'Only POST requests allowed'}, status=405)
	
	try:
		profile, created = Profile.objects.get_or_create(user=request.user)
		updated_fields = []
		has_changes = False
		
		# Debug: Log what we received
		print(f"POST data: {list(request.POST.keys())}")
		print(f"FILES data: {list(request.FILES.keys())}")
		
		# Update user fields - only update if value is provided AND different from current
		if 'first_name' in request.POST:
			new_first_name = request.POST.get('first_name', '')
			if new_first_name != request.user.first_name:
				request.user.first_name = new_first_name
				updated_fields.append('first_name')
				has_changes = True
		
		if 'last_name' in request.POST:
			new_last_name = request.POST.get('last_name', '')
			if new_last_name != request.user.last_name:
				request.user.last_name = new_last_name
				updated_fields.append('last_name')
				has_changes = True
		
		if 'email' in request.POST:
			new_email = request.POST.get('email', '')
			if new_email != request.user.email:
				# Check if email is taken by another user
				from django.contrib.auth.models import User
				if new_email and User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
					return JsonResponse({'success': False, 'message': 'Email is already taken by another user'})
				request.user.email = new_email
				updated_fields.append('email')
				has_changes = True
		
		if 'phone' in request.POST:
			new_phone = request.POST.get('phone', '')
			if new_phone != profile.phone:
				profile.phone = new_phone
				updated_fields.append('phone')
				has_changes = True
		
		# Handle password change
		if 'password' in request.POST:
			password = request.POST.get('password', '').strip()
			if password:  # Only update if password is provided and not empty
				if len(password) >= 8:
					request.user.set_password(password)
					updated_fields.append('password')
					has_changes = True
				else:
					return JsonResponse({'success': False, 'message': 'Password must be at least 8 characters long'})
		
		# Handle profile picture upload
		if 'photo' in request.FILES:
			photo = request.FILES['photo']
			print(f"Photo received: {photo.name}, Size: {photo.size}, Type: {photo.content_type}")
			# Validate file size (max 5MB)
			if photo.size > 5 * 1024 * 1024:
				return JsonResponse({'success': False, 'message': 'Profile picture size must be less than 5MB'})
			
			# Validate file type
			allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
			if photo.content_type not in allowed_types:
				return JsonResponse({'success': False, 'message': 'Please upload a valid image file (JPEG, PNG, GIF, WebP)'})
			
			# Delete old profile picture if exists
			if profile.image:
				import os
				try:
					if os.path.isfile(profile.image.path):
						os.remove(profile.image.path)
						print("Old profile picture deleted")
				except Exception as e:
					print(f"Error deleting old profile picture: {e}")
			
			# Update profile image
			profile.image = photo
			updated_fields.append('photo')
			has_changes = True
			print("Photo added to profile, has_changes set to True")
		
		# Only save if there were actual changes
		if has_changes:
			print(f"Saving changes. Updated fields: {updated_fields}")
			request.user.save()
			profile.save()
			print(f"Profile saved. Image path: {profile.image.path if profile.image else 'None'}")
		else:
			print("No changes detected, skipping save")
		
		return JsonResponse({
			'success': True, 
			'message': f'Profile updated successfully! Updated: {", ".join(updated_fields) if updated_fields else "no changes"}',
			'profile_photo_url': profile.image.url if profile.image else None
		})
		
	except Exception as e:
		import traceback
		print(f"Profile update error: {str(e)}")
		print(traceback.format_exc())
		return JsonResponse({
			'success': False, 
			'message': f'Error updating profile: {str(e)}'
		})


@login_required
def settings_view(request):
	"""Settings view - placeholder for user settings"""
	profile, created = Profile.objects.get_or_create(user=request.user)
	
	# For now, redirect to profile since we don't have a dedicated settings page
	messages.info(request, 'Settings page coming soon. For now, you can update your profile.')
	return redirect('accounts:profile')


# Role Management Views
@login_required
@user_passes_test(is_admin)
def role_list(request):
	from .models import CustomRole, NavigationItem
	from django.contrib.auth.models import Permission, User
	from django.core.paginator import Paginator
	
	# Get search query
	search_query = request.GET.get('search', '').strip()
	
	# Start with all custom roles
	custom_roles = CustomRole.objects.all()
	
	# Apply search filter to custom roles
	if search_query:
		custom_roles = custom_roles.filter(
			Q(name__icontains=search_query) |
			Q(description__icontains=search_query)
		)
	
	# Create system roles list (Admin and Staff)
	system_roles = []
	
	# Admin role (is_superuser)
	admin_count = User.objects.filter(is_superuser=True).count()
	system_roles.append({
		'id': 'system_admin',
		'name': 'Admin',
		'description': 'Full system administrator with all permissions (Django superuser)',
		'is_system': True,
		'permissions_count': Permission.objects.count(),  # Admins have all permissions
		'users_count': admin_count,
		'created_at': None,  # System role, no creation date
	})
	
	# Staff role (is_staff but not is_superuser)
	staff_count = User.objects.filter(is_staff=True, is_superuser=False).count()
	system_roles.append({
		'id': 'system_staff',
		'name': 'Staff',
		'description': 'Staff member with access to admin interface (Django staff flag)',
		'is_system': True,
		'permissions_count': 0,  # Staff permissions vary
		'users_count': staff_count,
		'created_at': None,  # System role, no creation date
	})
	
	# Filter system roles by search if needed
	if search_query:
		system_roles = [r for r in system_roles if search_query.lower() in r['name'].lower() or search_query.lower() in r['description'].lower()]
	
	# Combine system roles and custom roles
	# Convert custom roles to dict format for consistency
	all_roles_list = []
	
	# Add system roles first
	for sys_role in system_roles:
		all_roles_list.append(sys_role)
	
	# Add custom roles
	for role in custom_roles:
		all_roles_list.append({
			'id': role.id,
			'name': role.name,
			'description': role.description or 'No description provided',
			'is_system': False,
			'permissions_count': role.permissions.count(),
			'users_count': role.userrole_set.count(),
			'created_at': role.created_at,
			'role_obj': role,  # Keep reference to actual object for actions
		})
	
	# Sort by name
	all_roles_list.sort(key=lambda x: x['name'])
	
	# Pagination
	page_size = request.GET.get('page_size', '5')
	try:
		page_size = int(page_size)
		if page_size not in [5, 10, 25, 50, 100]:
			page_size = 5
	except (ValueError, TypeError):
		page_size = 5
	
	paginator = Paginator(all_roles_list, page_size)
	page_number = request.GET.get('page', 1)
	
	try:
		page_obj = paginator.get_page(page_number)
	except:
		page_obj = paginator.get_page(1)
	
	navigation_items = NavigationItem.objects.filter(is_active=True).order_by('order', 'name')
	permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
	profile, created = Profile.objects.get_or_create(user=request.user)
	
	# Get statistics (include system roles)
	total_permissions = Permission.objects.count()
	total_roles_count = len(all_roles_list)
	
	return render(request, 'accounts/role_list.html', {
		'roles': page_obj,
		'page_obj': page_obj,
		'paginator': paginator,
		'navigation_items': navigation_items,
		'permissions': permissions,
		'total_permissions': total_permissions,
		'total_roles_count': total_roles_count,
		'profile': profile,
		'current_page_size': page_size,
		'search_query': search_query,
	})


@login_required  
@user_passes_test(is_admin)
@login_required
@user_passes_test(is_admin)
def create_role(request):
	from .models import CustomRole, NavigationItem, RoleNavigationPermission
	if request.method == 'POST':
		name = request.POST.get('name')
		description = request.POST.get('description', '')
		permissions = request.POST.getlist('permissions')
		navigation_permissions = request.POST.getlist('navigation_permissions')
		
		if name:
			role = CustomRole.objects.create(name=name, description=description)
			
			# If this is an Admin role, assign all permissions automatically
			if name.lower() in ['admin', 'administrator', 'system administrator']:
				from django.contrib.auth.models import Permission
				all_permissions = Permission.objects.all()
				role.permissions.set(all_permissions)
				
				# Also assign all navigation permissions
				all_navigation_items = NavigationItem.objects.filter(is_active=True)
				for nav_item in all_navigation_items:
					RoleNavigationPermission.objects.get_or_create(
						role=role,
						navigation_item=nav_item,
						defaults={'can_access': True}
					)
				
				messages.success(request, f'Admin role "{name}" created with ALL permissions automatically!')
			else:
				# For non-admin roles, use the selected permissions
				if permissions:
					role.permissions.set(permissions)
				
				# Handle navigation permissions
				for nav_item_id in navigation_permissions:
					try:
						nav_item = NavigationItem.objects.get(id=nav_item_id)
						RoleNavigationPermission.objects.create(
							role=role,
							navigation_item=nav_item,
							can_access=True
						)
					except NavigationItem.DoesNotExist:
						continue
				
				messages.success(request, f'Role "{name}" created successfully!')
			
			return redirect('accounts:role_list')
		else:
			messages.error(request, 'Role name is required.')
	
	from django.contrib.auth.models import Permission
	permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
	navigation_items = NavigationItem.objects.filter(is_active=True).order_by('order', 'name')
	profile, created = Profile.objects.get_or_create(user=request.user)
	return render(request, 'accounts/create_role.html', {
		'permissions': permissions,
		'navigation_items': navigation_items,
		'profile': profile
	})


@login_required
@user_passes_test(is_admin) 
def edit_role(request, role_id):
	from .models import CustomRole
	role = get_object_or_404(CustomRole, pk=role_id)
	
	if request.method == 'POST':
		name = request.POST.get('name')
		description = request.POST.get('description', '')
		permissions = request.POST.getlist('permissions')
		
		if name:
			role.name = name
			role.description = description
			role.save()
			role.permissions.set(permissions)
			messages.success(request, f'Role "{name}" updated successfully!')
			return redirect('accounts:role_list')
		else:
			messages.error(request, 'Role name is required.')
	
	from django.contrib.auth.models import Permission
	permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
	profile, created = Profile.objects.get_or_create(user=request.user)
	return render(request, 'accounts/edit_role.html', {
		'role': role, 
		'permissions': permissions,
		'profile': profile
	})


@login_required
@user_passes_test(is_admin)
def delete_role(request, role_id):
	from .models import CustomRole
	role = get_object_or_404(CustomRole, pk=role_id)
	
	if request.method == 'POST':
		role_name = role.name
		role.delete()
		messages.success(request, f'Role "{role_name}" deleted successfully!')
	
	return redirect('accounts:role_list')


@login_required
@user_passes_test(is_admin)
def manage_permissions(request):
	from django.contrib.auth.models import Permission
	permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
	profile, created = Profile.objects.get_or_create(user=request.user)
	return render(request, 'accounts/manage_permissions.html', {
		'permissions': permissions,
		'profile': profile
	})


@login_required
@require_role('Admin')
def assign_user_role(request, user_id):
	"""View for assigning a single role to a user"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	if request.method == 'POST':
		role_id = request.POST.get('role_id')
		
		if role_id:
			try:
				role = CustomRole.objects.get(pk=role_id)
				user_role, created = UserRole.objects.get_or_create(
					user=user_obj,
					role=role,
					defaults={'assigned_by': request.user}
				)
				
				if created:
					messages.success(request, f'Role "{role.name}" assigned to {user_obj.username}')
					
					# Also add to Django group for backward compatibility
					group, _ = Group.objects.get_or_create(name=role.name)
					user_obj.groups.add(group)
				else:
					messages.info(request, f'{user_obj.username} already has the "{role.name}" role')
				
			except CustomRole.DoesNotExist:
				messages.error(request, 'Invalid role selected')
	
	return redirect('accounts:edit_user_roles', user_id=user_id)


@login_required  
@require_role('Admin')
def remove_user_role(request, user_id, role_id):
	"""View for removing a role from a user"""
	user_obj = get_object_or_404(User, pk=user_id)
	role = get_object_or_404(CustomRole, pk=role_id)
	
	if request.method == 'POST':
		try:
			user_role = UserRole.objects.get(user=user_obj, role=role)
			user_role.delete()
			
			# Also remove from Django group
			try:
				group = Group.objects.get(name=role.name)
				user_obj.groups.remove(group)
			except Group.DoesNotExist:
				pass
			
			messages.success(request, f'Role "{role.name}" removed from {user_obj.username}')
		except UserRole.DoesNotExist:
			messages.warning(request, f'{user_obj.username} does not have the "{role.name}" role')
	
	return redirect('accounts:edit_user_roles', user_id=user_id)


@login_required
@user_passes_test(is_admin)
def get_permissions(request):
	"""AJAX view to get all permissions for modal"""
	from django.http import JsonResponse
	from django.contrib.auth.models import Permission
	
	permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
	permissions_data = []
	
	for perm in permissions:
		permissions_data.append({
			'id': perm.id,
			'codename': perm.codename.replace('_', ' ').title(),
			'app_label': perm.content_type.app_label.title()
		})
	
	return JsonResponse({
		'success': True,
		'permissions': permissions_data
	})


@login_required
@user_passes_test(is_admin)
def get_navigation_items(request):
	"""AJAX view to get all navigation items for role creation modal"""
	from django.http import JsonResponse
	from .models import NavigationItem
	import logging
	
	logger = logging.getLogger(__name__)
	logger.info(f"get_navigation_items called by user: {request.user}")
	
	try:
		navigation_items = NavigationItem.objects.filter(is_active=True).order_by('order', 'name')
		navigation_data = []
		
		logger.info(f"Found {navigation_items.count()} navigation items")
		
		for nav_item in navigation_items:
			navigation_data.append({
				'id': nav_item.id,
				'display_name': nav_item.display_name,
				'url_name': nav_item.url_name or '',
				'parent': {
					'id': nav_item.parent.id,
					'display_name': nav_item.parent.display_name
				} if nav_item.parent else None
			})
		
		return JsonResponse({
			'success': True,
			'navigation_items': navigation_data,
			'count': len(navigation_data)
		})
	
	except Exception as e:
		import traceback
		logger.error(f"Error in get_navigation_items: {str(e)}")
		logger.error(traceback.format_exc())
		return JsonResponse({
			'success': False,
			'message': f'Error loading navigation items: {str(e)}',
			'traceback': traceback.format_exc()
		})


@login_required
@user_passes_test(is_admin)
def get_navigation_items(request):
	"""AJAX view to get all navigation items for modal"""
	from django.http import JsonResponse
	from .models import NavigationItem
	
	navigation_items = NavigationItem.objects.all().order_by('order', 'display_name')
	navigation_data = []
	
	for nav_item in navigation_items:
		navigation_data.append({
			'id': nav_item.id,
			'display_name': nav_item.display_name,
			'url_name': nav_item.url_name,
			'parent': {
				'id': nav_item.parent.id,
				'display_name': nav_item.parent.display_name
			} if nav_item.parent else None
		})
	
	return JsonResponse({
		'success': True,
		'navigation_items': navigation_data
	})


@login_required
@user_passes_test(is_admin)
def create_role_ajax(request):
	"""AJAX view to create a role"""
	from django.http import JsonResponse
	from .models import CustomRole
	
	if request.method == 'POST':
		name = request.POST.get('name')
		description = request.POST.get('description', '')
		permissions = request.POST.getlist('permissions')
		navigation_permissions = request.POST.getlist('navigation_permissions')
		
		if not name:
			return JsonResponse({
				'success': False,
				'message': 'Role name is required.'
			})
		
		# Check if role already exists
		if CustomRole.objects.filter(name=name).exists():
			return JsonResponse({
				'success': False,
				'message': f'Role "{name}" already exists.'
			})
		
		try:
			from .models import RoleNavigationPermission, NavigationItem
			
			role = CustomRole.objects.create(name=name, description=description)
			
			# If this is an Admin role, assign all permissions automatically
			if name.lower() in ['admin', 'administrator', 'system administrator']:
				from django.contrib.auth.models import Permission
				all_permissions = Permission.objects.all()
				role.permissions.set(all_permissions)
				
				# Also assign all navigation permissions
				all_navigation_items = NavigationItem.objects.filter(is_active=True)
				for nav_item in all_navigation_items:
					RoleNavigationPermission.objects.get_or_create(
						role=role,
						navigation_item=nav_item,
						defaults={'can_access': True}
					)
				
				return JsonResponse({
					'success': True,
					'message': f'Admin role "{name}" created with ALL permissions automatically!'
				})
			else:
				# For non-admin roles, use the selected permissions
				if permissions:
					role.permissions.set(permissions)
				
				# Handle navigation permissions
				if navigation_permissions:
					for nav_id in navigation_permissions:
						try:
							nav_item = NavigationItem.objects.get(id=nav_id)
							RoleNavigationPermission.objects.create(role=role, navigation_item=nav_item)
						except NavigationItem.DoesNotExist:
							continue
				
				return JsonResponse({
					'success': True,
					'message': f'Role "{name}" created successfully with navigation permissions!'
				})
		except Exception as e:
			return JsonResponse({
				'success': False,
				'message': f'Error creating role: {str(e)}'
			})
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method.'
	})


@login_required
@user_passes_test(is_admin)
def get_roles_for_user_creation(request):
	"""AJAX view to get available roles for user creation"""
	from django.http import JsonResponse
	from .models import CustomRole
	
	# Get all available roles except Admin (only superusers can assign Admin)
	if request.user.is_superuser:
		roles = CustomRole.objects.all()
	else:
		roles = CustomRole.objects.exclude(name='Admin')
	
	roles_data = []
	for role in roles:
		roles_data.append({
			'id': role.id,
			'name': role.name,
			'description': role.description or ''
		})
	
	return JsonResponse({
		'success': True,
		'roles': roles_data
	})


@login_required
@user_passes_test(is_admin)
def get_role_navigation(request, role_id):
	"""AJAX view to get navigation permissions for a specific role"""
	from django.http import JsonResponse
	from .models import NavigationItem, CustomRole, RoleNavigationPermission
	
	try:
		role = get_object_or_404(CustomRole, id=role_id)
		
		# Get all navigation items
		navigation_items = NavigationItem.objects.all().order_by('order', 'display_name')
		
		# Get current permissions for this role
		current_permissions = RoleNavigationPermission.objects.filter(role=role).values_list('navigation_item_id', flat=True)
		
		navigation_data = []
		for nav_item in navigation_items:
			navigation_data.append({
				'id': nav_item.id,
				'display_name': nav_item.display_name,
				'url_name': nav_item.url_name,
				'parent': {
					'id': nav_item.parent.id,
					'display_name': nav_item.parent.display_name
				} if nav_item.parent else None
			})
		
		return JsonResponse({
			'success': True,
			'navigation_items': navigation_data,
			'current_permissions': list(current_permissions)
		})
	except Exception as e:
		return JsonResponse({
			'success': False,
			'message': f'Error loading role navigation: {str(e)}'
		})


@login_required
@user_passes_test(is_admin)
def edit_role_navigation(request):
	"""AJAX view to edit navigation permissions for a role"""
	from django.http import JsonResponse
	from .models import NavigationItem, CustomRole, RoleNavigationPermission
	
	if request.method == 'POST':
		try:
			role_id = request.POST.get('role_id')
			navigation_permissions = request.POST.getlist('navigation_permissions')
			
			if not role_id:
				return JsonResponse({
					'success': False,
					'message': 'Role ID is required.'
				})
			
			role = get_object_or_404(CustomRole, id=role_id)
			
			# Remove existing navigation permissions for this role
			RoleNavigationPermission.objects.filter(role=role).delete()
			
			# Add new navigation permissions
			if navigation_permissions:
				for nav_id in navigation_permissions:
					try:
						nav_item = NavigationItem.objects.get(id=nav_id)
						RoleNavigationPermission.objects.create(role=role, navigation_item=nav_item)
					except NavigationItem.DoesNotExist:
						continue
			
			return JsonResponse({
				'success': True,
				'message': f'Navigation permissions updated successfully for role "{role.name}"!'
			})
		except Exception as e:
			return JsonResponse({
				'success': False,
				'message': f'Error updating navigation permissions: {str(e)}'
			})
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method.'
	})


@login_required
@user_passes_test(is_admin)
def create_user_ajax(request):
	"""AJAX view to create a user - Managers cannot use this"""
	from django.http import JsonResponse
	from .models import CustomRole, UserRole, Profile
	from django.core.validators import validate_email
	from django.core.exceptions import ValidationError
	
	# Managers cannot create users via AJAX - only via mobile API
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		return JsonResponse({
			'success': False,
			'message': 'Managers can only create Property Owner accounts via the mobile API (/api/v1/admin/register-owner/).'
		}, status=403)
	
	if request.method == 'POST':
		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip().lower()
		first_name = request.POST.get('first_name', '').strip()
		last_name = request.POST.get('last_name', '').strip()
		password = request.POST.get('password', '')
		confirm_password = request.POST.get('confirm_password', '')
		is_active = request.POST.get('is_active') == 'on'
		is_staff = request.POST.get('is_staff') == 'on'
		selected_roles = request.POST.getlist('roles')
		
		# Validation
		errors = []
		
		# Required fields
		if not username:
			errors.append('Username is required.')
		elif len(username) < 3:
			errors.append('Username must be at least 3 characters long.')
		elif len(username) > 150:
			errors.append('Username must be less than 150 characters.')
		elif not username.replace('_', '').replace('.', '').isalnum():
			errors.append('Username can only contain letters, numbers, underscores, and periods.')
		
		if not email:
			errors.append('Email is required.')
		else:
			try:
				validate_email(email)
			except ValidationError:
				errors.append('Please enter a valid email address.')
		
		if not password:
			errors.append('Password is required.')
		elif len(password) < 8:
			errors.append('Password must be at least 8 characters long.')
		elif password != confirm_password:
			errors.append('Passwords do not match.')
		else:
			# Password strength validation
			has_upper = any(c.isupper() for c in password)
			has_lower = any(c.islower() for c in password)
			has_digit = any(c.isdigit() for c in password)
			
			if not (has_upper and has_lower and has_digit):
				errors.append('Password must contain at least one uppercase letter, one lowercase letter, and one number.')
		
		# Check for existing username
		if username and User.objects.filter(username=username).exists():
			errors.append('Username already exists.')
		
		# Check for existing email
		if email and User.objects.filter(email__iexact=email).exists():
			errors.append('Email already exists.')
		
		# Validate role IDs
		if selected_roles:
			valid_role_ids = set(CustomRole.objects.values_list('id', flat=True))
			selected_role_ids = [int(rid) for rid in selected_roles if rid.isdigit()]
			invalid_roles = [rid for rid in selected_role_ids if rid not in valid_role_ids]
			if invalid_roles:
				errors.append(f'Invalid role IDs selected: {invalid_roles}')
		
		if errors:
			return JsonResponse({
				'success': False,
				'message': ' '.join(errors)
			})
		
		try:
			with transaction.atomic():
				# Create user
				user = User.objects.create_user(
					username=username,
					email=email,
					password=password,
					first_name=first_name,
					last_name=last_name,
					is_active=is_active,
					is_staff=is_staff
				)
				
				# Create profile
				Profile.objects.create(user=user)
				
				# Assign roles
				for role_id in selected_roles:
					try:
						role = CustomRole.objects.get(id=role_id)
						UserRole.objects.create(
							user=user,
							role=role,
							assigned_by=request.user
						)
					except CustomRole.DoesNotExist:
						continue
				
				return JsonResponse({
					'success': True,
					'message': f'User "{username}" created successfully!'
				})
		
		except Exception as e:
			return JsonResponse({
				'success': False,
				'message': f'Error creating user: {str(e)}'
			})
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method.'
	})


@login_required
@user_passes_test(is_admin)
def get_user_roles(request, user_id):
	"""AJAX view to get available roles and the roles currently assigned to a specific user"""
	from django.http import JsonResponse
	from .models import CustomRole, UserRole
	user_obj = get_object_or_404(User, pk=user_id)

	# Get all available roles except Admin (only superusers can assign Admin)
	if request.user.is_superuser:
		roles = CustomRole.objects.all()
	else:
		roles = CustomRole.objects.exclude(name='Admin')

	roles_data = []
	for role in roles:
		roles_data.append({
			'id': role.id,
			'name': role.name,
			'description': role.description or ''
		})

	# Get currently assigned role ids for the target user
	assigned = UserRole.objects.filter(user=user_obj).values_list('role__id', flat=True)
	assigned_list = list(assigned)

	return JsonResponse({
		'success': True,
		'available_roles': roles_data,
		'user_roles': assigned_list
	})


@login_required
@user_passes_test(is_admin)
def update_user_roles_ajax(request, user_id):
	"""AJAX view to update roles for a specific user"""
	from django.http import JsonResponse
	from .models import CustomRole, UserRole

	if request.method != 'POST':
		return JsonResponse({'success': False, 'message': 'Invalid request method.'})

	# Check if user is Manager - Managers cannot assign/update roles
	is_manager_user = is_manager(request.user)
	
	if is_manager_user and not (request.user.is_superuser or request.user.is_staff):
		return JsonResponse({
			'success': False, 
			'message': 'Managers cannot assign or update user roles'
		}, status=403)

	user_obj = get_object_or_404(User, pk=user_id)

	# Get role IDs from POST data
	selected_role_ids = request.POST.getlist('roles')
	
	# Convert to integers and filter out empty strings/None
	selected_role_ids = [int(rid) for rid in selected_role_ids if rid and str(rid).strip()]
	
	# Log for debugging
	import logging
	logger = logging.getLogger(__name__)
	logger.info(f"Updating roles for user {user_obj.id}: {selected_role_ids}")

	try:
		# Clear existing role assignments
		UserRole.objects.filter(user=user_obj).delete()

		# Add new role assignments
		if selected_role_ids:
			selected_roles = CustomRole.objects.filter(pk__in=selected_role_ids)
			for role in selected_roles:
				UserRole.objects.get_or_create(
					user=user_obj, 
					role=role,
					defaults={'assigned_by': request.user}
				)

		# Also sync with Django groups for backward compatibility
		if selected_role_ids:
			role_names = [role.name for role in selected_roles]
			group_names = []
			for name in role_names:
				group_names.append(name)
				if name == 'Manager':
					group_names.append('Property manager')

			# Clear and add groups
			user_obj.groups.clear()
			for name in group_names:
				group, _ = Group.objects.get_or_create(name=name)
				user_obj.groups.add(group)
		else:
			# If no roles selected, clear all groups
			user_obj.groups.clear()

		return JsonResponse({'success': True, 'message': 'Roles updated successfully.'})
	except Exception as e:
		return JsonResponse({'success': False, 'message': f'Error updating roles: {str(e)}'})


## Firebase connectivity test view removed (unused)


## Firebase tenant listing view removed (unused)


## Firebase disable tenant view removed (unused)


## Firebase delete tenant view removed (unused)


# =============================================================================
# HOUSES/PROPERTIES MANAGEMENT VIEWS
# =============================================================================

@login_required
def houses_list(request):
    """View for listing houses/properties"""
    from properties.models import Property
    from properties.forms import PropertySearchForm
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    properties = Property.objects.select_related(
        'property_type', 'region', 'owner'
    ).prefetch_related('images', 'amenities')
    
    # Sorting functionality
    sort_by = request.GET.get('sort', '-created_at')
    allowed_sorts = [
        '-created_at', 'created_at',  # Newest/Oldest
        'rent_amount', '-rent_amount',  # Price: Low to High / High to Low
        'title', '-title',  # Title A-Z / Z-A
        'bedrooms', '-bedrooms',  # Bedrooms ascending/descending
        'size_sqft', '-size_sqft',  # Size ascending/descending
    ]
    
    if sort_by in allowed_sorts:
        properties = properties.order_by(sort_by)
    else:
        properties = properties.order_by('-created_at')
    
    # Search functionality
    search_form = PropertySearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        if search_query:
            properties = properties.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        
        property_type = search_form.cleaned_data.get('property_type')
        if property_type:
            properties = properties.filter(property_type=property_type)
        
        region = search_form.cleaned_data.get('region')
        if region:
            properties = properties.filter(region=region)
        
        # District filter
        district = search_form.cleaned_data.get('district')
        if district:
            properties = properties.filter(district=district)
        
        min_bedrooms = search_form.cleaned_data.get('min_bedrooms')
        if min_bedrooms:
            properties = properties.filter(bedrooms__gte=min_bedrooms)
        
        max_bedrooms = search_form.cleaned_data.get('max_bedrooms')
        if max_bedrooms:
            properties = properties.filter(bedrooms__lte=max_bedrooms)
        
        min_rent = search_form.cleaned_data.get('min_rent')
        if min_rent:
            properties = properties.filter(rent_amount__gte=min_rent)
        
        max_rent = search_form.cleaned_data.get('max_rent')
        if max_rent:
            properties = properties.filter(rent_amount__lte=max_rent)
        
        is_furnished = search_form.cleaned_data.get('is_furnished')
        if is_furnished:
            properties = properties.filter(is_furnished=True)
        
        pets_allowed = search_form.cleaned_data.get('pets_allowed')
        if pets_allowed:
            properties = properties.filter(pets_allowed=True)
        
        amenities = search_form.cleaned_data.get('amenities')
        if amenities:
            properties = properties.filter(amenities__in=amenities).distinct()
    
    # Count total properties before pagination
    total_properties_count = properties.count()
    
    # Pagination - support more items per page options
    per_page = request.GET.get('per_page', '12')
    try:
        per_page = int(per_page)
        if per_page not in [12, 24, 48, 96]:
            per_page = 12
    except (ValueError, TypeError):
        per_page = 12
    
    paginator = Paginator(properties, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Create pagination range for template
    page_range = []
    current_page = page_obj.number
    total_pages = paginator.num_pages
    
    # Always show first page
    if total_pages > 1:
        page_range.append(1)
    
    # Add pages around current page
    start_range = max(2, current_page - 2)
    end_range = min(total_pages, current_page + 2)
    
    # Add ellipsis if needed
    if start_range > 2:
        page_range.append('...')
    
    # Add middle range
    for i in range(start_range, end_range + 1):
        if i not in page_range and i != 1 and i != total_pages:
            page_range.append(i)
    
    # Add ellipsis if needed
    if end_range < total_pages - 1:
        page_range.append('...')
    
    # Always show last page
    if total_pages > 1 and total_pages not in page_range:
        page_range.append(total_pages)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_properties': total_properties_count,
        'page_range': page_range,
        'per_page': per_page,
        'per_page_options': [12, 24, 48, 96],
        'current_sort': sort_by,
    }
    
    return render(request, 'accounts/houses/houses_list.html', context)


@login_required
def house_detail(request, pk):
    """View for displaying house/property details"""
    from properties.models import Property, PropertyView, PropertyFavorite
    
    property_obj = get_object_or_404(
        Property.objects.select_related('property_type', 'region', 'owner')
        .prefetch_related('images', 'amenities'),
        pk=pk
    )
    
    # Track property view
    PropertyView.objects.get_or_create(
        property=property_obj,
        user=request.user,
        defaults={
            'ip_address': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
    )
    
    # Check if property is favorited by current user
    is_favorited = PropertyFavorite.objects.filter(
        user=request.user,
        property=property_obj
    ).exists()
    
    # Get related properties (same region or property type)
    related_properties = Property.objects.filter(
        Q(region=property_obj.region) | Q(property_type=property_obj.property_type)
    ).exclude(pk=property_obj.pk).select_related(
        'property_type', 'region'
    ).prefetch_related('images')[:6]
    
    context = {
        'property': property_obj,
        'is_favorited': is_favorited,
        'related_properties': related_properties,
    }
    
    return render(request, 'accounts/houses/house_detail.html', context)


@login_required
def house_create(request):
    """View for creating a new house/property"""
    from properties.forms import PropertyForm, PropertyImageFormSet
    from properties.models import PropertyImage
    
    if request.method == 'POST':
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        form = PropertyForm(request.POST, request.FILES, owner=request.user)
        image_formset = PropertyImageFormSet(request.POST, request.FILES) if not is_ajax else None
        
        if form.is_valid() and (image_formset is None or image_formset.is_valid()):
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            form.save_m2m()  # Save many-to-many relationships (amenities)
            
            # Handle multiple images for AJAX request
            if is_ajax and request.FILES.getlist('images'):
                images = request.FILES.getlist('images')
                for index, image_file in enumerate(images):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image_file,
                        is_primary=(index == 0),  # First image is primary
                        order=index
                    )
            elif image_formset:
                # Save images from formset (non-AJAX)
                image_formset.instance = property_obj
                image_formset.save()
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'House created successfully!',
                    'property_id': property_obj.pk
                })
            else:
                messages.success(request, 'House created successfully!')
                return redirect('accounts:house_detail', pk=property_obj.pk)
        else:
            if is_ajax:
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                return JsonResponse({
                    'success': False,
                    'message': 'Please correct the errors below.',
                    'errors': errors
                }, status=400)
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm(owner=request.user)
        image_formset = PropertyImageFormSet()
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'title': 'Add New House',
    }
    
    return render(request, 'accounts/houses/house_form.html', context)


@login_required
def house_edit(request, pk):
    """View for editing an existing house/property"""
    from properties.models import Property
    from properties.forms import PropertyForm, PropertyImageFormSet
    
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property_obj, owner=request.user)
        image_formset = PropertyImageFormSet(
            request.POST, 
            request.FILES, 
            instance=property_obj
        )
        
        if form.is_valid() and image_formset.is_valid():
            form.save()
            image_formset.save()
            
            messages.success(request, 'House updated successfully!')
            return redirect('accounts:house_detail', pk=property_obj.pk)
    else:
        form = PropertyForm(instance=property_obj, owner=request.user)
        image_formset = PropertyImageFormSet(instance=property_obj)
    
    context = {
        'form': form,
        'image_formset': image_formset,
        'property': property_obj,
        'title': 'Edit House',
    }
    
    return render(request, 'accounts/houses/house_form.html', context)


@login_required
def house_delete(request, pk):
    """View for deleting a house/property"""
    from properties.models import Property
    
    # Allow admins to delete any property, others can only delete their own
    if request.user.is_staff or request.user.is_superuser:
        property_obj = get_object_or_404(Property, pk=pk)
    else:
        property_obj = get_object_or_404(Property, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        property_title = property_obj.title
        confirm_title = request.POST.get('confirm_title', '')
        
        # Verify title confirmation for security
        if confirm_title == property_title:
            property_obj.delete()
            messages.success(request, f'House "{property_title}" deleted successfully!')
            
            # Redirect based on user role and context
            redirect_url = request.POST.get('redirect_to', 'accounts:houses_list')
            if redirect_url == 'my_houses':
                return redirect('accounts:my_houses')
            else:
                return redirect('accounts:houses_list')
        else:
            messages.error(request, 'Property title confirmation does not match. Deletion cancelled.')
    
    context = {
        'property': property_obj,
        'is_admin': request.user.is_staff or request.user.is_superuser,
    }
    
    return render(request, 'accounts/houses/house_confirm_delete.html', context)


@login_required
def bulk_delete_houses(request):
    """View for bulk deleting houses (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to perform bulk operations.')
        return redirect('accounts:houses_list')
    
    if request.method == 'POST':
        house_ids = request.POST.getlist('house_ids')
        action = request.POST.get('action')
        
        if action == 'delete' and house_ids:
            from properties.models import Property
            properties = Property.objects.filter(id__in=house_ids)
            count = properties.count()
            
            if count > 0:
                # Get titles for the success message
                titles = list(properties.values_list('title', flat=True))
                properties.delete()
                
                if count == 1:
                    messages.success(request, f'Successfully deleted house: {titles[0]}')
                else:
                    messages.success(request, f'Successfully deleted {count} houses')
            else:
                messages.warning(request, 'No houses were selected for deletion.')
        else:
            messages.error(request, 'Invalid bulk action or no houses selected.')
    
    return redirect('accounts:houses_list')


@login_required
def my_houses(request):
    """View for displaying user's houses/properties"""
    from properties.models import Property
    from django.db.models import Count
    
    properties = Property.objects.filter(owner=request.user).select_related(
        'property_type', 'region'
    ).prefetch_related('images').annotate(
        views_count=Count('views'),
        favorites_count=Count('favorited_by')
    )
    
    # Statistics
    stats = {
        'total': properties.count(),
        'available': properties.filter(status='available').count(),
        'rented': properties.filter(status='rented').count(),
        'under_maintenance': properties.filter(status='under_maintenance').count(),
        'total_views': sum(p.views_count for p in properties),
        'total_favorites': sum(p.favorites_count for p in properties),
    }
    
    context = {
        'properties': properties,
        'stats': stats,
    }
    
    return render(request, 'accounts/houses/my_houses.html', context)


@login_required  
def house_manage_metadata(request):
    """View for managing property types, regions, and amenities"""
    from properties.models import PropertyType, Region, Amenity
    from properties.forms import PropertyTypeForm, RegionForm, AmenityForm
    
    # Handle form submissions
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'property_type':
            form = PropertyTypeForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Property type created successfully!')
                return redirect('accounts:house_manage_metadata')
        
        elif form_type == 'region':
            form = RegionForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Region created successfully!')
                return redirect('accounts:house_manage_metadata')
        
        elif form_type == 'amenity':
            form = AmenityForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Amenity created successfully!')
                return redirect('accounts:house_manage_metadata')
    
    # Get all data
    property_types = PropertyType.objects.all().order_by('name')
    regions = Region.objects.all().order_by('name')
    amenities = Amenity.objects.all().order_by('name')
    
    # Initialize forms
    property_type_form = PropertyTypeForm()
    region_form = RegionForm()
    amenity_form = AmenityForm()
    
    context = {
        'property_types': property_types,
        'regions': regions,
        'amenities': amenities,
        'property_type_form': property_type_form,
        'region_form': region_form,
        'amenity_form': amenity_form,
    }
    
    return render(request, 'accounts/houses/house_manage_metadata.html', context)


@login_required
def delete_property_type(request, pk):
    """Delete a property type"""
    from properties.models import PropertyType
    
    property_type = get_object_or_404(PropertyType, pk=pk)
    
    if request.method == 'POST':
        try:
            name = property_type.name
            # Check if any properties use this type
            if property_type.properties.exists():
                messages.error(request, f'Cannot delete "{name}" - it is being used by {property_type.properties.count()} propert{"y" if property_type.properties.count() == 1 else "ies"}.')
            else:
                property_type.delete()
                messages.success(request, f'Property type "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting property type: {str(e)}')
    
    return redirect('accounts:house_manage_metadata')


@login_required
def delete_region(request, pk):
    """Delete a region"""
    from properties.models import Region
    
    region = get_object_or_404(Region, pk=pk)
    
    if request.method == 'POST':
        try:
            name = region.name
            # Check if any properties use this region
            if region.properties.exists():
                messages.error(request, f'Cannot delete "{name}" - it is being used by {region.properties.count()} propert{"y" if region.properties.count() == 1 else "ies"}.')
            else:
                region.delete()
                messages.success(request, f'Region "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting region: {str(e)}')
    
    return redirect('accounts:house_manage_metadata')


@login_required
def delete_amenity(request, pk):
    """Delete an amenity"""
    from properties.models import Amenity
    
    amenity = get_object_or_404(Amenity, pk=pk)
    
    if request.method == 'POST':
        try:
            name = amenity.name
            # Check if any properties use this amenity
            property_count = amenity.propertyamenity_set.count()
            if property_count > 0:
                messages.error(request, f'Cannot delete "{name}" - it is being used by {property_count} propert{"y" if property_count == 1 else "ies"}.')
            else:
                amenity.delete()
                messages.success(request, f'Amenity "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting amenity: {str(e)}')
    
    return redirect('accounts:house_manage_metadata')


def debug_navigation_items(request):
	"""Debug view to test navigation items without authentication"""
	from django.http import JsonResponse
	from .models import NavigationItem
	
	try:
		# Test the exact same logic as get_navigation_items
		navigation_items = NavigationItem.objects.filter(is_active=True).order_by('order', 'name')
		navigation_data = []
		
		for nav_item in navigation_items:
			navigation_data.append({
				'id': nav_item.id,
				'display_name': nav_item.display_name,
				'url_name': nav_item.url_name or '',
				'parent': {
					'id': nav_item.parent.id,
					'display_name': nav_item.parent.display_name
				} if nav_item.parent else None
			})
		
		return JsonResponse({
			'success': True,
			'navigation_items': navigation_data,
			'count': len(navigation_data),
			'message': 'Debug: Navigation items loaded successfully'
		})
	
	except Exception as e:
		import traceback
		return JsonResponse({
			'success': False,
			'error': str(e),
			'traceback': traceback.format_exc()
		})


@login_required
@user_passes_test(is_admin)
def system_logs(request):
	"""System logs view with filtering and pagination"""
	try:
		# Get filter parameters
		log_level = request.GET.get('level', 'all')
		search_query = request.GET.get('search', '')
		date_from = request.GET.get('date_from', '')
		date_to = request.GET.get('date_to', '')
		page = request.GET.get('page', 1)
		
		# Read log file
		log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'api.log')
		logs = []
		
		if os.path.exists(log_file_path):
			try:
				with open(log_file_path, 'r', encoding='utf-8') as f:
					lines = f.readlines()
				
				# Parse log entries (reverse to show newest first)
				for line in reversed(lines[-5000:]):  # Limit to last 5000 lines for performance
					line = line.strip()
					if not line:
						continue
					
					try:
						# Parse log format: timestamp - level - message
						parts = line.split(' - ', 2)
						if len(parts) >= 3:
							timestamp_str = parts[0]
							level = parts[1]
							message = parts[2]
							
							# Parse timestamp
							try:
								timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
							except:
								try:
									timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
								except:
									timestamp = timezone.now()
							
							# Apply filters
							if log_level != 'all' and level.upper() != log_level.upper():
								continue
							
							if search_query and search_query.lower() not in message.lower():
								continue
							
							# Date filtering
							if date_from:
								try:
									from_date = datetime.strptime(date_from, '%Y-%m-%d')
									if timestamp.date() < from_date.date():
										continue
								except:
									pass
							
							if date_to:
								try:
									to_date = datetime.strptime(date_to, '%Y-%m-%d')
									if timestamp.date() > to_date.date():
										continue
								except:
									pass
							
							logs.append({
								'timestamp': timestamp,
								'level': level,
								'message': message,
								'severity_class': get_log_severity_class(level)
							})
					except Exception as e:
						# Skip malformed log entries
						continue
			except Exception as e:
				messages.error(request, f'Error reading log file: {str(e)}')
		else:
			# Create sample logs if no log file exists
			logs = generate_sample_logs()
		
		# Pagination
		paginator = Paginator(logs, 50)  # 50 logs per page
		page_obj = paginator.get_page(page)
		
		# Log statistics
		total_logs = len(logs)
		error_count = len([log for log in logs if log['level'].upper() == 'ERROR'])
		warning_count = len([log for log in logs if log['level'].upper() == 'WARNING'])
		info_count = len([log for log in logs if log['level'].upper() == 'INFO'])
		
		context = {
			'logs': page_obj,
			'total_logs': total_logs,
			'error_count': error_count,
			'warning_count': warning_count,
			'info_count': info_count,
			'current_level': log_level,
			'search_query': search_query,
			'date_from': date_from,
			'date_to': date_to,
			'log_levels': ['all', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
		}
		
		return render(request, 'accounts/system_logs.html', context)
		
	except Exception as e:
		messages.error(request, f'Error loading system logs: {str(e)}')
		return render(request, 'accounts/system_logs.html', {
			'logs': [],
			'total_logs': 0,
			'error_count': 0,
			'warning_count': 0,
			'info_count': 0,
		})


def get_log_severity_class(level):
	"""Get CSS class for log severity level"""
	level = level.upper()
	if level == 'ERROR':
		return 'danger'
	elif level == 'WARNING':
		return 'warning' 
	elif level == 'INFO':
		return 'info'
	elif level == 'DEBUG':
		return 'secondary'
	else:
		return 'primary'


def generate_sample_logs():
	"""Generate sample logs for demonstration"""
	now = timezone.now()
	sample_logs = []
	
	# Recent activities
	activities = [
		('INFO', 'User admin logged in successfully'),
		('INFO', 'Property "Sunset Apartments" created by user admin'),
		('WARNING', 'Failed login attempt for user: unknown@email.com'),
		('ERROR', 'Database connection timeout in properties module'),
		('INFO', 'User profile updated for user: john.doe'),
		('WARNING', 'High memory usage detected: 85%'),
		('INFO', 'Daily backup completed successfully'),
		('ERROR', 'Payment processing failed for transaction #12345'),
		('INFO', 'System maintenance completed'),
		('WARNING', 'API rate limit exceeded for IP: 192.168.1.100'),
		('INFO', 'New user registration: jane.smith@email.com'),
		('ERROR', '404 Not Found: /api/invalid-endpoint'),
		('INFO', 'Email notification sent to tenant'),
		('WARNING', 'Disk space running low: 90% used'),
		('INFO', 'Property listing updated successfully'),
	]
	
	for i, (level, message) in enumerate(activities):
		timestamp = now - timedelta(hours=i, minutes=i*3)
		sample_logs.append({
			'timestamp': timestamp,
			'level': level,
			'message': message,
			'severity_class': get_log_severity_class(level)
		})
	
	return sample_logs


# ==================== MULTI-TENANCY: Owner Management Views ====================

@login_required
@user_passes_test(is_admin)
def owner_list(request):
	"""
	MULTI-TENANCY: Admin view to list all property owners with their status
	"""
	# Get search and filter parameters
	search_query = request.GET.get('search', '')
	status_filter = request.GET.get('status', '')
	
	# Start with all owners (users with owner role)
	owners = User.objects.filter(profile__role='owner').select_related('profile').prefetch_related('user_roles__role', 'owned_properties')
	
	# Apply search filter
	if search_query:
		owners = owners.filter(
			Q(first_name__icontains=search_query) |
			Q(last_name__icontains=search_query) |
			Q(username__icontains=search_query) |
			Q(email__icontains=search_query)
		)
	
	# Apply status filter
	if status_filter == 'active':
		owners = owners.filter(profile__is_deactivated=False, profile__is_approved=True)
	elif status_filter == 'deactivated':
		owners = owners.filter(profile__is_deactivated=True)
	elif status_filter == 'pending':
		owners = owners.filter(profile__is_approved=False)
	
	# Order by date joined (newest first)
	owners = owners.order_by('-date_joined')
	
	# Pagination
	from django.core.paginator import Paginator
	paginator = Paginator(owners, 10)  # 10 owners per page
	page_obj = paginator.get_page(request.GET.get('page'))
	
	# Get statistics
	total_owners = User.objects.filter(profile__role='owner').count()
	active_owners = User.objects.filter(profile__role='owner', profile__is_deactivated=False, profile__is_approved=True).count()
	deactivated_owners = User.objects.filter(profile__role='owner', profile__is_deactivated=True).count()
	pending_owners = User.objects.filter(profile__role='owner', profile__is_approved=False).count()
	
	# Get property counts for each owner
	owners_data = []
	for owner in page_obj:
		profile = owner.profile
		owners_data.append({
			'user': owner,
			'profile': profile,
			'properties_count': owner.owned_properties.count(),
			'is_deactivated': profile.is_deactivated if profile else False,
			'deactivation_reason': profile.deactivation_reason if profile else None,
		})
	
	return render(request, 'accounts/owner_list.html', {
		'owners_data': owners_data,
		'page_obj': page_obj,
		'total_owners': total_owners,
		'active_owners': active_owners,
		'deactivated_owners': deactivated_owners,
		'pending_owners': pending_owners,
		'search_query': search_query,
		'status_filter': status_filter,
	})


@login_required
@user_passes_test(is_admin)
def register_owner(request):
	"""
	MULTI-TENANCY: Admin view to register/create a new property owner
	"""
	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		password = request.POST.get('password')
		confirm_password = request.POST.get('confirm_password')
		phone = request.POST.get('phone', '')
		
		# Validation
		if not username or not email or not password:
			messages.error(request, 'Username, email, and password are required.')
		elif password != confirm_password:
			messages.error(request, 'Passwords do not match.')
		elif User.objects.filter(username=username).exists():
			messages.error(request, 'Username already exists.')
		elif User.objects.filter(email=email).exists():
			messages.error(request, 'Email already exists.')
		else:
			try:
				with transaction.atomic():
					# Create user
					user = User.objects.create_user(
						username=username,
						email=email,
						password=password,
						first_name=first_name,
						last_name=last_name,
						is_active=True
					)
					
					# Create profile with owner role and auto-approve
					profile = Profile.objects.create(
						user=user,
						role='owner',
						phone=phone,
						is_approved=True,
						approved_by=request.user,
						approved_at=timezone.now(),
						is_deactivated=False  # Ensure they're active
					)
					
					# Ensure they have Property Owner role
					role_name = 'Property Owner'
					try:
						custom_role = CustomRole.objects.get(name=role_name)
					except CustomRole.DoesNotExist:
						custom_role = CustomRole.objects.create(
							name=role_name,
							description='Property owner with system access'
						)
					
					# Assign role
					UserRole.objects.get_or_create(
						user=user,
						role=custom_role,
						defaults={'assigned_by': request.user}
					)
					
					messages.success(request, f'Owner "{username}" has been registered and activated successfully.')
					return redirect('accounts:owner_list')
			except Exception as e:
				messages.error(request, f'Error creating owner: {str(e)}')
	
	return render(request, 'accounts/register_owner.html')


@login_required
@user_passes_test(is_admin)
def activate_owner(request, user_id):
	"""
	MULTI-TENANCY: Admin view to activate a deactivated owner
	"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Verify this is an owner
	try:
		profile = user_obj.profile
		if profile.role != 'owner':
			messages.error(request, 'User is not a property owner.')
			return redirect('accounts:owner_list')
	except Profile.DoesNotExist:
		messages.error(request, 'User profile not found.')
		return redirect('accounts:owner_list')
	
	if request.method == 'POST':
		profile.is_deactivated = False
		profile.deactivation_reason = None
		profile.deactivated_at = None
		profile.deactivated_by = None
		profile.save()
		
		messages.success(request, f'Owner "{user_obj.username}" has been activated successfully.')
		return redirect('accounts:owner_list')
	
	return render(request, 'accounts/activate_owner_confirm.html', {
		'owner': user_obj,
		'profile': profile,
	})


@login_required
@user_passes_test(is_admin)
def deactivate_owner(request, user_id):
	"""
	MULTI-TENANCY: Admin view to deactivate an owner with reason
	"""
	user_obj = get_object_or_404(User, pk=user_id)
	
	# Verify this is an owner
	try:
		profile = user_obj.profile
		if profile.role != 'owner':
			messages.error(request, 'User is not a property owner.')
			return redirect('accounts:owner_list')
	except Profile.DoesNotExist:
		messages.error(request, 'User profile not found.')
		return redirect('accounts:owner_list')
	
	# Prevent deactivation of superusers
	if user_obj.is_superuser:
		messages.error(request, 'You cannot deactivate a superuser.')
		return redirect('accounts:owner_list')
	
	# Prevent users from deactivating themselves
	if user_obj == request.user:
		messages.error(request, 'You cannot deactivate your own account.')
		return redirect('accounts:owner_list')
	
	if request.method == 'POST':
		reason = request.POST.get('reason', '')
		
		if not reason:
			messages.error(request, 'Deactivation reason is required.')
			return render(request, 'accounts/deactivate_owner_confirm.html', {
				'owner': user_obj,
				'profile': profile,
			})
		
		profile.is_deactivated = True
		profile.deactivation_reason = reason
		profile.deactivated_at = timezone.now()
		profile.deactivated_by = request.user
		profile.save()
		
		messages.success(request, f'Owner "{user_obj.username}" has been deactivated. Reason: {reason}')
		return redirect('accounts:owner_list')
	
	return render(request, 'accounts/deactivate_owner_confirm.html', {
		'owner': user_obj,
		'profile': profile,
	})


@csrf_exempt
def forgot_password_request(request):
	"""Handle password reset request from login page"""
	if request.method == 'POST':
		email = request.POST.get('email', '').strip()
		
		if not email:
			return JsonResponse({
				'success': False,
				'message': 'Email is required'
			}, status=400)
		
		try:
			user = User.objects.get(email__iexact=email)
			
			# Create notification for admins
			Notification.objects.create(
				notification_type='password_reset',
				title=f'Password Reset Request from {user.get_full_name() or user.username}',
				message=f'User {user.get_full_name() or user.username} ({user.email}) has requested a password reset. Please reset their password to the default: DefaultPass@12',
				related_user=user,
				metadata={
					'email': user.email,
					'username': user.username,
					'user_id': user.id
				}
			)
			
			return JsonResponse({
				'success': True,
				'message': 'Your password reset request has been sent to the administrator. You will be notified once your password is reset.'
			})
		except User.DoesNotExist:
			# Don't reveal if user exists or not for security
			return JsonResponse({
				'success': True,
				'message': 'If an account exists with this email, a password reset request has been sent to the administrator.'
			})
		except Exception as e:
			logging.error(f"Error creating password reset request: {str(e)}")
			return JsonResponse({
				'success': False,
				'message': 'An error occurred. Please try again later.'
			}, status=500)
	
	return JsonResponse({
		'success': False,
		'message': 'Invalid request method'
	}, status=405)


@login_required
def notifications_list(request):
	"""View for displaying all notifications"""
	if not (request.user.is_superuser or request.user.is_staff):
		messages.error(request, 'You do not have permission to view notifications.')
		return redirect('accounts:dashboard')
	
	# Start with all notifications, ordered by most recent first
	notifications = Notification.objects.all().order_by('-created_at')
	
	# Filter by type if provided
	notification_type = request.GET.get('type', '')
	if notification_type:
		notifications = notifications.filter(notification_type=notification_type)
	
	# Filter by read status
	read_filter = request.GET.get('read', '')
	if read_filter == 'unread':
		notifications = notifications.filter(is_read=False)
	elif read_filter == 'read':
		notifications = notifications.filter(is_read=True)
	# If no filter, show all (both read and unread)
	
	# Pagination
	paginator = Paginator(notifications, 20)
	page = request.GET.get('page', 1)
	notifications_page = paginator.get_page(page)
	
	# Get unread count
	unread_count = Notification.get_unread_count(request.user)
	
	context = {
		'notifications': notifications_page,
		'unread_count': unread_count,
		'notification_types': Notification.NOTIFICATION_TYPES,
		'current_type': notification_type,
		'current_read_filter': read_filter,
	}
	
	return render(request, 'accounts/notifications.html', context)

