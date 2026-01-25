"""Tests for the GeocodingService."""

# disable logging when running these tests
import logging
logging.disable(logging.CRITICAL)

from decimal import Decimal
from unittest.mock import MagicMock, patch
from django.test import TestCase, override_settings

from inventory.services import (
    GeocodingAPIError,
    GeocodingNetworkError,
    GeocodingNoResultsError,
    GeocodingResult,
    GeocodingService,
)


class GeocodingServiceTests(TestCase):
    """Test cases for GeocodingService."""

    def setUp(self) -> None:
        self.service = GeocodingService(api_key="test-api-key")

    def test_successful_geocoding(self) -> None:
        """Test successful geocoding returns coordinates and postcode."""
        mock_response = {
            "status": "OK",
            "results": [
                {
                    "geometry": {"location": {"lat": 40.7128, "lng": -74.0060}},
                    "address_components": [
                        {"types": ["postal_code"], "short_name": "10001"},
                    ],
                }
            ],
        }

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=MagicMock(return_value=mock_response),
                raise_for_status=MagicMock(),
            )

            result = self.service.geocode_address(
                street_address="123 Main St",
                city="New York",
                postcode=None,
            )

        self.assertIsInstance(result, GeocodingResult)
        self.assertEqual(result.latitude, Decimal("40.7128"))
        self.assertEqual(result.longitude, Decimal("-74.006"))
        self.assertEqual(result.postcode, 10001)

    def test_geocoding_with_user_provided_postcode(self) -> None:
        """Test that user-provided postcode doesn't affect geocoding result."""
        mock_response = {
            "status": "OK",
            "results": [
                {
                    "geometry": {"location": {"lat": 51.5074, "lng": -0.1278}},
                    "address_components": [
                        {"types": ["postal_code"], "short_name": "12345"},
                    ],
                }
            ],
        }

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=MagicMock(return_value=mock_response),
                raise_for_status=MagicMock(),
            )

            result = self.service.geocode_address(
                street_address="10 Downing St",
                city="London",
                postcode="99999",  # User-provided postcode
            )

        # The service returns what the API found - serializer decides whether to use it
        self.assertEqual(result.postcode, 12345)

    def test_geocoding_no_results(self) -> None:
        """Test that GeocodingNoResultsError is raised for invalid addresses."""
        mock_response = {
            "status": "ZERO_RESULTS",
            "results": [],
        }

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=MagicMock(return_value=mock_response),
                raise_for_status=MagicMock(),
            )

            with self.assertRaises(GeocodingNoResultsError) as ctx:
                self.service.geocode_address(
                    street_address="Invalid Address",
                    city="Nowhere",
                )

        self.assertIn("Invalid Address, Nowhere", str(ctx.exception))

    def test_geocoding_api_error(self) -> None:
        """Test that GeocodingAPIError is raised for API errors."""
        mock_response = {
            "status": "REQUEST_DENIED",
            "error_message": "Invalid API key",
        }

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=MagicMock(return_value=mock_response),
                raise_for_status=MagicMock(),
            )

            with self.assertRaises(GeocodingAPIError) as ctx:
                self.service.geocode_address(
                    street_address="123 Main St",
                    city="New York",
                )

        self.assertEqual(ctx.exception.status, "REQUEST_DENIED")

    def test_geocoding_network_timeout(self) -> None:
        """Test that GeocodingNetworkError is raised on timeout."""
        import requests

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

            with self.assertRaises(GeocodingNetworkError):
                self.service.geocode_address(
                    street_address="123 Main St",
                    city="New York",
                )

    def test_geocoding_network_error(self) -> None:
        """Test that GeocodingNetworkError is raised on network failure."""
        import requests

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

            with self.assertRaises(GeocodingNetworkError):
                self.service.geocode_address(
                    street_address="123 Main St",
                    city="New York",
                )

    def test_non_numeric_postcode_returns_none(self) -> None:
        """Test that non-numeric postcodes (UK, Canada) return None."""
        mock_response = {
            "status": "OK",
            "results": [
                {
                    "geometry": {"location": {"lat": 51.5074, "lng": -0.1278}},
                    "address_components": [
                        {"types": ["postal_code"], "short_name": "SW1A 1AA"},
                    ],
                }
            ],
        }

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=MagicMock(return_value=mock_response),
                raise_for_status=MagicMock(),
            )

            result = self.service.geocode_address(
                street_address="10 Downing St",
                city="London",
            )

        self.assertEqual(result.latitude, Decimal("51.5074"))
        self.assertEqual(result.longitude, Decimal("-0.1278"))
        self.assertIsNone(result.postcode)

    def test_address_without_postcode_component(self) -> None:
        """Test geocoding when API response has no postcode component."""
        mock_response = {
            "status": "OK",
            "results": [
                {
                    "geometry": {"location": {"lat": 40.7128, "lng": -74.0060}},
                    "address_components": [
                        {"types": ["locality"], "short_name": "New York"},
                    ],
                }
            ],
        }

        with patch("inventory.services.geocoding.requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                json=MagicMock(return_value=mock_response),
                raise_for_status=MagicMock(),
            )

            result = self.service.geocode_address(
                street_address="123 Main St",
                city="New York",
            )

        self.assertEqual(result.latitude, Decimal("40.7128"))
        self.assertEqual(result.longitude, Decimal("-74.006"))
        self.assertIsNone(result.postcode)

    @override_settings(GOOGLEMAPS_KEY="settings-api-key")
    def test_uses_settings_api_key_by_default(self) -> None:
        """Test that the service uses settings.GOOGLEMAPS_KEY by default."""
        service = GeocodingService()
        self.assertEqual(service.api_key, "settings-api-key")

    def test_custom_timeout(self) -> None:
        """Test that custom timeout is used."""
        service = GeocodingService(api_key="test", timeout=30)
        self.assertEqual(service.timeout, 30)

    def test_build_address_string_with_postcode(self) -> None:
        """Test address string building with postcode."""
        address = self.service._build_address_string(
            street_address="123 Main St",
            city="New York",
            postcode="10001",
        )
        self.assertEqual(address, "123 Main St, New York, 10001")

    def test_build_address_string_without_postcode(self) -> None:
        """Test address string building without postcode."""
        address = self.service._build_address_string(
            street_address="123 Main St",
            city="New York",
            postcode=None,
        )
        self.assertEqual(address, "123 Main St, New York")
