"""
Mock fixtures for Google Maps API responses in tests.
"""
from typing import Any
from urllib.parse import parse_qs, urlparse


def create_google_maps_response(
    lat: float, lng: float, postcode: int | None = None
) -> dict[str, Any]:
    """Build a mock Google Maps geocoding API response."""
    address_components: list[dict[str, Any]] = []
    if postcode is not None:
        address_components.append({
            "long_name": str(postcode),
            "short_name": str(postcode),
            "types": ["postal_code"]
        })

    return {
        "results": [
            {
                "geometry": {
                    "location": {
                        "lat": lat,
                        "lng": lng
                    }
                },
                "address_components": address_components
            }
        ],
        "status": "OK"
    }


# Pre-built responses for all test addresses
MOCK_RESPONSES: dict[str, dict[str, Any]] = {
    # setUp retailers
    "test_street_1, San Francisco, 94107": create_google_maps_response(
        37.7749, -122.4194
    ),
    "test_street_2, New York, 10003": create_google_maps_response(
        40.7128, -74.0060
    ),
    # test_view_retailers_by_postcode_and_soda
    "new_retailer_street, San Francisco, 94107": create_google_maps_response(
        37.7749, -122.4194
    ),
    # test_create_retailer_without_sodas
    "new_retailer_street, New York, 10009": create_google_maps_response(
        40.7275, -73.98
    ),
    # test_create_retailer_with_sodas
    "new_retailer_street, Los Angeles, 90291": create_google_maps_response(
        33.9925, -118.4627
    ),
    # test_create_retailer_without_postcode (no postcode in address, API returns it)
    "409 Edgecombe Avenue, New York": create_google_maps_response(
        40.8294, -73.94, postcode=10032
    ),
    # test_create_retailer_with_postcode
    "12621 N Frank Lloyd Wright Boulevard, Scottsdale, 85250": create_google_maps_response(
        33.6189, -111.8953
    ),
    # test_create_retailer_with_same_name_fails
    "unique_street_address, Chicago, 60601": create_google_maps_response(
        41.8819, -87.6278
    ),
    # test_create_retailer_with_same_street_address_fails
    "test_street_1, Chicago, 60601": create_google_maps_response(
        41.8819, -87.6278
    ),
}


class MockResponse:
    """Mimics requests.Response with .json() method."""

    def __init__(self, json_data: dict[str, Any]) -> None:
        self._json_data = json_data

    def json(self) -> dict[str, Any]:
        return self._json_data


def mock_requests_get(url: str) -> MockResponse:
    """
    Replacement function for requests.get that parses address from URL
    and returns appropriate mock response.
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    address = query_params.get("address", [""])[0]

    if address in MOCK_RESPONSES:
        return MockResponse(MOCK_RESPONSES[address])

    # Fallback for unexpected addresses - return empty results
    return MockResponse({"results": [], "status": "ZERO_RESULTS"})
