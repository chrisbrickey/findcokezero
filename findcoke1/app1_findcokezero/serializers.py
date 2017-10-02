from rest_framework import serializers
from .models import Retailer

class RetailerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Retailer
        fields = ('name', 'street_address', 'city', 'postcode', 'country', 'latitude', 'longtitude', 'timestamp_last_updated', 'timestamp_created')
