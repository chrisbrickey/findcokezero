from django.shortcuts import render

# landing page; not part of the hyper-linked api
def index(request):
    return render(
        request,
        'index.html',
        context={},
    )
