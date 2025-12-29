from decimal import Decimal

# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.db import IntegrityError
from django.test import TestCase
from django_webtest import WebTest

from inventory.models import Retailer, Soda


class RetailerDBTestCase(TestCase):
    def setUp(self):
        Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco",
                                postcode="94107")
        Retailer.objects.create(name="Bush Market", street_address="820 Bush Street", city="San Francisco",
                                postcode="94108")

    def test_database_stores_retailers_and_retrieves_by_unique_field(self):
        """Retailers are stored in database and identified by unique field: address"""
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
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco",
                                            postcode="94107")

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

