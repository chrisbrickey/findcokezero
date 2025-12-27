# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.test import TestCase
from django_webtest import WebTest
from django.db import IntegrityError

from app1_findcokezero.models import Retailer, Soda


# web tests should not use objects created and stored in database; that is testing behavior of both the http application and the database (too much)
class SodaWebTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        self.app.post_json('/api/sodas/',
                           params={"abbreviation": "CH",
                                   "low_calorie": "True",
                                   "name": "CherryCokeZero"})
        self.app.post_json('/api/sodas/',
                           params={"abbreviation": "CC",
                                   "low_calorie": "False",
                                   "name": "Coke Classic"})

    def test_show_sodas(self):
        # "For sodas, HTTP get request with no params retrieves all retailers"
        get_response = self.app.get('/api/sodas/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_sodas_by_retailer(self):
        # "HTTP get request with retailer ID and 'sodas' in params retrieves all sodas associated with that retailer"
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

        get_response = self.app.get("/api/retailers/%d/sodas/" % retailer_id_Shell)
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_create_soda(self):
        # "For sodas, HTTP request post request with valid data results in creation of object and response with all object data"
        post_response = self.app.post_json('/api/sodas/',
                                           params={"abbreviation": "DC",
                                                   "low_calorie": "True",
                                                   "name": "Diet Coke"})
        self.assertEqual(post_response.status, "201 Created")

        self.assertEqual(post_response.json["abbreviation"], "DC")
        self.assertEqual(post_response.json["low_calorie"], True)
        self.assertEqual(post_response.json["name"], "Diet Coke")
        self.assertIn("id", post_response.json,
                      "Expected Retailer object to have key 'id', but it was missing.")

        new_soda_id = post_response.json["id"]

        get_response = self.app.get('/api/sodas/%d/' % new_soda_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json.keys()), 5)
        self.assertEqual(get_response.json, post_response.json)
