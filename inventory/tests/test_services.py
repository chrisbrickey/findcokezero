import requests

from decimal import Decimal
from django.test import TestCase
from unittest.mock import Mock, patch

from inventory.services.geocoding import GeocodingResult, GeocodingService
from inventory.services.exceptions import (
    GeocodingAPIError,
    GeocodingNetworkError,
    GeocodingNoResultsError,
)
from inventory.tests.types import RetailerTestFormDataWithGeocoding


class GeocodingServiceTest(TestCase):
    """Tests only the GeocodingService. Underlying HTTP calls to GoogleMaps API are mocked."""

    SAMPLE_RETAILER_DATA: RetailerTestFormDataWithGeocoding = {
        "name": "Plaid Pantry",
        "street_address": "1305 SW 11th Avenue",
        "city": "Portland",
        "postcode": "97201",
        "latitude": Decimal("45.5162468"),
        "longitude": Decimal("-122.6857963"),
    }

    def setUp(self) -> None:
        self.service = GeocodingService(api_key="test-api-key")

    @patch("inventory.services.geocoding.logger")
    @patch("inventory.services.geocoding.requests.get")
    def test_geocode_service_correctly_packages_api_responses(self, mock_get: Mock, mock_logger: Mock) -> None:
        mock_response = Mock()
        mock_response.json.return_value = self._build_mock_api_response()
        mock_get.return_value = mock_response

        result = self._call_geocode_service()

        self.assertIsInstance(result, GeocodingResult)
        self.assertEqual(result.latitude, self.SAMPLE_RETAILER_DATA["latitude"])
        self.assertEqual(result.longitude, self.SAMPLE_RETAILER_DATA["longitude"])
        self.assertEqual(result.postcode, self.SAMPLE_RETAILER_DATA["postcode"])

        mock_logger.info.assert_called_once_with(
            "Geocoding request successful for address: %s",
            "1305 SW 11th Avenue, Portland",
        )

    @patch("inventory.services.geocoding.logger")
    @patch("inventory.services.geocoding.requests.get")
    def test_timeout_raises_network_error(self, mock_get: Mock, mock_logger: Mock) -> None:
        mock_get.side_effect = requests.exceptions.Timeout()

        with self.assertRaises(GeocodingNetworkError):
            self._call_geocode_service()

        mock_logger.error.assert_called_once_with(
            "Geocoding request timed out for address: %s",
            "1305 SW 11th Avenue, Portland",
        )

    @patch("inventory.services.geocoding.logger")
    @patch("inventory.services.geocoding.requests.get")
    def test_request_exception_raises_network_error(self, mock_get: Mock, mock_logger: Mock) -> None:
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

        with self.assertRaises(GeocodingNetworkError):
            self._call_geocode_service()

        mock_logger.error.assert_called_once_with(
            "Network error during geocoding: %s",
            "Connection failed",
        )

    @patch("inventory.services.geocoding.logger")
    @patch("inventory.services.geocoding.requests.get")
    def test_api_error_status_raises_api_error(self, mock_get: Mock, mock_logger: Mock) -> None:
        mock_response = Mock()
        mock_response.json.return_value = self._build_mock_api_response(status="REQUEST_DENIED", results=[])
        mock_get.return_value = mock_response

        with self.assertRaises(GeocodingAPIError):
            self._call_geocode_service()

        mock_logger.error.assert_called_once_with("Geocoding API error: %s", "REQUEST_DENIED")

    @patch("inventory.services.geocoding.logger")
    @patch("inventory.services.geocoding.requests.get")
    def test_empty_results_raises_no_results_error(self, mock_get: Mock, mock_logger: Mock) -> None:
        mock_response = Mock()
        mock_response.json.return_value = self._build_mock_api_response(status="OK", results=[])
        mock_get.return_value = mock_response

        with self.assertRaises(GeocodingNoResultsError):
            self._call_geocode_service()

        mock_logger.warning.assert_called_once_with("No geocoding results for this address")

    @patch("inventory.services.geocoding.requests.get")
    def test_missing_postcode_returns_none(self, mock_get: Mock) -> None:
        mock_response = Mock()
        mock_response.json.return_value = self._build_mock_api_response(
            status="OK",
            results=[{
                "geometry": {
                    "location": {
                        "lat": float(self.SAMPLE_RETAILER_DATA["latitude"]),
                        "lng": float(self.SAMPLE_RETAILER_DATA["longitude"]),
                    }
                },
                "address_components": []
            }]
        )
        mock_get.return_value = mock_response

        result = self._call_geocode_service()

        self.assertIsInstance(result, GeocodingResult)
        self.assertIsNone(result.postcode)

    def _build_mock_api_response(
            self,
            status: str = "OK",
            results: list | None = None
    ) -> dict:
        if results is None:
            results = [{
                "geometry": {
                    "location": {
                        "lat": float(self.SAMPLE_RETAILER_DATA["latitude"]),
                        "lng": float(self.SAMPLE_RETAILER_DATA["longitude"]),
                    }
                },
                "address_components": [
                    {"types": ["postal_code"], "short_name": self.SAMPLE_RETAILER_DATA["postcode"]}
                ]
            }]
        return {"status": status, "results": results}

    def _call_geocode_service(self) -> GeocodingResult:
        return self.service.geocode_address(
            street_address=self.SAMPLE_RETAILER_DATA["street_address"],
            city=self.SAMPLE_RETAILER_DATA["city"],
        )