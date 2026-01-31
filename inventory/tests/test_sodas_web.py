# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django_webtest import WebTest

from inventory.tests.types import SodaTestFormData


class SodaWebTestCase(WebTest):
    csrf_checks = False

    soda_ch_data: SodaTestFormData = {
        "abbreviation": "CH",
        "low_calorie": "True",
        "name": "CherryCokeZero",
    }

    soda_cc_data: SodaTestFormData = {
        "abbreviation": "CC",
        "low_calorie": "False",
        "name": "CokeClassic",
    }

    def setUp(self) -> None:
        self.post_soda_ch = self.app.post_json('/api/sodas/', params=self.soda_ch_data)
        self.post_soda_cc = self.app.post_json('/api/sodas/', params=self.soda_cc_data)

    def test_view_sodas_returns_all(self) -> None:
        """HTTP get request with no params retrieves all sodas"""

        get_response = self.app.get('/api/sodas/')

        self.assertEqual(get_response.status, "200 OK")

        # verify content
        response_data = get_response.json
        self.assertEqual(len(response_data), 2)

        result_names = [soda["name"] for soda in response_data]
        self.assertIn(self.soda_ch_data["name"], result_names)
        self.assertIn(self.soda_cc_data["name"], result_names)

    def test_view_all_sodas_by_retailer_filters_correctly(self) -> None:
        """HTTP get request with retailer ID and 'sodas' in params retrieves all sodas associated with that retailer"""

        # create the retailer with associated sodas
        soda_ch_url = self.post_soda_ch.json["url"]
        post_retailer_response = self.app.post_json('/api/retailers/',
                                                          params={"city": "San Francisco",
                                                                  "name": "Shell",
                                                                  "postcode": "94107",
                                                                  "street_address": "598 Bryant Street",
                                                                  "sodas": [soda_ch_url]})

        # filter sodas by the new retailer
        retailer_id = post_retailer_response.json["id"]
        get_response = self.app.get(f"/api/retailers/{retailer_id}/sodas/")

        # verify successful response that only includes the associated soda
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 1)

        result_name = get_response.json[0]["name"]
        self.assertEqual(result_name, self.soda_ch_data["name"])

    def test_view_all_sodas_by_bad_retailer_returns_404(self) -> None:
        """HTTP get request with invalid retailer ID returns 404 (not 500 index error)"""

        # retailer id 99999 will not exist in the test database
        get_response = self.app.get('/api/retailers/99999/sodas/', expect_errors=True)

        self.assertEqual(get_response.status, "404 Not Found")

    def test_create_soda_with_correct_params_succeeds(self) -> None:
        """HTTP request post request with valid data results in creation of object and correct response"""

        new_soda_params = {
            "abbreviation": "VZ",
            "low_calorie": "True",
            "name": "Vanilla Coke Zero"
        }
        post_response = self.app.post_json('/api/sodas/', params=new_soda_params)

        self.assertEqual(post_response.status, "201 Created")

        # verify response structure and content
        response_data = post_response.json
        self.assertEqual(response_data["abbreviation"], new_soda_params["abbreviation"])
        self.assertEqual(response_data["low_calorie"], bool(new_soda_params["low_calorie"]))
        self.assertEqual(response_data["name"], new_soda_params["name"])
        self.assertIn("id", response_data,
                      "Expected Soda object to have key 'id', but it was missing.")

        # Verify new id can be used to fetch the soda
        new_soda_id = post_response.json["id"]
        get_response = self.app.get(f'/api/sodas/{new_soda_id}/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(get_response.json, post_response.json)

    def test_create_soda_with_lowercase_abbreviation_transforms_to_uppercase(self) -> None:
        """HTTP request post request with lowercase abbreviation succeeds
        and stores abbreviation as uppercase"""

        lowercase_soda_params = {
            "abbreviation": "vz",
            "low_calorie": "True",
            "name": "Vanilla Coke Zero"
        }
        post_response = self.app.post_json('/api/sodas/', params=lowercase_soda_params)

        self.assertEqual(post_response.status, "201 Created")

        # verify post response content
        post_response_data = post_response.json
        self.assertEqual(post_response_data["abbreviation"], lowercase_soda_params["abbreviation"].upper())

        # verify that abbreviation was persisted as uppercase
        new_soda_id = post_response_data["id"]
        get_response = self.app.get(f'/api/sodas/{new_soda_id}/')
        self.assertEqual(get_response.json["abbreviation"], lowercase_soda_params["abbreviation"].upper())

    def test_create_soda_with_large_abbreviation_fails(self) -> None:
        """HTTP post request with abbreviation larger than two letters returns informative error"""

        duplicate_name_params = {
            "abbreviation": "SCH",
            "low_calorie": "True",
            "name": "Sour Cherry Coke"
        }
        post_response = self.app.post_json('/api/sodas/', params=duplicate_name_params, expect_errors=True)

        self.assertEqual(post_response.status, "400 Bad Request")
        self.assertIn("Ensure this field has no more than 2 characters.", post_response.json["abbreviation"])

    def test_create_soda_with_same_abbreviation_fails(self) -> None:
        """HTTP post request with duplicate abbreviation returns error"""

        duplicate_name_params = {
            "abbreviation": "CH",
            "low_calorie": "True",
            "name": "Sour Cherry Coke"
        }
        post_response = self.app.post_json('/api/sodas/', params=duplicate_name_params, expect_errors=True)

        self.assertEqual(post_response.status, "400 Bad Request")

    def test_create_soda_with_same_name_fails(self) -> None:
        """HTTP post request with duplicate name returns error"""

        duplicate_name_params = {
            "abbreviation": "CY",
            "low_calorie": "True",
            "name": "CherryCokeZero"
        }
        post_response = self.app.post_json('/api/sodas/', params=duplicate_name_params, expect_errors=True)

        self.assertEqual(post_response.status, "400 Bad Request")

    def test_delete_soda_succeeds(self) -> None:
        """HTTP delete request removes soda"""

        # Delete soda
        soda_ch_id = self.post_soda_ch.json["id"]
        delete_response = self.app.delete(f"/api/sodas/{soda_ch_id}/")
        self.assertEqual(delete_response.status, "204 No Content")

        # Verify soda is no longer available
        get_response = self.app.get(f"/api/sodas/{soda_ch_id}/", expect_errors=True)
        self.assertEqual(get_response.status, "404 Not Found")
