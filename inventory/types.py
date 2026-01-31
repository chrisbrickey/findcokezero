"""Type definitions for the inventory application."""

from typing import NotRequired, TypedDict


class GoogleMapsAddressComponent(TypedDict):
    """Single address component from Google Maps API."""

    types: list[str]
    short_name: str
    long_name: NotRequired[str]


class GoogleMapsLocation(TypedDict):
    """Geographic coordinates from Google Maps API."""

    lat: float
    lng: float


class GoogleMapsGeometry(TypedDict):
    """Geometry data from Google Maps API."""

    location: GoogleMapsLocation


class GoogleMapsResult(TypedDict):
    """Single result from Google Maps Geocoding API."""

    geometry: GoogleMapsGeometry
    address_components: list[GoogleMapsAddressComponent]


class GoogleMapsGeocodeResponse(TypedDict):
    """Full response from Google Maps Geocoding API."""

    status: str
    results: list[GoogleMapsResult]