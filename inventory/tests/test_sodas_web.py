# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django_webtest import WebTest

class SodaWebTestCase(WebTest):
    csrf_checks = False

    def setUp(self) -> None:
        self.app.post_json('/api/sodas/',
                           params={"abbreviation": "CH",
                                   "low_calorie": "True",
                                   "name": "CherryCokeZero"})
        self.app.post_json('/api/sodas/',
                           params={"abbreviation": "CC",
                                   "low_calorie": "False",
                                   "name": "Coke Classic"})

    def test_show_sodas(self) -> None:
        """HTTP get request with no params retrieves all retailers"""

        get_response = self.app.get('/api/sodas/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_sodas_by_retailer(self) -> None:
        """HTTP get request with retailer ID and 'sodas' in params retrieves all sodas associated with that retailer"""

        post_soda_response_DC = self.app.post_json('/api/sodas/',
                                                   params={"abbreviation": "DC",
                                                           "low_calorie": "True",
                                                           "name": "Diet Coke"})
        soda_url_DC = post_soda_response_DC.json["url"]

        post_soda_response_CF = self.app.post_json('/api/sodas/',
                                                   params={"abbreviation": "CF",
                                                           "low_calorie": "True",
                                                           "name": "Caffeine Free Diet Coke"})
        soda_url_CF = post_soda_response_CF.json["url"]

        post_retailer_response_Shell = self.app.post_json('/api/retailers/',
                                                          params={"city": "San Francisco",
                                                                  "name": "Shell",
                                                                  "postcode": "94107",
                                                                  "street_address": "598 Bryant Street",
                                                                  "sodas": [soda_url_DC, soda_url_CF]})
        retailer_id_Shell = post_retailer_response_Shell.json["id"]

        get_response = self.app.get(f"/api/retailers/{retailer_id_Shell}/sodas/")
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

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
                      "Expected Retailer object to have key 'id', but it was missing.")

        # Verify new id can be used to fetch the soda
        new_soda_id = post_response.json["id"]
        get_response = self.app.get(f'/api/sodas/{new_soda_id}/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(get_response.json, post_response.json)

    def test_create_soda_with_lowercase_abbreviation_succeeds(self) -> None:
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
