from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Retailer, Soda
from .serializers import RetailerSerializer, SodaSerializer

class RetailerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows retailers to be viewed or edited.
    """

    serializer_class = RetailerSerializer
    # queryset = Retailer.objects.all()

    def get_queryset(self):
        queryset = Retailer.objects.prefetch_related('sodas')
        post_code = self.request.query_params.get('postcode', None)
        sodas= self.request.query_params.get('sodas', None)

        if post_code is not None:
            queryset = queryset.filter(postcode=post_code)

        if sodas is not None:
            soda_abbrevs = sodas.split(",")
            for abbrev in soda_abbrevs:
                queryset = queryset.filter(sodas__abbreviation=abbrev)
            queryset = queryset.distinct()

        return queryset


class SodaViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sodas to be viewed or edited.
    """
    queryset = Soda.objects.all()
    serializer_class = SodaSerializer


@api_view(['GET'])
def sodas_by_retailer(request, pk):
    """
    API endpoint that shows sodas filtered by retailer.
    """
    retailer = get_object_or_404(Retailer, id=pk)
    retailer_sodas = retailer.sodas.all()
    serializer_context = {'request': request}
    serializer = SodaSerializer(retailer_sodas, many=True, context=serializer_context)
    return Response(serializer.data)

@api_view(['GET'])
def retailers_by_sodas(request, pk):
    """
    API endpoint that shows retailers filtered by soda.
    """
    soda = get_object_or_404(Soda, id=pk)
    soda_retailers = soda.retailer_set.all()
    serializer_context = {'request': request}
    serializer = RetailerSerializer(soda_retailers, context=serializer_context, many=True)
    return Response(serializer.data)
