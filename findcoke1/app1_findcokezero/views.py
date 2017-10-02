# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from .models import Retailer
from rest_framework import viewsets
from .serializers import RetailerSerializer

class RetailerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows retailers to be viewed or edited.
    """
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer
