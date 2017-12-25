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

    def test_view_all_retailers_by_postcode_and_soda(self):
        pass
        # "HTTP get request with postcode in params and soda types in data retrieves all retailers associated with that postcode and soda"
        # retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        # retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        # retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco", postcode="94107")
        # retailer4 = Retailer.objects.create(name="Retailer4", street_address="xyz", city="San Francisco", postcode="94108")
        #
        # sodaCZ = Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        # sodaCC = Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)
        # retailer1.sodas.add(sodaCZ)
        # retailer1.sodas.add(sodaCC)
        # retailer2.sodas.add(sodaCZ)
        # retailer3.sodas.add(sodaCZ)
        # retailer4.sodas.add(sodaCC)

        # params_CZ = {"abbreviation": "CZ"}
        # get_response_94107_CZ = self.app.get("/api/retailers/?postcode=94107", params={"abbreviation": "CZ"})
        # self.assertEqual(get_response_94107_CZ.status, "200 OK")
        # self.assertEqual(len(get_response_94107_CZ.json), 2)

        # self.assertEqual(post_response.json["name"], "McJSONs Store")
        # self.assertEqual(post_response.json["city"], "SF")
        # self.assertEqual(post_response.json["street_address"], "Bush St")
        # self.assertTrue(post_response.json.has_key("id"), "Expected Retailer object to have key 'id', but it was missing.")

        # get_response_94108_CC = self.app.get("/api/retailers/?postcode=%d" % 94108, params={"abbreviation": "CC"})
        # self.assertEqual(get_response_94108_CC.status, "200 OK")
        # self.assertEqual(len(get_response_94108_CC.json), 1)

        # self.assertEqual(post_response.json["name"], "McJSONs Store")
        # self.assertEqual(post_response.json["city"], "SF")
        # self.assertEqual(post_response.json["street_address"], "Bush St")
        # self.assertTrue(post_response.json.has_key("id"), "Expected Retailer object to have key 'id', but it was missing.")



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


class SodaTestCase(TestCase):
    def setUp(self):
        Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)

    def test_database_stores_sodas(self):
        """Soda types are stored in database and identified by abbreviation"""
        soda1 = Soda.objects.get(abbreviation="CZ")
        soda2 = Soda.objects.get(abbreviation="CC")
        self.assertEqual(soda1.name, "CherryCokeZero")
        self.assertEqual(soda2.name, "Coke Classic")
        self.assertEqual(soda1.low_calorie, True)
        self.assertEqual(soda2.low_calorie, False)

    def test_database_does_not_allow_duplicate_names(self):
        """For Sodas, duplicate names are not allowed"""
        with self.assertRaises(IntegrityError):
            Soda.objects.create(name="Coke Classic", abbreviation="CL", low_calorie=False)

    def test_database_does_not_allow_duplicate_abbreviations(self):
        """For Sodas, duplicate abbreviations are not allowed"""
        with self.assertRaises(IntegrityError):
            Soda.objects.create(name="CherryCokeZero2", abbreviation="CZ", low_calorie=False)

    def test_database_retrieves_soda_by_retailer(self):
        """Sodas are retreived in a group by retailer"""
        retailer = Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", postcode="94107")
        soda1 = Soda.objects.get(abbreviation="CZ")
        soda2 = Soda.objects.get(abbreviation="CC")
        retailer.sodas.add(soda1, soda2)
        self.assertEqual(retailer.sodas.get(pk=soda1.pk), soda1)
        self.assertEqual(retailer.sodas.get(pk=soda2.pk), soda2)


class SodaWebTestCase(WebTest):
    csrf_checks = False

    def setUp(self):
        Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)

    def test_show_sodas(self):
        # "For sodas, HTTP get request with no params retrieves all retailers in database"
        get_response = self.app.get('/api/sodas/')
        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)

    def test_view_all_sodas_by_retailer(self):
        # "HTTP get request with retailer ID and 'sodas' in params retrieves all sodas associated with that retailer"
        retailer = Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", postcode="94107")
        soda1 = Soda.objects.create(name="Diet Coke", abbreviation="DC", low_calorie=True)
        retailer.sodas.add(soda1)
        soda2 = Soda.objects.get(abbreviation="CC")
        retailer.sodas.add(soda2)

        retailer_id = retailer.id
        get_response = self.app.get("/api/retailers/%d/sodas/" % retailer_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json), 2)


    def test_create_soda(self):
        # """For sodas, HTTP request post request with valid data results in creation of object and response with all object data"""
        post_response = self.app.post_json('/api/sodas/',
                                           params={"abbreviation": "DC", "low_calorie": "True", "name": "Diet Coke"})
        self.assertEqual(post_response.status, "201 Created")

        self.assertEqual(post_response.json["abbreviation"], "DC")
        self.assertEqual(post_response.json["low_calorie"], True)
        self.assertEqual(post_response.json["name"], "Diet Coke")
        self.assertTrue(post_response.json.has_key("id"), "Expected Retailer object to have key 'id', but it was missing.")

        new_soda_id = post_response.json["id"]

        get_response = self.app.get('/api/sodas/%d/' % new_soda_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json.keys()), 4)
        self.assertEqual(get_response.json, post_response.json)
