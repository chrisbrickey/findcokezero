# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from .models import Retailer, Soda
from rest_framework import viewsets
from .serializers import RetailerSerializer, SodaSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@csrf_exempt
@api_view(['GET'])
def sodas_by_retailer(request, pk):
    """
    API endpoint that shows sodas filtered by retailer.
    """
    retailer = Retailer.objects.filter(id=pk)[0]
    retailer_sodas = retailer.sodas.all()
    serializer = SodaSerializer(retailer_sodas, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['GET'])
def retailers_by_sodas(request, pk):
    """
    API endpoint that shows retails filtered by soda.
    """
    soda = Soda.objects.filter(id=pk)[0]
    soda_retailers = soda.retailer_set.all()
    serializer_context = {'request': request}
    serializer = RetailerSerializer(soda_retailers, context=serializer_context, many=True)
    return Response(serializer.data)