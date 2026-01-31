"""Type definitions for test fixtures."""

from decimal import Decimal
from typing import TypedDict


class RetailerBaseData(TypedDict):
    """Base fields shared by all Retailer test fixtures."""

    name: str
    street_address: str
    city: str


class RetailerTestPersistenceData(RetailerBaseData):
    """Test fixture for Retailer (DB layer)."""

    postcode: int


class RetailerTestFormDataWithGeocoding(RetailerBaseData):
    """Test fixture for Retailer with geocoding fields."""

    postcode: str
    latitude: Decimal
    longitude: Decimal


class SodaBaseData(TypedDict):
    """Base fields shared by all Soda test fixtures."""

    name: str
    abbreviation: str


class SodaTestPersistenceData(SodaBaseData):
    """Test fixture for Soda (DB layer)."""

    low_calorie: bool


class SodaTestFormData(SodaBaseData):
    """Test fixture for Soda form submission (web layer)."""

    low_calorie: str  # "True"/"False" from form
