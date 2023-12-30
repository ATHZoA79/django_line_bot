from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import json


# Create your views here.
def index(request: HttpRequest):
    # return render(request, "index.html")
    payload = {"name": "ZoA"}
    return HttpResponse(json.dumps(payload))
