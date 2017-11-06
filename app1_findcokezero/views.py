# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from .models import Retailer, Soda
from rest_framework import viewsets
from .serializers import RetailerSerializer, SodaSerializer

class RetailerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows retailers to be viewed or edited.
    """
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer

class SodaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sodas to be viewed or edited.
    """
    queryset = Soda.objects.all()
    serializer_class = SodaSerializer
