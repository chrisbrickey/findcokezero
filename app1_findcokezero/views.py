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

    serializer_class = RetailerSerializer
    # queryset = Retailer.objects.all()

    def get_queryset(self):
        queryset = Retailer.objects.all()
        post_code = self.request.query_params.get('postcode', None)
        sodas= self.request.query_params.get('sodas', None)

        if post_code is not None:
            queryset = queryset.filter(postcode=post_code)

        if sodas is not None:
            soda_array = list(map(lambda x: str(x), sodas.split(",")))

            new_queryset = []
            for retailer in queryset:

                queryset_sodas = retailer.sodas.all()
                queryset_soda_abbrevs = list(map(lambda x: x.abbreviation, queryset_sodas))
                has_all = True

                for soda in soda_array:
                    if soda not in queryset_soda_abbrevs:
                        has_all = False

                if has_all == True:
                    new_queryset.append(retailer)

            queryset = new_queryset

        return queryset


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
    serializer_context = {'request': request}
    serializer = SodaSerializer(retailer_sodas, many=True, context=serializer_context)
    return Response(serializer.data)

@csrf_exempt
@api_view(['GET'])
def retailers_by_sodas(request, pk):
    """
    API endpoint that shows retailers filtered by soda.
    """
    soda = Soda.objects.filter(id=pk)[0]
    soda_retailers = soda.retailer_set.all()
    serializer_context = {'request': request}
    serializer = RetailerSerializer(soda_retailers, context=serializer_context, many=True)
    return Response(serializer.data)
