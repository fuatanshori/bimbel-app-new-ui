from django.shortcuts import render
from django.conf import settings

# Create your views here.
def home(request):
    print(settings.DEBUG)
    print(settings.IS_DOCKER)
    return render(request,'home/home.html',status=200)