# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.test import TestCase

from app1_findcokezero.models import Retailer

class RetailerTestCase(TestCase):
    def setUp(self):
        Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", state="CA", zip="94107", country="", longitude="", latitude="")
        Retailer.objects.create(name="Bush Market", street_address="820 Bush Street", city="San Francisco", state="CA", zip="94108", country="", longitude="", latitude="")

    def database_stores_retailers(self):
        """Retailers are stored and identified by address"""
        retailer1 = Retailer.objects.get(street_address="598 Bryant Street")
        retailer2 = Retailer.objects.get(street_address="820 Bush Street")
        self.assertEqual(retailer1.name, "Shell")
        self.assertEqual(retailer2.name, "Bush Market")
