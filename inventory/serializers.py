from decimal import Decimal
import requests
import urllib.parse

from django.conf import settings
from rest_framework import serializers

from .models import Retailer, Soda


class RetailerSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        saved_retailer = super(RetailerSerializer, self).create(validated_data)

        # construct address string; postcode can be empty
        postcode = validated_data.get('postcode', '')
        postcode_suffix = f", {postcode}" if postcode else ""
        address_string = f"{validated_data['street_address']}, {validated_data['city']}{postcode_suffix}"

        query_params = {'address': address_string, 'key': settings.GOOGLEMAPS_KEY}
        query_string = urllib.parse.urlencode(query_params)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{query_string}"
        json_response = requests.get(url).json()

        # populate latitude and longitude from google maps response
        results = json_response["results"]
        if len(results) > 0:
            location = results[0]["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            saved_retailer.latitude = Decimal(lat)
            saved_retailer.longitude = Decimal(lon)
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
