from django_webtest import WebTest

class RetailerGeocodingIntegrationTestCase(WebTest):
   """Integration tests verify that external service contracts are maintained."""

    csrf_checks = False

    def test_create_retailer_geocoding_with_real_api(self) -> None:
        """Integration test: verify real Google Maps API geocoding works
        and returns complete response structure."""

        new_retailer_params = {
            "name": "integration_test_retailer",
            "city": "New York",
            "street_address": "409 Edgecombe Avenue",
        }
        post_response = self.app.post_json('/api/retailers/', params=new_retailer_params)

        # Verify HTTP status
        self.assertEqual(post_response.status, "201 Created")

        response_data = post_response.json

        # Verify all expected fields are present in response
        expected_fields = {
            "id", "name", "street_address", "city", "postcode", "country",
            "latitude", "longitude", "timestamp_last_updated", "timestamp_created", "sodas"
        }
        self.assertEqual(set(response_data.keys()), expected_fields)

        # Verify field types
        self.assertIsInstance(response_data["id"], int)
        self.assertIsInstance(response_data["name"], str)
        self.assertIsInstance(response_data["street_address"], str)
        self.assertIsInstance(response_data["city"], str)
        self.assertIsInstance(response_data["postcode"], int)
        self.assertIsInstance(response_data["country"], str)
        self.assertIsInstance(response_data["latitude"], str)  # Decimal serialized as string
        self.assertIsInstance(response_data["longitude"], str)  # Decimal serialized as string
        self.assertIsInstance(response_data["timestamp_last_updated"], str)
        self.assertIsInstance(response_data["timestamp_created"], str)
        self.assertIsInstance(response_data["sodas"], list)

        # Verify input data was stored correctly
        self.assertEqual(response_data["name"], new_retailer_params["name"])
        self.assertEqual(response_data["street_address"], new_retailer_params["street_address"])
        self.assertEqual(response_data["city"], new_retailer_params["city"])

        # Verify geocoded values from real API (using approximate matching for coordinates)
        self.assertAlmostEqual(float(response_data["latitude"]), 40.8294, delta=0.01)
        self.assertAlmostEqual(float(response_data["longitude"]), -73.94, delta=0.01)
        self.assertEqual(response_data["postcode"], 10032)

        # Verify latitude/longitude are within valid ranges
        latitude = float(response_data["latitude"])
        longitude = float(response_data["longitude"])
        self.assertGreaterEqual(latitude, -90.0)
        self.assertLessEqual(latitude, 90.0)
        self.assertGreaterEqual(longitude, -180.0)
        self.assertLessEqual(longitude, 180.0)

        # Verify timestamps are ISO format strings
        self.assertRegex(response_data["timestamp_created"], r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertRegex(response_data["timestamp_last_updated"], r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")

        # Verify empty sodas list (none were associated)
        self.assertEqual(response_data["sodas"], [])
