import os
import unittest
from decimal import Decimal
from unittest.mock import patch

from django_webtest import WebTest

from inventory.services import GeocodingResult


def mock_geocode_address(
    street_address: str,
    city: str,
    postcode: str | int | None = None,
) -> GeocodingResult:
    """Mock geocoding that returns predictable coordinates based on city."""
    # Return different coordinates based on city for realistic test data
    city_coords = {
        "San Francisco": (Decimal("37.7749"), Decimal("-122.4194"), 94107),
        "New York": (Decimal("40.7128"), Decimal("-74.0060"), 10001),
        "Los Angeles": (Decimal("34.0522"), Decimal("-118.2437"), 90001),
        "Scottsdale": (Decimal("33.4942"), Decimal("-111.9261"), 85250),
    }
    lat, lng, default_postcode = city_coords.get(
        city, (Decimal("40.0"), Decimal("-74.0"), 10001)
    )
    return GeocodingResult(
        latitude=lat,
        longitude=lng,
        postcode=default_postcode,
    )


@patch(
    "inventory.services.geocoding.GeocodingService.geocode_address",
    side_effect=mock_geocode_address,
)
class RetailerWebTestCase(WebTest):
    csrf_checks = False

    retailer1_data = {
        "name": "test_retailer_1",
        "city": "San Francisco",
        "postcode": 94107,
        "street_address": "test_street_1",
    }

    retailer2_data = {
        "name": "test_retailer_2",
        "city": "New York",
        "postcode": 10003,
        "street_address": "test_street_2",
    }

    soda_ch_data = {
        "abbreviation": "CH",
        "low_calorie": "True",
        "name": "CherryCokeZero",
    }

    soda_vz_data = {
        "abbreviation": "VZ",
        "low_calorie": "True",
        "name": "VanillaCokeZero",
    }

    soda_cc_data = {
        "abbreviation": "CC",
        "low_calorie": "False",
        "name": "CokeClassic",
    }

    def setUp(self) -> None:
        # Create sodas first so we have their URLs

        post_soda_ch = self.app.post_json('/api/sodas/', params=self.soda_ch_data)
        self.soda_ch_url = post_soda_ch.json["url"]
        self.soda_ch_id = post_soda_ch.json["id"]

        post_soda_cc = self.app.post_json('/api/sodas/', params=self.soda_cc_data)
        self.soda_cc_url = post_soda_cc.json["url"]
        self.soda_cc_id = post_soda_cc.json["id"]

        post_soda_vz = self.app.post_json('/api/sodas/', params=self.soda_vz_data)
        self.soda_vz_url = post_soda_vz.json["url"]
        self.soda_vz_id = post_soda_vz.json["id"]

        # Create retailers with soda associations

        # retailer1: CH (CherryCokeZero) and CC (CokeClassic)
        retailer1_params = {**self.retailer1_data, "sodas": [self.soda_ch_url, self.soda_cc_url]}
        post_retailer_1  = self.app.post_json('/api/retailers/', params=retailer1_params)
        self.retailer1_id = post_retailer_1.json["id"]

        # retailer2: VZ (VanillaCokeZero) and CC (CokeClassic)
        retailer2_params = {**self.retailer2_data, "sodas": [self.soda_vz_url, self.soda_cc_url]}
        self.app.post_json('/api/retailers/', params=retailer2_params)

    def test_view_retailers_returns_all(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with no params retrieves all retailers"""

        get_response = self.app.get('/api/retailers/')

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

        result_names = [r["name"] for r in get_response.json]
        self.assertIn(self.retailer1_data["name"], result_names)
        self.assertIn(self.retailer2_data["name"], result_names)

    def test_view_retailer_by_id_succeeds(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with retailer ID retrieves single retailer"""

        get_response = self.app.get(f"/api/retailers/{self.retailer1_id}/")

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(get_response.json["name"], self.retailer1_data["name"])
        self.assertEqual(get_response.json["city"], self.retailer1_data["city"])
        self.assertEqual(get_response.json["street_address"], self.retailer1_data["street_address"])

    def test_view_retailers_by_soda_returns_filtered_results(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with one soda in params retrieves associated retailers"""

        # single record
        get_response = self.app.get(f"/api/sodas/{self.soda_ch_id}/retailers/")
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 1)
        self.assertEqual(get_response.json[0]["name"], self.retailer1_data["name"])

        # multiple records
        get_response = self.app.get(f"/api/sodas/{self.soda_cc_id}/retailers/")
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)
        result_names = [r["name"] for r in get_response.json]
        self.assertIn(self.retailer1_data["name"], result_names)
        self.assertIn(self.retailer2_data["name"], result_names)

    def test_view_retailers_by_bad_soda_returns_404(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with invalid soda ID returns 404 (not 500 index error)"""

        # soda id 99999 will not exist in the test database
        get_response = self.app.get('/api/sodas/99999/retailers/', expect_errors=True)
        self.assertEqual(get_response.status, "404 Not Found")

    def test_view_retailers_by_postcode_returns_filtered_results(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with postcode in params retrieves associated retailers"""

        get_response = self.app.get(f"/api/retailers/?postcode={self.retailer2_data['postcode']}")

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 1)
        self.assertEqual(get_response.json[0]["name"], self.retailer2_data["name"])

    def test_view_retailers_by_postcode_and_soda_returns_filtered_results(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with postcode and one soda type in query string retrieves associated retailers"""

        # retailer3: VZ (VanillaCokeZero) and same postcode as retailer1
        new_retailer_params = {
            "name": "new_retailer",
            "city": "San Francisco",
            "postcode": self.retailer1_data["postcode"],
            "street_address": "new_retailer_street",
            "sodas": [self.soda_vz_url]
        }
        self.app.post_json('/api/retailers/', params=new_retailer_params)

        # Make GET request using params to filter by postcode and soda
        get_params = {
            "postcode": self.retailer1_data["postcode"],
            "sodas": self.soda_ch_data["abbreviation"],
        }
        get_response = self.app.get("/api/retailers/", params=get_params)

        # Verify response
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 1)
        self.assertEqual(get_response.json[0]["name"], self.retailer1_data["name"])

    def test_view_retailers_by_multiple_sodas_returns_filtered_results(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP get request with multiple soda types in params retrieves associated retailers"""

        get_response = self.app.get("/api/retailers/?sodas=CC,VZ")

        # Verify response
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 1)
        self.assertEqual(get_response.json[0]["name"], self.retailer2_data["name"])

    def test_create_retailer_without_sodas_succeeds(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP post request with required data results in creation of object and response with all object data"""

        new_retailer_params = {
            "name": "new_retailer",
            "city": "New York",
            "postcode": 10009,
            "street_address": "new_retailer_street",
        }
        post_response = self.app.post_json('/api/retailers/', params=new_retailer_params)

        # Verify response structure: response code with retailer data
        self.assertEqual(post_response.status, "201 Created")
        self.assertEqual(post_response.json["name"], new_retailer_params["name"])
        self.assertEqual(post_response.json["city"], new_retailer_params["city"])
        self.assertEqual(post_response.json["street_address"], new_retailer_params["street_address"])

        # Verify id was created and can be used to fetch the retailer
        self.assertIn("id", post_response.json,
                      "Expected Retailer object to have key 'id', but it was missing.")
        new_retailer_id = post_response.json["id"]
        get_response = self.app.get(f"/api/retailers/{new_retailer_id}/")
        self.assertEqual(get_response.status, "200 OK")

        # Verify latitude and longitude were populated (mocked values)
        self.assertIn("latitude", post_response.json,
                      "Expected Retailer object to have key 'latitude', but it was missing.")
        self.assertIn("longitude", post_response.json,
                      "Expected Retailer object to have key 'longitude', but it was missing.")
        self.assertIsNotNone(post_response.json["latitude"])
        self.assertIsNotNone(post_response.json["longitude"])

    def test_create_retailer_with_sodas_succeeds(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP post request with soda data results in creation of object and response with all object data"""

        new_retailer_params = {
            "name": "new_retailer",
            "city": "Los Angeles",
            "postcode": 90291,
            "street_address": "new_retailer_street",
            "sodas": [self.soda_ch_url, self.soda_vz_url]
        }
        post_response = self.app.post_json('/api/retailers/', params=new_retailer_params)

        # Verify response structure: response code with retailer data
        self.assertEqual(post_response.status, "201 Created")
        self.assertEqual(post_response.json["name"], new_retailer_params["name"])
        self.assertEqual(post_response.json["sodas"], new_retailer_params["sodas"])

    def test_create_retailer_without_postcode_populates_all_geocoding(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP post request without postcode will populate latitude, longitude,
        and numeric postcode via geocoding service"""

        new_retailer_params = {
            "name": "new_retailer",
            "city": "New York",
            "street_address": "409 Edgecombe Avenue",
        }
        post_response = self.app.post_json('/api/retailers/', params=new_retailer_params)

        # Verify latitude, longitude, and zip code were populated
        self.assertEqual(post_response.status, "201 Created")
        self.assertIn("latitude", post_response.json,
                      "Expected Retailer object to have key 'latitude', but it was missing.")
        self.assertIn("longitude", post_response.json,
                      "Expected Retailer object to have key 'longitude', but it was missing.")
        self.assertIn("postcode", post_response.json,
                      "Expected Retailer object to have key 'postcode', but it was missing.")

        # Verify data was populated (using mocked values for New York)
        self.assertEqual(Decimal(post_response.json["latitude"]), Decimal("40.7128"))
        self.assertEqual(Decimal(post_response.json["longitude"]), Decimal("-74.0060"))
        self.assertEqual(post_response.json["postcode"], 10001)

    def test_create_retailer_with_postcode_preserves_user_value(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP post request with user-provided postcode preserves that value
        instead of over-writing it with geocoded postcode"""

        user_provided_postcode = 85250
        new_retailer_params = {
            "name": "new_retailer_user_postcode",
            "city": "Scottsdale",
            "street_address": "12621 N Frank Lloyd Wright Boulevard",
            "postcode": user_provided_postcode,
        }
        post_response = self.app.post_json('/api/retailers/', params=new_retailer_params)

        self.assertEqual(post_response.status, "201 Created")
        self.assertEqual(post_response.json["postcode"], user_provided_postcode)

    def test_create_retailer_with_same_name_fails(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP post request with duplicate name returns error"""

        duplicate_name_params = {
            "name": self.retailer1_data["name"],  # duplicate name
            "city": "Chicago",
            "postcode": 60601,
            "street_address": "unique_street_address",
        }
        post_response = self.app.post_json('/api/retailers/', params=duplicate_name_params, expect_errors=True)

        self.assertEqual(post_response.status, "400 Bad Request")

    def test_create_retailer_with_same_street_address_fails(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP post request with duplicate street_address returns error"""

        duplicate_address_params = {
            "name": "unique_retailer_name",
            "city": "Chicago",
            "postcode": 60601,
            "street_address": self.retailer1_data["street_address"],  # duplicate address
        }
        post_response = self.app.post_json('/api/retailers/', params=duplicate_address_params, expect_errors=True)

        self.assertEqual(post_response.status, "400 Bad Request")

    def test_update_retailer_with_sodas(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP put request updates retailer with new soda"""

        # Get existing list of sodas from retailer1
        get_response = self.app.get(f"/api/retailers/{self.retailer1_id}/")
        sodas_list_before = get_response.json["sodas"]
        self.assertEqual(len(sodas_list_before), 2)

        # Update retailer1 with VanillaCokeZero (adding to existing sodas)
        updated_sodas = sodas_list_before + [self.soda_vz_url]
        update_params = {**self.retailer1_data, "sodas": updated_sodas}
        put_response = self.app.put_json(f"/api/retailers/{self.retailer1_id}/", params=update_params)

        # Verify sodas updated
        self.assertEqual(put_response.json["name"], self.retailer1_data["name"])
        sodas_list_after = put_response.json["sodas"]
        self.assertEqual(len(sodas_list_after), 3)

        self.assertIn(self.soda_ch_url, sodas_list_after)
        self.assertIn(self.soda_cc_url, sodas_list_after)
        self.assertIn(self.soda_vz_url, sodas_list_after)

    def test_update_retailer_with_same_soda_does_not_create_duplicate(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP put request adding already-associated soda does not create duplicates"""

        # Get existing list of sodas from retailer1 (should have CH and CC)
        get_response = self.app.get(f"/api/retailers/{self.retailer1_id}/")
        sodas_list_before = get_response.json["sodas"]
        self.assertEqual(len(sodas_list_before), 2)

        # Attempt to update retailer1 with CherryCokeZero again (already present)
        update_params = {**self.retailer1_data, "sodas": [self.soda_ch_url, self.soda_cc_url, self.soda_ch_url]}
        put_response = self.app.put_json(f"/api/retailers/{self.retailer1_id}/", params=update_params)

        # Verify no duplicate was created
        self.assertEqual(put_response.status, "200 OK")
        sodas_list_after = put_response.json["sodas"]
        self.assertEqual(len(sodas_list_after), 2)

    def test_delete_retailer_succeeds(self, mock_geocode: unittest.mock.MagicMock) -> None:
        """HTTP delete request removes retailer"""

        # Delete retailer1
        delete_response = self.app.delete(f"/api/retailers/{self.retailer1_id}/")
        self.assertEqual(delete_response.status, "204 No Content")

        # Verify retailer1 no longer exists
        get_response = self.app.get(f"/api/retailers/{self.retailer1_id}/", expect_errors=True)
        self.assertEqual(get_response.status, "404 Not Found")


@unittest.skipUnless(
    os.environ.get("RUN_INTEGRATION_TESTS"),
    "Skipping integration tests that hit real Google Maps API. Set RUN_INTEGRATION_TESTS=1 to run.",
)
class RetailerGeocodingIntegrationTestCase(WebTest):
    """Integration tests that hit the real Google Maps API.

    These tests are skipped by default. To run them:
        RUN_INTEGRATION_TESTS=1 python manage.py test inventory.tests.tests_retailers_web.RetailerGeocodingIntegrationTestCase
    """

    csrf_checks = False

    def test_create_retailer_geocoding_with_real_api(self) -> None:
        """Integration test: verify real Google Maps API geocoding works."""

        new_retailer_params = {
            "name": "integration_test_retailer",
            "city": "New York",
            "street_address": "409 Edgecombe Avenue",
        }
        post_response = self.app.post_json('/api/retailers/', params=new_retailer_params)

        # Verify latitude, longitude, and zip code were populated
        self.assertEqual(post_response.status, "201 Created")

        # Verify correctness of data from real API (using approximate matching)
        self.assertAlmostEqual(
            float(post_response.json["latitude"]), 40.8294, delta=0.01
        )
        self.assertAlmostEqual(
            float(post_response.json["longitude"]), -73.94, delta=0.01
        )
        self.assertEqual(post_response.json["postcode"], 10032)
