"""
Utility functions for properties app
"""
import requests
import time
from typing import Optional, Tuple
from django.conf import settings
from django.db.models import Q
from .models import Property
import logging

logger = logging.getLogger(__name__)


def geocode_address(address: str, region: str = None, country: str = "Tanzania") -> Optional[Tuple[float, float]]:
    """
    Geocode an address to get latitude and longitude coordinates using SerpApi Google Maps API.
    
    This function uses SerpApi to access Google Maps geocoding, which provides better accuracy
    than OpenStreetMap, especially for Tanzania addresses.
    
    Falls back to OpenStreetMap Nominatim API if SerpApi is not configured or fails.
    
    Args:
        address: The address string to geocode
        region: Optional region name to improve accuracy
        country: Country name (default: Tanzania)
    
    Returns:
        Tuple of (latitude, longitude) if successful, None otherwise
    """
    if not address or not address.strip():
        return None
    
    # Check if SerpApi key is configured
    if not settings.SERPAPI_KEY:
        logger.warning("SERPAPI_KEY not configured. Falling back to OpenStreetMap.")
        return _geocode_address_openstreetmap(address, region, country)
    
    # Build search query
    address_clean = address.strip()
    
    # Build full address string for better accuracy
    if region:
        full_address = f"{address_clean}, {region}, {country}"
    else:
        full_address = f"{address_clean}, {country}"
    
    try:
        from serpapi import GoogleSearch
        
        # Use SerpApi Google Maps API for geocoding
        params = {
            "q": full_address,
            "engine": "google_maps",
            "api_key": settings.SERPAPI_KEY,
            "type": "search",
            "hl": "en",  # Language: English
            "gl": "tz",  # Country: Tanzania
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for errors
        if "error" in results:
            logger.error(f"SerpApi error for address '{address}': {results.get('error', 'Unknown error')}")
            return None
        
        # Extract coordinates from results
        if "local_results" in results and results["local_results"]:
            # Get first result
            first_result = results["local_results"][0]
            gps = first_result.get("gps_coordinates", {})
            
            if gps.get("latitude") and gps.get("longitude"):
                lat = float(gps["latitude"])
                lon = float(gps["longitude"])
                logger.info(f"Geocoded address '{address}' to coordinates ({lat}, {lon}) using SerpApi")
                return (lat, lon)
        
        # If no local_results, try place_results
        if "place_results" in results:
            place = results["place_results"]
            gps = place.get("gps_coordinates", {})
            
            if gps.get("latitude") and gps.get("longitude"):
                lat = float(gps["latitude"])
                lon = float(gps["longitude"])
                logger.info(f"Geocoded address '{address}' to coordinates ({lat}, {lon}) using SerpApi")
                return (lat, lon)
        
        logger.warning(f"Geocoding failed for address '{address}': No coordinates found in SerpApi results")
        return None
        
    except ImportError:
        logger.error("SerpApi library not installed. Falling back to OpenStreetMap.")
        return _geocode_address_openstreetmap(address, region, country)
    except Exception as e:
        logger.warning(f"SerpApi geocoding error for address '{address}': {str(e)}. Falling back to OpenStreetMap.")
        return _geocode_address_openstreetmap(address, region, country)


def _geocode_address_openstreetmap(address: str, region: str = None, country: str = "Tanzania") -> Optional[Tuple[float, float]]:
    """
    Fallback geocoding using OpenStreetMap Nominatim API.
    Used when SerpApi is not available or fails.
    
    Args:
        address: The address string to geocode
        region: Optional region name to improve accuracy
        country: Country name (default: Tanzania)
    
    Returns:
        Tuple of (latitude, longitude) if successful, None otherwise
    """
    if not address or not address.strip():
        return None
    
    # Build search query - try multiple variations for better results
    address_clean = address.strip()
    
    # Try different query formats
    queries_to_try = []
    
    # 1. Full address with region and country
    if region:
        queries_to_try.append(f"{address_clean}, {region}, {country}")
    queries_to_try.append(f"{address_clean}, {country}")
    
    # 2. If address seems incomplete, try adding region
    if region and 'dar' not in address_clean.lower():
        queries_to_try.append(f"{address_clean}, {region}, {country}")
    
    # 3. Just the address (fallback)
    queries_to_try.append(address_clean)
    
    try:
        # Use Nominatim API (OpenStreetMap's geocoding service)
        # Free, no API key required, but has rate limits
        url = "https://nominatim.openstreetmap.org/search"
        
        # Try each query variation until we get a result
        for query in queries_to_try:
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'tz',  # Tanzania country code
            }
        
            headers = {
                'User-Agent': 'Maisha Property Management System',  # Required by Nominatim
            }
            
            # Make request with rate limiting consideration
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result.get('lat', 0))
                    lon = float(result.get('lon', 0))
                    
                    if lat != 0 and lon != 0:
                        logger.info(f"Geocoded address '{address}' to coordinates ({lat}, {lon}) using OpenStreetMap fallback")
                        return (lat, lon)
            
            # Small delay between attempts to respect rate limits
            time.sleep(0.5)
        
        logger.warning(f"Geocoding failed for address '{address}': No results found after trying {len(queries_to_try)} query variations")
        return None
        
    except requests.exceptions.Timeout:
        logger.error(f"Geocoding timeout for address '{address}'")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Geocoding error for address '{address}': {str(e)}")
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Geocoding parsing error for address '{address}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected geocoding error for address '{address}': {str(e)}")
        return None


