from django.shortcuts import render,HttpResponse
from menu.pembayaran.models import Tarif,Diskon


# Create your views here.
def home(request):
    try:
        tarif_obj = Tarif.get_tarif_is_used()
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