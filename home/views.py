from django.shortcuts import render,HttpResponse
from menu.pembayaran.models import Tarif,Diskon


# Create your views here.
def home(request):
    try:
        tarif_obj = Tarif.objects.get(is_used=True)
    except Tarif.DoesNotExist:
        tarif_obj = None
    try:
        diskon_objs = Diskon.objects.filter(tarif=tarif_obj,is_publish=True)
    except Diskon.DoesNotExist:
        diskon_objs = None
    context={
        "tarif_obj":tarif_obj,
        "diskon_objs":diskon_objs,
    }
    return render(request,'home/home.html',context)