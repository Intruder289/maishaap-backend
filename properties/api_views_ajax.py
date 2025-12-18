from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.template.loader import render_to_string
from django.forms import modelform_factory
from properties.models import Property, PropertyType, Region, District, Amenity
from properties.forms import PropertyForm
from django.contrib.auth.models import User
import json

@login_required
@require_http_methods(["GET"])
def property_search_api(request):
    """AJAX API for searching properties"""
    search_query = request.GET.get('search', '')
    type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    
    # MULTI-TENANCY: Start with filtered properties for data isolation
    if request.user.is_authenticated and not (request.user.is_staff or request.user.is_superuser):
        # Property owner: only see own properties
        properties = Property.objects.filter(owner=request.user)
    else:
        # Admin/staff: see all properties
        properties = Property.objects.all()
    
    # Apply search filter
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Apply type filter
    if type_filter:
        properties = properties.filter(property_type__iexact=type_filter)
    
    # Apply status filter
    if status_filter == 'available':
        properties = properties.filter(status='available')
    elif status_filter == 'occupied':
        properties = properties.filter(status='rented')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(properties, per_page)
    page_obj = paginator.get_page(page)
    
    # Render table rows
    html = render_to_string('properties/partials/property_table_rows.html', {
        'properties': page_obj,
        'request': request
    })
    
    return JsonResponse({
        'html': html,
        'total_count': paginator.count,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def property_toggle_status_api(request, property_id):
    """AJAX API for toggling property availability"""
    try:
        property_obj = Property.objects.get(id=property_id)
        current_status = property_obj.status
        requested_status = 'rented' if current_status == 'available' else 'available'

        # Toggle between available and rented based on request
        property_obj.status = requested_status
        property_obj.is_active = (requested_status == 'available')
        property_obj.save()

        # Immediately synchronize status with actual bookings/leases
        property_obj.refresh_status_from_activity()
        property_obj.refresh_from_db()

        status_corrected = property_obj.status != requested_status
        status_message = ''
        if status_corrected and requested_status == 'rented':
            status_message = 'Property reverted to Available because no active bookings or leases were found.'
        
        return JsonResponse({
            'success': True,
            'is_active': property_obj.is_active,
            'status': property_obj.status,
            'status_corrected': status_corrected,
            'message': status_message,
            'new_status': {
                'class': 'bg-success-subtle text-success' if property_obj.is_active else 'bg-danger-subtle text-danger',
                'text': 'Active' if property_obj.is_active else 'Inactive'
            }
        })
    except Property.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Property not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def property_delete_api(request, property_id):
    """AJAX API for deleting properties"""
    try:
        property_obj = Property.objects.get(id=property_id)
        property_obj.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Property deleted successfully'
        })
    except Property.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Property not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def property_create_api(request):
    """AJAX API for creating properties"""
    try:
        # Parse JSON data
        data = json.loads(request.body)
        print(f"Received data: {data}")  # Debug logging
        
        # Create form instance
        form = PropertyForm(data, owner=request.user)
        
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            
            # Handle amenities separately since it's a many-to-many field
            if 'amenities' in data and data['amenities']:
                property_obj.amenities.set(data['amenities'])
            
            print(f"Property created successfully: {property_obj.id}")  # Debug logging
            
            return JsonResponse({
                'success': True,
                'message': 'Property created successfully',
                'property_id': property_obj.id,
                'property_title': property_obj.title,
                'redirect_url': f'/properties/{property_obj.id}/'
            })
        else:
            print(f"Form errors: {form.errors}")  # Debug logging
            return JsonResponse({
                'success': False,
                'message': 'Please correct the errors below',
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")  # Debug logging
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debug logging
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def property_form_data_api(request):
    """AJAX API for getting form data (property types, regions, amenities)"""
    try:
        print("Loading form data...")  # Debug logging
        property_types = list(PropertyType.objects.values('id', 'name'))
        regions = list(Region.objects.values('id', 'name'))
        amenities = list(Amenity.objects.values('id', 'name'))
        
        print(f"Found {len(property_types)} property types, {len(regions)} regions, {len(amenities)} amenities")  # Debug logging
        
        return JsonResponse({
            'success': True,
            'data': {
                'property_types': property_types,
                'regions': regions,
                'amenities': amenities
            }
        })
    except Exception as e:
        print(f"Error loading form data: {e}")  # Debug logging
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["GET"])
def districts_by_region_api(request):
    """AJAX API for getting districts by region"""
    try:
        region_id = request.GET.get('region_id')
        if not region_id:
            return JsonResponse({
                'success': False,
                'message': 'region_id parameter is required'
            }, status=400)
        
        districts = list(District.objects.filter(region_id=region_id).values('id', 'name'))
        
        return JsonResponse({
            'success': True,
            'data': {
                'districts': districts
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# Property Type Management AJAX
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def property_type_update_api(request, property_type_id):
    """AJAX API for updating property types"""
    try:
        property_type = PropertyType.objects.get(id=property_type_id)
        data = json.loads(request.body)
        
        property_type.name = data.get('name', property_type.name)
        property_type.description = data.get('description', property_type.description)
        property_type.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Property type updated successfully',
            'data': {
                'id': property_type.id,
                'name': property_type.name,
                'description': property_type.description
            }
        })
    except PropertyType.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Property type not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def property_type_delete_api(request, property_type_id):
    """AJAX API for deleting property types"""
    try:
        property_type = PropertyType.objects.get(id=property_type_id)
        property_type.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Property type deleted successfully'
        })
    except PropertyType.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Property type not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# Region Management AJAX
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def region_update_api(request, region_id):
    """AJAX API for updating regions"""
    try:
        region = Region.objects.get(id=region_id)
        data = json.loads(request.body)
        
        region.name = data.get('name', region.name)
        region.description = data.get('description', region.description)
        region.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Region updated successfully',
            'data': {
                'id': region.id,
                'name': region.name,
                'description': region.description
            }
        })
    except Region.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Region not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def region_delete_api(request, region_id):
    """AJAX API for deleting regions"""
    try:
        region = Region.objects.get(id=region_id)
        region.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Region deleted successfully'
        })
    except Region.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Region not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# Amenity Management AJAX
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def amenity_update_api(request, amenity_id):
    """AJAX API for updating amenities"""
    try:
        amenity = Amenity.objects.get(id=amenity_id)
        data = json.loads(request.body)
        
        amenity.name = data.get('name', amenity.name)
        amenity.description = data.get('description', amenity.description)
        amenity.icon = data.get('icon', amenity.icon)
        amenity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Amenity updated successfully',
            'data': {
                'id': amenity.id,
                'name': amenity.name,
                'description': amenity.description,
                'icon': amenity.icon
            }
        })
    except Amenity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Amenity not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def amenity_delete_api(request, amenity_id):
    """AJAX API for deleting amenities"""
    try:
        amenity = Amenity.objects.get(id=amenity_id)
        amenity.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Amenity deleted successfully'
        })
    except Amenity.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Amenity not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_property_owners_api(request):
    """AJAX API to get list of property owners for assignment"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied. Only admins can assign property owners.'
        }, status=403)
    
    try:
        from accounts.models import UserRole
        # Get all users with Property Owner role
        owner_role_ids = UserRole.objects.filter(
            role__name__in=['Property Owner', 'Property owner']
        ).values_list('user_id', flat=True)
        
        # Also check profile role for backward compatibility
        profile_owners = User.objects.filter(profile__role='owner').values_list('id', flat=True)
        
        # Combine both
        all_owner_ids = set(list(owner_role_ids) + list(profile_owners))
        
        owners = User.objects.filter(id__in=all_owner_ids).select_related('profile').order_by('first_name', 'last_name', 'username')
        
        owners_list = []
        for owner in owners:
            owners_list.append({
                'id': owner.id,
                'username': owner.username,
                'email': owner.email,
                'full_name': owner.get_full_name() or owner.username,
                'properties_count': owner.owned_properties.count()
            })
        
        return JsonResponse({
            'success': True,
            'owners': owners_list
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching property owners: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def assign_property_owner_api(request, property_id):
    """AJAX API to assign a property owner to a property"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({
            'success': False,
            'message': 'Permission denied. Only admins can assign property owners.'
        }, status=403)
    
    try:
        property_obj = get_object_or_404(Property, pk=property_id)
        
        # Get owner_id from POST data
        data = json.loads(request.body)
        owner_id = data.get('owner_id')
        
        if not owner_id:
            return JsonResponse({
                'success': False,
                'message': 'Owner ID is required'
            }, status=400)
        
        # Get the owner user
        owner = get_object_or_404(User, pk=owner_id)
        
        # Verify owner has Property Owner role
        from accounts.models import UserRole
        is_property_owner = UserRole.objects.filter(
            user=owner,
            role__name__in=['Property Owner', 'Property owner']
        ).exists()
        
        if not is_property_owner and hasattr(owner, 'profile'):
            is_property_owner = owner.profile.role == 'owner'
        
        if not is_property_owner:
            return JsonResponse({
                'success': False,
                'message': 'Selected user is not a property owner'
            }, status=400)
        
        # Assign the property to the owner
        old_owner = property_obj.owner
        property_obj.owner = owner
        property_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Property assigned to {owner.get_full_name() or owner.username} successfully',
            'owner': {
                'id': owner.id,
                'username': owner.username,
                'full_name': owner.get_full_name() or owner.username,
                'email': owner.email
            },
            'old_owner': {
                'id': old_owner.id,
                'username': old_owner.username,
                'full_name': old_owner.get_full_name() or old_owner.username
            } if old_owner else None
        })
    except Property.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Property not found'
        }, status=404)
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Owner not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error assigning property owner: {str(e)}'
        }, status=500)

