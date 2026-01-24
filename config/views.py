from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# landing page; not part of the hyper-linked api
def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'index.html',
        context={},
    )
