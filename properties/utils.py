from django.shortcuts import get_object_or_404
from .models import Property


def get_management_context(request, property_type):
    """
    Utility function to get management context for property-based management modules.
    
    Args:
        request: Django request object
        property_type: Type of property ('hotel', 'lodge', 'venue', 'house')
    
    Returns:
        dict: Context containing selected property, properties list, and mode flags
    """
    session_key = f'selected_{property_type}_property_id'
    selected_property_id = request.session.get(session_key) or request.GET.get('property_id')
    
    # Get properties of the specified type
    properties = Property.objects.filter(property_type__name__iexact=property_type)
    
    # Filter data based on selected property
    if selected_property_id:
        try:
            selected_property = Property.objects.get(id=selected_property_id, property_type__name__iexact=property_type)
            # Store selected property in session
            request.session[session_key] = selected_property_id
            is_single_property_mode = True
        except Property.DoesNotExist:
            selected_property = None
            is_single_property_mode = False
    else:
        selected_property = None
        is_single_property_mode = False
    
    return {
        'properties': properties,
        'selected_property': selected_property,
        'is_single_property_mode': is_single_property_mode,
        'property_type': property_type,
    }


def get_property_filtered_queryset(base_queryset, selected_property, property_type):
    """
    Filter a queryset based on selected property or property type.
    
    Args:
        base_queryset: Base queryset to filter
        selected_property: Selected property object (can be None)
        property_type: Type of property for fallback filtering
    
    Returns:
        QuerySet: Filtered queryset
    """
    if selected_property:
        return base_queryset.filter(property_obj=selected_property)
    else:
        return base_queryset.filter(property_obj__property_type__name__iexact=property_type)


def clear_property_selection(request, property_type):
    """
    Clear the selected property from session.
    
    Args:
        request: Django request object
        property_type: Type of property ('hotel', 'lodge', 'venue', 'house')
    """
    session_key = f'selected_{property_type}_property_id'
    if session_key in request.session:
        del request.session[session_key]


def set_property_selection(request, property_id, property_type):
    """
    Set the selected property in session.
    
    Args:
        request: Django request object
        property_id: ID of the property to select
        property_type: Type of property ('hotel', 'lodge', 'venue', 'house')
    """
    # Validate property_id - handle 'all' case
    if property_id == 'all':
        property_id = None
    elif property_id:
        try:
            property_id = int(property_id)
        except (ValueError, TypeError):
            property_id = None
    
    session_key = f'selected_{property_type}_property_id'
    request.session[session_key] = property_id


def validate_property_id(property_id):
    """
    Validate and normalize property ID.
    
    Args:
        property_id: Property ID to validate (can be string, int, or None)
    
    Returns:
        int or None: Validated property ID or None if invalid
    """
    if property_id == 'all' or property_id is None:
        return None
    elif property_id:
        try:
            return int(property_id)
        except (ValueError, TypeError):
            return None
    return None


def get_property_selection_urls(property_type):
    """
    Get URLs for property selection actions.
    
    Args:
        property_type: Type of property ('hotel', 'lodge', 'venue', 'house')
    
    Returns:
        dict: URLs for selection actions
    """
    return {
        'select_property': f'properties:{property_type}_select_property',
        'clear_selection': f'properties:{property_type}_clear_selection',
        'dashboard': f'properties:{property_type}_dashboard',
        'bookings': f'properties:{property_type}_bookings',
        'rooms': f'properties:{property_type}_rooms',
        'customers': f'properties:{property_type}_customers',
        'payments': f'properties:{property_type}_payments',
        'reports': f'properties:{property_type}_reports',
    }
