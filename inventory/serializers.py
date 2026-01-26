import logging

from rest_framework import serializers
from typing import Any
from .exceptions import NonNumericPostcodeError
from .models import Retailer, Soda
from .services.geocoding import GeocodingService
from .services.exceptions import GeocodingError

logger = logging.getLogger(__name__)

class RetailerSerializer(serializers.HyperlinkedModelSerializer[Retailer]):

    def create(self, validated_data: dict[str, Any]) -> Retailer:
        saved_retailer = super(RetailerSerializer, self).create(validated_data)

        # This dependency is not injected due to reliance on HyperlinkedModelSerializer
        # from rest framework libary
        geocoding_service = GeocodingService()
        geocoding_result = None

        try:
            geocoding_result = geocoding_service.geocode_address(
                street_address=validated_data["street_address"],
                city=validated_data["city"],
                postcode=validated_data.get("postcode")
            )
        except GeocodingError as e:
            logger.warning(
                "Geocoding failed for retailer '%s': %s. Continuing without coordinates.",
                saved_retailer.name,
                str(e),
            )

        if geocoding_result is not None:
            # Populate latitude and longitude from geocoding service
            saved_retailer.latitude = geocoding_result.latitude
            saved_retailer.longitude = geocoding_result.longitude

            # Only populate postcode from geocoding service if not provided by user
            if not validated_data.get("postcode") and geocoding_result.postcode is not None:
                numerical_postcode = None

                try:
                    numerical_postcode = int(geocoding_result.postcode)
                except ValueError:
                    raise NonNumericPostcodeError
                saved_retailer.postcode = numerical_postcode

        saved_retailer.save()
        return saved_retailer

    class Meta:
        model = Retailer
        fields = ('id', 'name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longitude',
                  'timestamp_last_updated', 'timestamp_created', 'sodas')
        # add conditionals here to restrict amount of data sent to frontend for query string filters


class SodaSerializer(serializers.HyperlinkedModelSerializer[Soda]):
    class Meta:
        model = Soda
        fields = ('id', 'name', 'abbreviation', 'low_calorie', 'url')
