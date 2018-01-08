# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal

# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.test import TestCase
from django_webtest import WebTest
from django.db import IntegrityError

from app1_findcokezero.models import Retailer, Soda


# web tests should not use objects created and stored in database; that is testing behavior of both the http application and the database (too much)
class RetailerWebTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "Shell",
                                   "postcode": "94107",
                                   "street_address": "598 Bryant Street"})

        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "Bush Market",
                                   "postcode": "94108",
                                   "street_address": "820 Bush Street"})

    def test_view_all_retailers(self):
        # "For retailers, HTTP get request with no params retrieves all retailers in database"

        get_response = self.app.get('/api/retailers/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_retailers_by_soda(self):
        # "HTTP get request with soda ID and 'retailers' in params retrieves all retailers associated with that soda"

        post_soda_response = self.app.post_json('/api/sodas/',
                                                params={"abbreviation": "DC",
                                                        "low_calorie": "True",
                                                        "name": "Diet Coke"})
        new_soda_url = post_soda_response.json["url"]
        new_soda_id = post_soda_response.json["id"]

        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "CVS",
                                   "postcode": "94109",
                                   "sodas": [new_soda_url],
                                   "street_address": "225 Bush Street"})

        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "Le Beau",
                                   "postcode": "94109",
                                   "sodas": [new_soda_url],
                                   "street_address": "1415 Clay Street"})

        get_response = self.app.get("/api/sodas/%d/retailers/" % new_soda_id)
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_retailers_by_postcode(self):
        # "HTTP get request with postcode and 'retailers' in params retrieves all retailers associated with that postcode"

        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "Walgreens",
                                   "postcode": "94107",
                                   "street_address": "670 4th Street"})

        get_response_94107 = self.app.get("/api/retailers/?postcode=%d" % 94107)
        self.assertEqual(get_response_94107.status, "200 OK")
        self.assertEqual(len(get_response_94107.json), 2)

        get_response_94108 = self.app.get("/api/retailers/?postcode=%d" % 94108)
        self.assertEqual(get_response_94108.status, "200 OK")
        self.assertEqual(len(get_response_94108.json), 1)

    def test_view_one_retailer_by_postcode_and_one_soda(self):
        # "HTTP get request with postcode and one soda type in query string retrieves one associated retailer"

        post_soda_response_CH = self.app.post_json('/api/sodas/',
                                                   params={"abbreviation": "CH",
                                                           "low_calorie": "True",
                                                           "name": "CherryCokeZero"})
        CH_url = post_soda_response_CH.json["url"]

        post_soda_response_CC = self.app.post_json('/api/sodas/',
                                                   params={"abbreviation": "CC",
                                                           "low_calorie": "False",
                                                           "name": "Coke Classic"})
        CC_url = post_soda_response_CC.json["url"]

        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "CVS",
                                   "postcode": "94109",
                                   "sodas": [CH_url],
                                   "street_address": "225 Bush Street"})

        self.app.post_json('/api/retailers/',
                           params={"city": "San Francisco",
                                   "name": "Le Beau",
                                   "postcode": "94109",
                                   "sodas": [CC_url],
                                   "street_address": "1415 Clay Street"})

        get_response_94109_CH = self.app.get("/api/retailers/?postcode=94109&sodas=CH")
        self.assertEqual(get_response_94109_CH.status, "200 OK")
        self.assertEqual(len(get_response_94109_CH.json), 1)
        self.assertEqual(get_response_94109_CH.json[0]["name"], "CVS")
        self.assertEqual(get_response_94109_CH.json[0]["street_address"], "225 Bush Street")
        self.assertEqual(get_response_94109_CH.json[0]["city"], "San Francisco")
        self.assertEqual(get_response_94109_CH.json[0]["postcode"], 94109)

    def test_view_all_retailers_by_postcode_and_one_soda(self):
        # "HTTP get request with postcode and one soda type in query string retrieves all associated retailers"

        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")  # 94107
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")  # 94108
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco",
                                            postcode="94107")
        retailer4 = Retailer.objects.create(name="Retailer4", street_address="xyz", city="San Francisco",
                                            postcode="94108")

        sodaCZ = Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        sodaCC = Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)
        sodaDC = Soda.objects.create(name="Diet Coke", abbreviation="DC", low_calorie=True)

        retailer1.sodas.add(sodaCZ)
        retailer1.sodas.add(sodaCC)
        retailer2.sodas.add(sodaCZ)
        retailer3.sodas.add(sodaCZ)
        retailer4.sodas.add(sodaCC)

        get_response_94107_CZ = self.app.get("/api/retailers/?postcode=94107&sodas=CZ")
        self.assertEqual(get_response_94107_CZ.status, "200 OK")
        self.assertEqual(len(get_response_94107_CZ.json), 2)

        get_response_94108_CC = self.app.get("/api/retailers/?postcode=94108&sodas=CC")
        self.assertEqual(get_response_94108_CC.status, "200 OK")
        self.assertEqual(len(get_response_94108_CC.json), 1)
        self.assertEqual(get_response_94108_CC.json[0]["name"], "Retailer4")
        self.assertEqual(get_response_94108_CC.json[0]["street_address"], "xyz")
        self.assertEqual(get_response_94108_CC.json[0]["city"], "San Francisco")
        self.assertEqual(get_response_94108_CC.json[0]["postcode"], 94108)

        get_response_94108_DC = self.app.get("/api/retailers/?postcode=94108&sodas=DC")
        self.assertEqual(get_response_94108_DC.status, "200 OK")
        self.assertEqual(len(get_response_94108_DC.json), 0)

    def test_view_all_retailers_by_postcode_and_multiple_sodas(self):
        # "HTTP get request with postcode and multiple soda types in params retrieves all associated retailers"

        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")  # 94107
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco",
                                            postcode="94107")
        retailer4 = Retailer.objects.create(name="Retailer4", street_address="opq", city="San Francisco",
                                            postcode="94108")
        retailer5 = Retailer.objects.create(name="Retailer5", street_address="xyz", city="San Francisco",
                                            postcode="94107")

        cherry_coke_dict = {"name": "CherryCokeZero", "abbreviation": "CZ", "low_calorie": True}
        sodaCZ = Soda.objects.create(**cherry_coke_dict)
        sodaCC = Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)
        sodaDC = Soda.objects.create(name="Diet Coke", abbreviation="DC", low_calorie=True)

        retailer1.sodas.add(sodaCZ)
        retailer1.sodas.add(sodaDC)
        retailer1.sodas.add(sodaCC)
        retailer3.sodas.add(sodaCZ)
        retailer3.sodas.add(sodaCC)
        retailer4.sodas.add(sodaCZ)
        retailer5.sodas.add(sodaCZ)
        retailer5.sodas.add(sodaDC)

        get_response_94107_CZ_DC = self.app.get("/api/retailers/?postcode=94107&sodas=CZ,DC")
        self.assertEqual(get_response_94107_CZ_DC.status, "200 OK")
        self.assertEqual(len(get_response_94107_CZ_DC.json), 2)

        result_names = [str(get_response_94107_CZ_DC.json[0]["name"]), str(get_response_94107_CZ_DC.json[1]["name"])]
        self.assertTrue("Shell" in result_names)
        self.assertTrue("Retailer5" in result_names)
        self.assertEqual(get_response_94107_CZ_DC.json[0]["postcode"], 94107)

    def test_create_retailer_without_sodas(self):
        # "For retailers, HTTP request post request with required data results in creation of object and response with all object data"

        post_response = self.app.post_json('/api/retailers/',
                                           params={"city": "SF",
                                                   "name": "McJSONs Store",
                                                   "street_address": "Bush St"})
        self.assertEqual(post_response.status, "201 Created")

        self.assertEqual(post_response.json["name"], "McJSONs Store")
        self.assertEqual(post_response.json["city"], "SF")
        self.assertEqual(post_response.json["street_address"], "Bush St")
        self.assertTrue(post_response.json.has_key("id"),
                        "Expected Retailer object to have key 'id', but it was missing.")

        new_retailer_id = post_response.json["id"]

        get_response = self.app.get('/api/retailers/%d/' % new_retailer_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json.keys()), 11)

        get_latitude = Decimal(get_response.json["latitude"])
        get_longitude = Decimal(get_response.json["longitude"])
        post_latitude = Decimal(post_response.json["latitude"])
        post_longitude = Decimal(post_response.json["longitude"])

        self.assertAlmostEqual(get_latitude, post_latitude, places=10)
        self.assertAlmostEqual(get_longitude, post_longitude, places=10)

        get_dictionary = get_response.json
        post_dictionary = post_response.json
        del get_dictionary["latitude"]
        del get_dictionary["longitude"]
        del post_dictionary["latitude"]
        del post_dictionary["longitude"]

        self.assertEqual(get_dictionary, post_dictionary)

    def test_create_retailer_with_sodas(self):
        # "For retailers, HTTP request post request with soda data results in creation of object and response with all object data"

        post_soda_response = self.app.post_json('/api/sodas/',
                                                params={"name": "FavoriteSoda", "abbreviation": "FS"})
        new_soda_url = post_soda_response.json["url"]

        post_retailer_response = self.app.post_json('/api/retailers/',
                                                    params={"city": "SF",
                                                            "name": "McJSONs Store",
                                                            "street_address": "Bush St",
                                                            "sodas": [new_soda_url]})
        new_retailer_id = post_retailer_response.json["id"]

        get_retailer_response = self.app.get('/api/retailers/%d/' % new_retailer_id)
        self.assertEqual(get_retailer_response.status, "200 OK")
        sodas_list = get_retailer_response.json["sodas"]
        self.assertEqual(len(sodas_list), 1)

    def test_creating_retailer_populates_latlong(self):
        # "For retailers, HTTP request post request populates latitude and longitude for user"

        post_response = self.app.post_json('/api/retailers/',
                                           params={"city": "SF",
                                                   "name": "McJSONs Store",
                                                   "street_address": "Bush St",
                                                   "sodas": []})

        new_retailer_id = post_response.json["id"]

        get_response = self.app.get('/api/retailers/%d/' % new_retailer_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(get_response.json["latitude"], "37.78839980000000053906")
        self.assertEqual(get_response.json["longitude"], "-122.42269170000000144682")

    def test_update_retailer_with_sodas(self):
        # "For retailers, HTTP request put request with new data (including soda) updates retailer"

        post_soda_response_DC = self.app.post_json('/api/sodas/',
                                                   params={"abbreviation": "DC",
                                                           "low_calorie": "True",
                                                           "name": "Diet Coke"})
        soda_url_DC = post_soda_response_DC.json["url"]

        post_retailer_response_McJSON = self.app.post_json('/api/retailers/',
                                                           params={"city": "SF",
                                                                   "name": "McJSONs Store",
                                                                   "street_address": "Bush St"})

        self.assertEqual(post_retailer_response_McJSON.json["name"], "McJSONs Store")
        sodas_list_before = post_retailer_response_McJSON.json["sodas"]
        self.assertEqual(len(sodas_list_before), 0)

        retailer_id_McJSON = post_retailer_response_McJSON.json["id"]
        city_McJSON = post_retailer_response_McJSON.json["city"]
        address_McJSON = post_retailer_response_McJSON.json["street_address"]

        put_retailer_response_McJSON = self.app.put_json('/api/retailers/%d/' % retailer_id_McJSON,
                                                         params={"name": "McJSON2",
                                                                 "city": city_McJSON,
                                                                 "sodas": [soda_url_DC],
                                                                 "street_address": address_McJSON})

        self.assertEqual(put_retailer_response_McJSON.json["name"], "McJSON2")

        sodas_list_after = put_retailer_response_McJSON.json["sodas"]
        self.assertEqual(len(sodas_list_after), 1)
