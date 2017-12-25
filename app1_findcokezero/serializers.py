from rest_framework import serializers
from .models import Retailer, Soda

class RetailerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Retailer
        fields = ('id', 'name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longtitude', 'timestamp_last_updated', 'timestamp_created', 'sodas')
        #add conditionals here to restrict amount of data sent to frontend for query string filters

class SodaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Soda
        fields = ('id', 'name', 'abbreviation', 'low_calorie')
