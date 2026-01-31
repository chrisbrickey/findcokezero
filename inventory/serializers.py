import logging

from rest_framework import serializers
from typing import Any
from .exceptions import NonNumericPostcodeError
from .models import Retailer, Soda
from .services.geocoding import GeocodingService, GeocodingResult
from .services.exceptions import GeocodingError

logger = logging.getLogger(__name__)

class RetailerSerializer(serializers.HyperlinkedModelSerializer[Retailer]):
    class Meta:
        model = Retailer
        fields = ('id', 'name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longitude',
                  'timestamp_last_updated', 'timestamp_created', 'sodas')

    def create(self, validated_data: dict[str, Any]) -> Retailer:
        saved_retailer = super(RetailerSerializer, self).create(validated_data)

        geocoding_result = self._fetch_geocoding(validated_data, saved_retailer.name)
        if geocoding_result is not None:
            self._apply_geocoding(saved_retailer, geocoding_result, validated_data)

        saved_retailer.save()
        return saved_retailer

    def _fetch_geocoding(
        self, validated_data: dict[str, Any], retailer_name: str
    ) -> GeocodingResult | None:
        """Fetch geocoding data for the address. Returns None on failure."""

        # This dependency is not injected due to reliance on HyperlinkedModelSerializer
        geocoding_service = GeocodingService()

        try:
            return geocoding_service.geocode_address(
                street_address=validated_data["street_address"],
                city=validated_data["city"],
                postcode=validated_data.get("postcode")
            )

        except GeocodingError as e:
            logger.warning(
                "Geocoding failed for retailer '%s': %s. Continuing without coordinates.",
                retailer_name,
                str(e),
            )
            return None

    def _apply_geocoding(
        self,
        retailer: Retailer,
        geocoding_result: GeocodingResult,
        validated_data: dict[str, Any],
    ) -> None:
        """Apply geocoding results to retailer object."""

        retailer.latitude = geocoding_result.latitude
        retailer.longitude = geocoding_result.longitude

        if not validated_data.get("postcode") and geocoding_result.postcode is not None:
            try:
                numerical_postcode = int(geocoding_result.postcode)
            except ValueError:
                raise NonNumericPostcodeError
            retailer.postcode = numerical_postcode


class SodaSerializer(serializers.HyperlinkedModelSerializer[Soda]):
    class Meta:
        model = Soda
        fields = ('id', 'name', 'abbreviation', 'low_calorie', 'url')

    def validate_abbreviation(self, value: str) -> str:
        return value.upper()

