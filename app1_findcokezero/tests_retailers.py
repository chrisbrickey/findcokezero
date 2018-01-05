# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.test import TestCase
from django_webtest import WebTest
from django.db import IntegrityError

from app1_findcokezero.models import Retailer, Soda

class RetailerTestCase(TestCase):
    def setUp(self):
        Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", postcode="94107")
        Retailer.objects.create(name="Bush Market", street_address="820 Bush Street", city="San Francisco", postcode="94108")

    def test_database_stores_retailers_and_retrieves_by_unique_field(self):
        """Retailers are stored in database and identified by unique field: address"""
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        self.assertEqual(retailer1.name, "Shell")
        self.assertEqual(retailer2.name, "Bush Market")

    def test_database_does_not_allow_duplicate_names(self):
        """For Retailers, duplicate names are not allowed"""
        with self.assertRaises(IntegrityError):
            Retailer.objects.create(name="Bush Market", street_address="823 Bush Street", city="San Francisco", postcode="94108")

    def test_database_does_not_allow_duplicate_addresses(self):
        """For Retailers, duplicate addresses are not allowed"""
        with self.assertRaises(IntegrityError):
            Retailer.objects.create(name="Bush Market2", street_address="820 Bush Street", city="San Francisco", postcode="94108")

    def test_database_retrieves_retailer_by_soda(self):
        """Retailers are retreived in a group by soda"""
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        soda = Soda.objects.create(name="Diet Coke", abbreviation="DC", low_calorie=True)

        retailer1.sodas.add(soda)
        retailer2.sodas.add(soda)
        self.assertEqual(soda.retailer_set.get(pk=retailer1.pk), retailer1)
        self.assertEqual(soda.retailer_set.get(pk=retailer2.pk), retailer2)

    def test_database_retrieves_retailer_by_postcode(self):
        """Retailers are retreived by postcode"""
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")

        results_94107 = Retailer.objects.filter(postcode="94107")
        array_94107 = []
        for retailer in results_94107:
            array_94107.append(str(retailer.name))
        array_94107.sort()

        results_94108 = Retailer.objects.filter(postcode="94108")
        array_94108 = []
        for retailer in results_94108:
            array_94108.append(str(retailer.name))
        array_94108.sort()

        self.assertEqual(len(results_94107), 2)
        self.assertEqual(len(results_94108), 1)
        self.assertEqual(array_94107, ['Retailer3', 'Shell'])
        self.assertEqual(array_94108, ['Bush Market'])

    def test_database_retrieves_retailers_by_postcode_and_soda(self):
        """Retailers are retreived in a group by soda and postcode"""
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")
        retailer4 = Retailer.objects.create(name="Retailer4", street_address="xyz", city="San Francisco", postcode="94108")

        sodaCZ = Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        sodaCC = Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)
        sodaDC = Soda.objects.create(name="Diet Coke", abbreviation="DC", low_calorie=True)

        retailer1.sodas.add(sodaCZ)
        retailer1.sodas.add(sodaCC)
        retailer2.sodas.add(sodaCZ)
        retailer3.sodas.add(sodaCZ)
        retailer4.sodas.add(sodaCC)

        array_94107_CZ = []
        results_94107 = Retailer.objects.filter(postcode="94107")
        for retailer in results_94107:
          if sodaCZ in retailer.sodas.all():
            array_94107_CZ.append(str(retailer.name))
        array_94107_CZ.sort()


        array_94108_CC = []
        results_94108 = Retailer.objects.filter(postcode="94108")
        for retailer in results_94108:
          if sodaCC in retailer.sodas.all():
            array_94108_CC.append(str(retailer.name))
        array_94108_CC.sort()

        array_94108_DC = []
        for retailer in results_94108:
          if sodaDC in retailer.sodas.all():
            array_94108_DC.append(str(retailer.name))


        self.assertEqual(len(array_94107_CZ), 2)
        self.assertEqual(len(array_94108_CC), 1)
        self.assertEqual(len(array_94108_DC), 0)

        self.assertEqual(array_94107_CZ, ['Retailer3', 'Shell'])
        self.assertEqual(array_94108_CC, ['Retailer4'])


class RetailerWebTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", postcode="94107")
        Retailer.objects.create(name="Bush Market", street_address="820 Bush Street", city="San Francisco", postcode="94108")

    def test_view_all_retailers(self):
        # "For retailers, HTTP get request with no params retrieves all retailers in database"
        get_response = self.app.get('/api/retailers/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_retailers_by_soda(self):
        # "HTTP get request with soda ID and 'retailers' in params retrieves all retailers associated with that soda"
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        soda = Soda.objects.create(name="Diet Coke", abbreviation="DC", low_calorie=True)
        retailer1.sodas.add(soda)
        retailer2.sodas.add(soda)

        soda_id = soda.id
        get_response = self.app.get("/api/sodas/%d/retailers/" % soda_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_retailers_by_postcode(self):
        # "HTTP get request with postcode and 'retailers' in params retrieves all retailers associated with that postcode"
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")

        get_response_94107 = self.app.get("/api/retailers/?postcode=%d" % 94107)
        self.assertEqual(get_response_94107.status, "200 OK")
        self.assertEqual(len(get_response_94107.json), 2)

        get_response_94108 = self.app.get("/api/retailers/?postcode=%d" % 94108)
        self.assertEqual(get_response_94108.status, "200 OK")
        self.assertEqual(len(get_response_94108.json), 1)

    def test_view_one_retailer_by_postcode_and_one_soda(self):
        # "HTTP get request with postcode and one soda type in query string retrieves one associated retailer"
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street") # 94107
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")

        sodaCZ = Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        sodaCC = Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)

        retailer1.sodas.add(sodaCZ)
        retailer3.sodas.add(sodaCC)

        get_response_94107_CZ = self.app.get("/api/retailers/?postcode=94107&sodas=CZ")
        self.assertEqual(get_response_94107_CZ.status, "200 OK")
        self.assertEqual(len(get_response_94107_CZ.json), 1)
        self.assertEqual(get_response_94107_CZ.json[0]["name"], "Shell")
        self.assertEqual(get_response_94107_CZ.json[0]["street_address"], "598 Bryant Street")
        self.assertEqual(get_response_94107_CZ.json[0]["city"], "San Francisco")
        self.assertEqual(get_response_94107_CZ.json[0]["postcode"], 94107)

    def test_view_all_retailers_by_postcode_and_one_soda(self):
        # "HTTP get request with postcode and one soda type in query string retrieves all associated retailers"
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street") # 94107
        retailer2 = Retailer.objects.get(street_address="820 Bush Street") #94108
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")
        retailer4 = Retailer.objects.create(name="Retailer4", street_address="xyz", city="San Francisco", postcode="94108")

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
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street") # 94107
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")
        retailer4 = Retailer.objects.create(name="Retailer4", street_address="opq", city="San Francisco", postcode="94108")
        retailer5 = Retailer.objects.create(name="Retailer5", street_address="xyz", city="San Francisco", postcode="94107")

        sodaCZ = Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
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

    def test_create_retailer(self):
        # "For retailers, HTTP request post request with valid data results in creation of object and response with all object data"
        post_response = self.app.post_json('/api/retailers/',
                                           params={"city": "SF", "name": "McJSONs Store", "street_address": "Bush St"})
        self.assertEqual(post_response.status, "201 Created")

        self.assertEqual(post_response.json["name"], "McJSONs Store")
        self.assertEqual(post_response.json["city"], "SF")
        self.assertEqual(post_response.json["street_address"], "Bush St")
        self.assertTrue(post_response.json.has_key("id"), "Expected Retailer object to have key 'id', but it was missing.")

        new_retailer_id = post_response.json["id"]

        get_response = self.app.get('/api/retailers/%d/' % new_retailer_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json.keys()), 11)
        self.assertEqual(get_response.json, post_response.json)
