import logging
from typing import Any

from rest_framework import serializers

from .models import Retailer, Soda
from .services import (
    GeocodingError,
    GeocodingService,
)

logger = logging.getLogger(__name__)


class RetailerSerializer(serializers.HyperlinkedModelSerializer[Retailer]):

    def __init__(
        self,
        *args: Any,
        geocoding_service: GeocodingService | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the serializer with optional dependency injection.

        Args:
            geocoding_service: Optional GeocodingService instance for testing.
        """
        super().__init__(*args, **kwargs)
        self._geocoding_service = geocoding_service

    @property
    def geocoding_service(self) -> GeocodingService:
        """Lazy-load the geocoding service."""
        if self._geocoding_service is None:
            self._geocoding_service = GeocodingService()
        return self._geocoding_service

    def create(self, validated_data: dict[str, Any]) -> Retailer:
        saved_retailer = super(RetailerSerializer, self).create(validated_data)

        try:
            result = self.geocoding_service.geocode_address(
                street_address=validated_data["street_address"],
                city=validated_data["city"],
                postcode=validated_data.get("postcode"),
            )

            saved_retailer.latitude = result.latitude
            saved_retailer.longitude = result.longitude

            # Auto-populate postcode only if not already provided by user
            if not validated_data.get("postcode") and result.postcode is not None:
                saved_retailer.postcode = result.postcode

            saved_retailer.save()

        except GeocodingError as e:
            logger.warning(
                "Geocoding failed for retailer '%s': %s. Continuing without coordinates.",
                saved_retailer.name,
                str(e),
            )

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
