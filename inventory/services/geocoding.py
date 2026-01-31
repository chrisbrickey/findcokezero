import logging
import requests
import urllib

from dataclasses import dataclass
from decimal import Decimal
from django.conf import settings

from inventory.types import GoogleMapsAddressComponent, GoogleMapsGeocodeResponse

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
    postcode: str | None = None

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
            postcode: str | None = None,
    ) -> GeocodingResult:
        """
        Retrieve and format geocoding data from Google Maps API

         Returns:
            GeocodingResult with latitude, longitude, and postcode.

        Raises:
            GeocodingAPIError: If the API returns an error status.
            GeocodingNetworkError: If a network error occurs.
            GeocodingNoResultsError: If no results are found.
        """

        formatted_address = self._build_address_string(street_address, city, postcode)
        response_data = self._make_api_request(formatted_address)
        return self._parse_response(response_data)

    def _build_address_string(
        self,
        street_address: str,
        city: str,
        postcode: str | None,
    ) -> str:
        """Build a formatted address string for the API request."""

        postcode_suffix = f", {postcode}" if postcode else ""
        return f"{street_address}, {city}{postcode_suffix}"

    def _make_api_request(self, address: str):
        """
        Makes HTTP request to the Google Maps Geocoding API using requests library.

        Args:
            address: Formatted address string
        Returns:
            Parsed JSON response
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

        logger.info("Geocoding request successful for address: %s", address)
        return data

    def _parse_response(self, data: GoogleMapsGeocodeResponse) -> GeocodingResult:
        """
        Parse the API response and extract coordinates.

        Args:
            data: Parsed JSON response from the API.
        Returns:
            GeocodingResult with latitude, longitude, postcode
        Raises:
            GeocodingNoResultsError: If no results are found.
        """

        results = data.get("results", [])
        if not results:
            logger.warning("No geocoding results for this address")
            raise GeocodingNoResultsError

        result = results[0]

        # extract latitude and longitude as Decimals to apply exact arithmetic
        location = result["geometry"]["location"]
        latitude = Decimal(str(location["lat"]))
        longitude = Decimal(str(location["lng"]))

        # extract postcode
        address_components = result.get("address_components", [])
        postcode = self._extract_postcode(address_components)

        return GeocodingResult(
            latitude=latitude,
            longitude=longitude,
            postcode=postcode,
        )

    def _extract_postcode(
            self,
            address_data: list[GoogleMapsAddressComponent]
    ) -> str | None:
        """
        Extract postcode from address components portion of response from Google Maps API.

        Returns: Postcode as a string. None if no postcode in response data.
        """

        for component in address_data:
            if "postal_code" in component.get("types", []):
                return component.get("short_name", "")

        return None

