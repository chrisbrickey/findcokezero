import requests
import urllib
from django.conf import settings
from django_webtest import WebTest

class GoogleMapsIntegrationTestCase(WebTest):
    """Verifies that Google Maps API service contract is maintained."""

    csrf_checks = False

    def test_google_maps_api_returns_expected_response_structure_including_geocoding(self) -> None:

        # Prepare url
        new_retailer_params = {
            "city": "New York",
            "street_address": "409 Edgecombe Avenue",
        }
        address_string = f"{new_retailer_params['street_address']}, {new_retailer_params['city']}"
        query_params = {'address': address_string, 'key': settings.GOOGLEMAPS_KEY}
        query_string = urllib.parse.urlencode(query_params)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{query_string}"

        # Call Google Maps API
        response = requests.get(url)

        # Verify response status code
        self.assertEqual(response.status_code, 200)

        # Verify a single result is returned
        response_json = response.json()
        self.assertEqual(len(response_json['results']), 1)

        # Verify all expected fields are present in response with correct type
        result = response_json['results'][0]
        latitude = result["geometry"]["location"]["lat"]
        longitude = result["geometry"]["location"]["lng"]

        postcode = None
        address_components = result["address_components"]
        for component in address_components:
            if "postal_code" in component.get("types"):
                postcode = component.get("short_name")

        self.assertIsInstance(latitude, float)
        self.assertIsInstance(longitude, float)
        self.assertIsInstance(postcode, str)

        # Verify geocoding values are accurate
        self.assertAlmostEqual(latitude, 40.8294, delta=0.01)
        self.assertAlmostEqual(longitude, -73.94, delta=0.01)
        self.assertEqual(int(postcode), 10032)