def reverse_geocode(latitude: float, longitude: float) -> Optional[str]:
    """
    Reverse geocode coordinates to get an address using SerpApi Google Maps API.
    
    Falls back to OpenStreetMap Nominatim API if SerpApi is not configured or fails.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        Address string if successful, None otherwise
    """
    # Check if SerpApi key is configured
    if not settings.SERPAPI_KEY:
        logger.warning("SERPAPI_KEY not configured. Falling back to OpenStreetMap.")
        return _reverse_geocode_openstreetmap(latitude, longitude)
    
    try:
        from serpapi import GoogleSearch
        
        # Use SerpApi Google Maps API for reverse geocoding
        # Search for nearby places using coordinates
        params = {
            "q": f"{latitude},{longitude}",
            "engine": "google_maps",
            "api_key": settings.SERPAPI_KEY,
            "type": "search",
            "hl": "en",
            "gl": "tz",
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for errors
        if "error" in results:
            logger.error(f"SerpApi reverse geocoding error: {results.get('error', 'Unknown error')}")
            return None
        
        # Extract address from results
        if "local_results" in results and results["local_results"]:
            first_result = results["local_results"][0]
            address = first_result.get("address", "")
            if address:
                return address
        
        if "place_results" in results:
            place = results["place_results"]
            address = place.get("address", "")
            if address:
                return address
        
        return None
        
    except ImportError:
        logger.error("SerpApi library not installed. Falling back to OpenStreetMap.")
        return _reverse_geocode_openstreetmap(latitude, longitude)
    except Exception as e:
        logger.warning(f"SerpApi reverse geocoding error for coordinates ({latitude}, {longitude}): {str(e)}. Falling back to OpenStreetMap.")
        return _reverse_geocode_openstreetmap(latitude, longitude)


def _reverse_geocode_openstreetmap(latitude: float, longitude: float) -> Optional[str]:
    """
    Fallback reverse geocoding using OpenStreetMap Nominatim API.
    Used when SerpApi is not available or fails.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        Address string if successful, None otherwise
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
        }
        
        headers = {
            'User-Agent': 'Maisha Property Management System',
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and 'display_name' in data:
                return data['display_name']
        
        return None
        
    except Exception as e:
        logger.error(f"OpenStreetMap reverse geocoding error for coordinates ({latitude}, {longitude}): {str(e)}")
        return None


# Property management utility functions

def get_management_context(request, property_type):
    """Get context for property management views"""
    # Get selected property from session
    # Use format: selected_{property_type}_property_id (e.g., selected_hotel_property_id)
    selected_property_id = request.session.get(f'selected_{property_type}_property_id')
    selected_property = None
    if selected_property_id:
        try:
            selected_property = Property.objects.get(id=selected_property_id)
        except Property.DoesNotExist:
            pass
    
    # Get all properties of this type for the user
    if request.user.is_staff or request.user.is_superuser:
        properties = Property.objects.filter(property_type__name__iexact=property_type)
    else:
        properties = Property.objects.filter(
            property_type__name__iexact=property_type,
            owner=request.user
        )
    
    return {
        'selected_property': selected_property,
        'properties': properties,
        'property_type': property_type,
    }


def get_property_filtered_queryset(request, property_type):
    """Get filtered queryset for property type"""
    if request.user.is_staff or request.user.is_superuser:
        return Property.objects.filter(property_type__name__iexact=property_type)
    else:
        return Property.objects.filter(
            property_type__name__iexact=property_type,
            owner=request.user
        )


def set_property_selection(request, property_id, property_type):
    """Set selected property in session"""
    # Use format: selected_{property_type}_property_id (e.g., selected_hotel_property_id)
    request.session[f'selected_{property_type}_property_id'] = property_id
    request.session.modified = True


def clear_property_selection(request, property_type):
    """Clear selected property from session"""
    # Use format: selected_{property_type}_property_id (e.g., selected_hotel_property_id)
    session_key = f'selected_{property_type}_property_id'
    if session_key in request.session:
        del request.session[session_key]
        request.session.modified = True


def validate_property_id(property_id, user, property_type=None):
    """Validate that a property ID exists and user has access to it"""
    try:
        property_obj = Property.objects.get(id=property_id)
        
        # Check if property type matches if specified
        if property_type and property_obj.property_type.name.lower() != property_type.lower():
            return None
        
        # Check user access
        if user.is_staff or user.is_superuser:
            return property_obj
        elif property_obj.owner == user:
            return property_obj
        else:
            return None
    except Property.DoesNotExist:
        return None
