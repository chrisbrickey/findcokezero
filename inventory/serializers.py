from decimal import Decimal
from typing import Any
import requests
import urllib.parse

from django.conf import settings
from rest_framework import serializers

from .models import Retailer, Soda


class RetailerSerializer(serializers.HyperlinkedModelSerializer[Retailer]):

    def create(self, validated_data: dict[str, Any]) -> Retailer:
        saved_retailer = super(RetailerSerializer, self).create(validated_data)

        # construct address string; postcode can be empty
        postcode = validated_data.get('postcode', '')
        postcode_suffix = f", {postcode}" if postcode else ""
        address_string = f"{validated_data['street_address']}, {validated_data['city']}{postcode_suffix}"

        query_params = {'address': address_string, 'key': settings.GOOGLEMAPS_KEY}
        query_string = urllib.parse.urlencode(query_params)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{query_string}"
        json_response = requests.get(url).json()

        # populate latitude and longitude (and optionally postcode) from google maps response
        results = json_response["results"]
        if results:
            result = results[0]

            # Extract latitude and longitude (always present per api contract)
            location = result["geometry"]["location"]
            saved_retailer.latitude = Decimal(location["lat"])
            saved_retailer.longitude = Decimal(location["lng"])

            # Auto-populate postcode only if not already provided by user
            if not validated_data.get('postcode'):
                api_postcode = self._extract_postcode_from_address_components(
                    result.get("address_components", [])
                )
                if api_postcode is not None:
                    saved_retailer.postcode = api_postcode

            saved_retailer.save()

        return saved_retailer

    def _extract_postcode_from_address_components(
        self, address_components: list[dict[str, Any]]
    ) -> int | None:
        """
        Extract postcode from Google Maps API response.
        Returns int if found and numeric, None otherwise.
        """
        for component in address_components:
            if "postal_code" in component.get("types", []):
                try:
                    return int(component.get("short_name", ""))
                except ValueError:
                    # Non-numeric postal code (e.g., UK, Canada) are not yet compatible with this app
                    return None
        return None

    class Meta:
        model = Retailer
        fields = ('id', 'name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longitude',
                  'timestamp_last_updated', 'timestamp_created', 'sodas')
        # add conditionals here to restrict amount of data sent to frontend for query string filters


class SodaSerializer(serializers.HyperlinkedModelSerializer[Soda]):
    class Meta:
        model = Soda
        fields = ('id', 'name', 'abbreviation', 'low_calorie', 'url')
