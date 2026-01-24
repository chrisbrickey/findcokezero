from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from inventory.models import Retailer, Soda

class RetailerDBTestCase(TestCase):
    retailer1_data: dict[str, str | int] = {
            "name": "Shell",
            "street_address": "598 Bryant Street",
            "city": "San Francisco",
            "postcode": 94107,
        }
    retailer2_data: dict[str, str | int] = {
            "name": "Bush Market",
            "street_address": "820 Bush Street",
            "city": "San Francisco",
            "postcode": 94108,
        }
    soda1_data: dict[str, str | bool] = {
            "name": "Cherry Coke Zero",
            "abbreviation": "CZ",
            "low_calorie": True,
        }

    def setUp(self) -> None:
        # persist two retailers and one soda in test database
        Retailer.objects.create(**self.retailer1_data)
        Retailer.objects.create(**self.retailer2_data)
        Soda.objects.create(**self.soda1_data)

    def test_database_stores_retailers_and_retrieves_by_unique_field(self) -> None:
        """Retailers are stored in database and identified by unique field: address"""
        retailer1 = Retailer.objects.get(street_address=self.retailer1_data["street_address"])
        retailer2 = Retailer.objects.get(street_address=self.retailer2_data["street_address"])
        self.assertEqual(retailer1.name, self.retailer1_data["name"])
        self.assertEqual(retailer2.name, self.retailer2_data["name"])

    def test_database_does_not_allow_duplicate_names(self) -> None:
        """For Retailers, duplicate names are not allowed"""
        with self.assertRaises(IntegrityError):
            Retailer.objects.create(name=self.retailer2_data["name"], street_address="823 Bush Street",
                                    city="San Francisco", postcode=self.retailer2_data["postcode"])

    def test_database_does_not_allow_duplicate_addresses(self) -> None:
        """For Retailers, duplicate addresses are not allowed"""
        with self.assertRaises(IntegrityError):
            Retailer.objects.create(name="Bush Market2", street_address=self.retailer2_data["street_address"],
                                    city="San Francisco", postcode=self.retailer2_data["postcode"])

    def test_database_rejects_latitude_with_more_than_7_decimals(self) -> None:
        retailer_too_large_latitude = Retailer(
            **{**self.retailer1_data, "latitude": 37.12345678}
        )
        with self.assertRaises(ValidationError):
            retailer_too_large_latitude.full_clean()

    def test_database_rejects_longitude_with_more_than_7_decimals(self) -> None:
        retailer_too_large_longitude = Retailer(
            **{**self.retailer1_data, "longitude": -54.12345678}
        )
        with self.assertRaises(ValidationError):
            retailer_too_large_longitude.full_clean()

    def test_database_retrieves_retailer_by_postcode(self) -> None:
        """Retailers are retrieved by postcode"""

        # Add a third retailer with the same postcode as retailer1
        retailer1 = Retailer.objects.get(street_address=self.retailer1_data["street_address"])
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco",
                                            postcode=self.retailer1_data["postcode"])

        # Retrieve retailers by zipcode
        zip_code = self.retailer1_data["postcode"]
        results = Retailer.objects.filter(postcode=zip_code)

        # Assert that only retailers with matching postcode are returned
        self.assertEqual(results.count(), 2)
        self.assertTrue(all(r.postcode == zip_code for r in results))


    def test_database_retrieves_retailer_by_soda(self) -> None:
        """Retailers are retrieved in a group by soda"""

        # Associate soda with both retailers
        soda = Soda.objects.get(abbreviation=self.soda1_data["abbreviation"])
        retailer1 = Retailer.objects.get(street_address=self.retailer1_data["street_address"])
        retailer2 = Retailer.objects.get(street_address=self.retailer2_data["street_address"])
        retailer1.sodas.add(soda)
        retailer2.sodas.add(soda)

        # Assert that retailers can be retrieved via the soda's reverse relation
        self.assertIn(retailer1, soda.retailer_set.all())
        self.assertIn(retailer2, soda.retailer_set.all())


    def test_database_retrieves_retailers_by_postcode_and_soda(self) -> None:
        """Retailers are retrieved in a group by soda and postcode"""

        # Get existing retailers and sodas, create a third retailer with same postcode as retailer1
        retailer1 = Retailer.objects.get(street_address=self.retailer1_data["street_address"])
        retailer2 = Retailer.objects.get(street_address=self.retailer2_data["street_address"])
        retailer3 = Retailer.objects.create(name="Retailer3", street_address="abc", city="San Francisco",
                                            postcode=self.retailer1_data["postcode"])
        soda = Soda.objects.get(abbreviation=self.soda1_data["abbreviation"])

        # Associate soda with retailer1 and retailer2 (different postcodes)
        retailer1.sodas.add(soda)
        retailer2.sodas.add(soda)

        # Filter retailers by both postcode and soda
        zip_code = self.retailer1_data["postcode"]
        results = Retailer.objects.filter(postcode=zip_code, sodas=soda)

        # Assert that only the single retailer with matching postcode AND soda is returned
        self.assertEqual(results.count(), 1)
        self.assertIn(retailer1, results)
        self.assertTrue(all(r.postcode == zip_code for r in results))
        self.assertTrue(all(soda in r.sodas.all() for r in results))