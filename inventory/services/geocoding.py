"""Geocoding service for converting addresses to coordinates."""

import logging
import urllib.parse
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests
from django.conf import settings

from .exceptions import (
    GeocodingAPIError,
    GeocodingNetworkError,
    GeocodingNoResultsError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeocodingResult:
    """Immutable result from a geocoding operation."""

    latitude: Decimal
    longitude: Decimal
    postcode: int | None = None


class GeocodingService:
    """Service for geocoding addresses using Google Maps API."""

    GOOGLE_MAPS_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    DEFAULT_TIMEOUT = 10  # seconds

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int | None = None,
    ) -> None:
        """
        Initialize the geocoding service.

        Args:
            api_key: Google Maps API key. Defaults to settings.GOOGLEMAPS_KEY.
            timeout: Request timeout in seconds. Defaults to DEFAULT_TIMEOUT.
        """
        self.api_key = api_key or settings.GOOGLEMAPS_KEY
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def geocode_address(
        self,
        street_address: str,
        city: str,
        postcode: str | int | None = None,
    ) -> GeocodingResult:
        """
        Geocode an address to coordinates.

        Args:
            street_address: Street address.
            city: City name.
            postcode: Optional postcode/zip code.

        Returns:
            GeocodingResult with latitude, longitude, and optionally postcode.

        Raises:
            GeocodingAPIError: If the API returns an error status.
            GeocodingNetworkError: If a network error occurs.
            GeocodingNoResultsError: If no results are found.
        """
        address = self._build_address_string(street_address, city, postcode)
        response_data = self._make_api_request(address)
        return self._parse_response(response_data, address)

    def _build_address_string(
        self,
        street_address: str,
        city: str,
        postcode: str | int | None,
    ) -> str:
        """Build a formatted address string for the API request."""
        postcode_suffix = f", {postcode}" if postcode else ""
        return f"{street_address}, {city}{postcode_suffix}"

    def _make_api_request(self, address: str) -> dict[str, Any]:
        """
        Make the HTTP request to the Google Maps Geocoding API.

        Args:
            address: Formatted address string.

        Returns:
            Parsed JSON response.

        Raises:
            GeocodingAPIError: If the API returns an error status.
            GeocodingNetworkError: If a network error occurs.
        """
        query_params = {"address": address, "key": self.api_key}
        query_string = urllib.parse.urlencode(query_params)
        url = f"{self.GOOGLE_MAPS_GEOCODE_URL}?{query_string}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.Timeout:
            logger.error("Geocoding request timed out for address: %s", address)
            raise GeocodingNetworkError(f"Request timed out for address: {address}")
        except requests.exceptions.RequestException as e:
            logger.error("Network error during geocoding: %s", str(e))
            raise GeocodingNetworkError(f"Network error: {str(e)}")

        # Check API-level status
        status = data.get("status", "UNKNOWN_ERROR")
        if status not in ("OK", "ZERO_RESULTS"):
            logger.error("Geocoding API error: %s", status)
            raise GeocodingAPIError(status)

        return data

    def _parse_response(
        self, data: dict[str, Any], address: str
    ) -> GeocodingResult:
        """
        Parse the API response and extract coordinates.

        Args:
            data: Parsed JSON response from the API.
            address: Original address string (for error messages).

        Returns:
            GeocodingResult with coordinates and optional postcode.

        Raises:
            GeocodingNoResultsError: If no results are found.
        """
        results = data.get("results", [])
        if not results:
            logger.warning("No geocoding results for address: %s", address)
            raise GeocodingNoResultsError(address)

        result = results[0]
        location = result["geometry"]["location"]

        postcode = self._extract_postcode_from_address_components(
            result.get("address_components", [])
        )

        return GeocodingResult(
            latitude=Decimal(str(location["lat"])),
            longitude=Decimal(str(location["lng"])),
            postcode=postcode,
        )

    def _extract_postcode_from_address_components(
        self, address_components: list[dict[str, Any]]
    ) -> int | None:
        """
        Extract postcode from Google Maps API address components.

        Args:
            address_components: List of address component dicts from API.

        Returns:
            Integer postcode if found and numeric, None otherwise.
        """
        for component in address_components:
            if "postal_code" in component.get("types", []):
                try:
                    return int(component.get("short_name", ""))
                except ValueError:
                    # Non-numeric postal codes (e.g., UK, Canada) not yet supported
                    return None
        return None
