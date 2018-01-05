from rest_framework import serializers
from .models import Retailer, Soda
from django.conf import settings

import urllib, requests


class RetailerSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        address_string = "%s, %s, CA %s" % (validated_data["street_address"],
                                            validated_data["city"],
                                            validated_data.get("postcode", "")) # postcode can be null so use 'get' method with default value

        query_params = {'address': address_string.strip(), 'key': settings.GOOGLEMAPS_KEY} #remove empty space at end of address if postcode is None
        query_string = urllib.urlencode(query_params)
        url = "https://maps.googleapis.com/maps/api/geocode/json?%s" % (query_string,)
        json_response = requests.get(url).json()

        results = json_response["results"]
        if len(results) > 0:
            location = results[0]["geometry"]["location"]
            lat = location["lat"]
            lon = location["lng"]
            validated_data["latitude"] = lat
            validated_data["longitude"] = lon
        return Retailer.objects.create(**validated_data)

    class Meta:
        model = Retailer
        fields = ('id', 'name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longitude',
                  'timestamp_last_updated', 'timestamp_created', 'sodas')
        # add conditionals here to restrict amount of data sent to frontend for query string filters


class SodaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Soda
        fields = ('id', 'name', 'abbreviation', 'low_calorie')
