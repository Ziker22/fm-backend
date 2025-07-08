import os
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from typing import Optional, Tuple, Dict, Any, Union, TypeVar

import logging

logger = logging.getLogger(__name__)

def geocode_address(
    street: Optional[str] = None,
    zip_code: Optional[str] = None,
    city: Optional[str] = None,
    place_name: Optional[str] = None,
    country_code: str = 'us'
) -> Tuple[Optional[Point], Optional[Dict[str, Any]]]:
    """
    Geocode an address using the Mapbox Search Box API.

    Args:
        street: Street address
        zip_code: ZIP/Postal code
        city: City name
        place_name: Name of the place
        country_code: Two-letter country code (default: 'us')

    Returns:
        Tuple[Optional[Point], Optional[Dict[str, Any]]]: (Point object with lat/lon, raw response data) or (None, None) if geocoding fails
    """
    # Get API key from settings or environment
    api_key = getattr(settings, 'MAPBOX_API_KEY', os.environ.get('MAPBOX_API_KEY'))

    if not api_key:
        raise ValueError("Mapbox API key not found. Please set MAPBOX_API_KEY in .env or settings.")

    # Build the address query
    address_parts = []
    if place_name:
        address_parts.append(place_name)
    # if street:
    #     address_parts.append(street)
    # if zip_code:
    #     address_parts.append(zip_code)
    if city:
        address_parts.append(city)

    if not address_parts:
        return None, None

    query = ", ".join(address_parts)

    # Make the API request to Search Box API
    url = "https://api.mapbox.com/search/searchbox/v1/forward"
    params = {
        'access_token': api_key,
        'q': query,
        'limit': 1,  # We only need the best match
        'country': country_code,
        'types': 'address,poi,place',  # Include addresses, points of interest, and place names
        'language': 'en',  # Default language for results
    }

    try:
        logger.info(f"Geocoding request: {url} with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()
        logger.info(f"Geocoding response: {data}")
        # Check if we got any results
        if not data.get('features'):
            return None, data

        # Get the coordinates (Mapbox Search Box returns [longitude, latitude] in coordinates)
        feature = data['features'][0]
        lon, lat = feature['geometry']['coordinates']

        # Create a Point object
        point = Point(lon, lat)

        return point, data

    except Exception as e:
        # Log the error
        logger.exception(f"Geocoding error: {str(e)}")
        return None, None
