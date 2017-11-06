# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.test import TestCase
from django_webtest import WebTest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from app1_findcokezero.models import Retailer, Soda

class RetailerTestCase(TestCase):
    def setUp(self):
        Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", postcode="94107")
        Retailer.objects.create(name="Bush Market", street_address="820 Bush Street", city="San Francisco", postcode="94108")

    def test_database_stores_retailers(self):
        """Retailers are stored in database and identified by address"""
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        self.assertEqual(retailer1.name, "Shell")
        self.assertEqual(retailer2.name, "Bush Market")

    def test_database_does_not_allow_duplicate_names(self):
        """For Retailers, duplicate names are not allowed"""
        with self.assertRaises(IntegrityError):
            Retailer.objects.create(name="Bush Market", street_address="823 Bush Street", city="San Francisco",
                                postcode="94108")

    def test_database_does_not_allow_duplicate_addresses(self):
        """For Retailers, duplicate addresses are not allowed"""
        with self.assertRaises(IntegrityError):
            Retailer.objects.create(name="Bush Market2", street_address="820 Bush Street", city="San Francisco",
                                    postcode="94108")

    # def test_api_retrieves_retailer_group_by_zipcode(self):
    #     """Retailers are retreived in a group by zipcode"""


class RetailerWebTestCase(WebTest):
    csrf_checks = False
    def test_create_retailer(self):
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
        self.assertEqual(len(get_response.json.keys()), 10)
        self.assertEqual(get_response.json, post_response.json)


class SodaTestCase(TestCase):
    def setUp(self):
        Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)

    def test_database_stores_retailers(self):
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

    # def test_database_does_not_allow_duplicate_abbreviations(self):
    #     """For Sodas, duplicate abbreviations are not allowed"""
    #     with self.assertRaises(IntegrityError):
    #         Retailer.objects.create(name="CherryCokeZero2", abbreviation="CZ", low_calorie=False)


    # def test_api_retrieves_soda_by_retailer(self):
    #     """Sodas are retreived in a group by retailer"""

    # def test_api_retrieves_for_soda_by_zipcode(self):
    #     """Sodas are retreived in a group by zipcode"""


class SodaWebTestCase(WebTest):
    csrf_checks = False
    def test_create_soda(self):
        post_response = self.app.post_json('/api/sodas/',
                                           params={"abbreviation": "CZ", "low_calorie": "True", "name": "Cherry Coke Zero"})
        self.assertEqual(post_response.status, "201 Created")

        self.assertEqual(post_response.json["abbreviation"], "CZ")
        self.assertEqual(post_response.json["low_calorie"], True)
        self.assertEqual(post_response.json["name"], "Cherry Coke Zero")
        self.assertTrue(post_response.json.has_key("id"), "Expected Retailer object to have key 'id', but it was missing.")

        new_soda_id = post_response.json["id"]

        get_response = self.app.get('/api/sodas/%d/' % new_soda_id)

        self.assertEqual(get_response.status, "200 OK")
        self.assertEqual(len(get_response.json.keys()), 4)
        self.assertEqual(get_response.json, post_response.json)