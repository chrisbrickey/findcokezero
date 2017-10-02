# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.test import TestCase
from django_webtest import WebTest

from app1_findcokezero.models import Retailer

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

class RetailerWebTestCase(WebTest):
    csrf_checks = False
    def test_create_retailer(self):
        response = self.app.post_json('/retailers/',
                                      headers={
                                        "accept": str('application/json'),
                                        "X-Requested-With": str('XMLHttpRequest'),
                                      },
                                      params={"city": "SF", "name": "McJSONs Store", "street_address": "Bush St"})
        self.assertEqual(response.status, "201 Created")

        self.assertEqual(response.json["name"], "McJSONs Store")
        self.assertEqual(response.json["city"], "SF")
        self.assertEqual(response.json["street_address"], "Bush St")
        self.assertTrue(response.json.has_key("id"), "Expected Retailer object to have key 'id', but it was missing.")
