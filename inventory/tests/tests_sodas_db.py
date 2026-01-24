# using test.TestCase instead of unittest.TestCase to make sure tests run within the suite - not just in isolation
from django.db import IntegrityError
from django.test import TestCase

from inventory.models import Retailer, Soda


class SodaDBTestCase(TestCase):
    def setUp(self) -> None:
        Soda.objects.create(name="CherryCokeZero", abbreviation="CZ", low_calorie=True)
        Soda.objects.create(name="Coke Classic", abbreviation="CC", low_calorie=False)

    def test_database_stores_sodas(self) -> None:
        """Soda types are stored in database and identified by abbreviation"""
        soda1 = Soda.objects.get(abbreviation="CZ")
        soda2 = Soda.objects.get(abbreviation="CC")
        self.assertEqual(soda1.name, "CherryCokeZero")
        self.assertEqual(soda2.name, "Coke Classic")
        self.assertEqual(soda1.low_calorie, True)
        self.assertEqual(soda2.low_calorie, False)

    def test_database_does_not_allow_duplicate_names(self) -> None:
        """For Sodas, duplicate names are not allowed"""
        with self.assertRaises(IntegrityError):
            Soda.objects.create(name="Coke Classic", abbreviation="CL", low_calorie=False)

    def test_database_does_not_allow_duplicate_abbreviations(self) -> None:
        """For Sodas, duplicate abbreviations are not allowed"""
        with self.assertRaises(IntegrityError):
            Soda.objects.create(name="CherryCokeZero2", abbreviation="CZ", low_calorie=False)

    def test_database_retrieves_soda_by_retailer(self) -> None:
        """Sodas are retreived in a group by retailer"""
        retailer = Retailer.objects.create(name="Shell", street_address="598 Bryant Street", city="San Francisco", postcode="94107")
        soda1 = Soda.objects.get(abbreviation="CZ")
        soda2 = Soda.objects.get(abbreviation="CC")
        retailer.sodas.add(soda1, soda2)
        self.assertEqual(retailer.sodas.get(pk=soda1.pk), soda1)
        self.assertEqual(retailer.sodas.get(pk=soda2.pk), soda2)
