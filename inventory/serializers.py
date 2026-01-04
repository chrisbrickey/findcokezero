from decimal import Decimal
import requests
import urllib.parse

from django.conf import settings
from rest_framework import serializers

from .models import Retailer, Soda


class RetailerSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):

        saved_retailer = super(RetailerSerializer, self).create(validated_data)

        # TODO: Remove hard-coding to California state but remember that postcode can be null
        address_string = f"{validated_data['street_address']}, {validated_data['city']}, CA {validated_data.get('postcode', '')}"

        # Remove empty space at end of address_string for some cases (e.g., postcode is None)
        query_params = {'address': address_string.strip(), 'key': settings.GOOGLEMAPS_KEY}

        query_string = urllib.parse.urlencode(query_params)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{query_string}"
        json_response = requests.get(url).json()

        results = json_response["results"]
        if len(results) > 0:
            location = results[0]["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            # Convert to string first to avoid float precision issues
            # Model DecimalField has decimal_places=7 which matches Google Maps precision
            saved_retailer.latitude = Decimal(str(lat))
            saved_retailer.longitude = Decimal(str(lon))
            saved_retailer.save()

        return saved_retailer

    class Meta:
        model = Retailer
        fields = ('id', 'name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longitude',
                  'timestamp_last_updated', 'timestamp_created', 'sodas')
        # add conditionals here to restrict amount of data sent to frontend for query string filters


class SodaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Soda
        fields = ('id', 'name', 'abbreviation', 'low_calorie', 'url')
