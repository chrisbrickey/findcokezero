# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(
        request,
        'index.html',
        context={},
    )

def landing_page(request):
    html = """
            <html>
            <head>
            </head>
            <body>
                <h1>FindCokeZero</h1>
                </br>
                <a href="https://www.findcokezero.com/api/">Visit the browseable API while I complete frontend development</a>
            </body>
            </html>
            """
    return HttpResponse(html)
