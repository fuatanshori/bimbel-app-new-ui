from django.shortcuts import render,HttpResponse
from menu.pembayaran.models import Tarif,Diskon
from menu.testimoni.models import Testimoni

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
    try:
        testimoni_objs = Testimoni.objects.select_related('user__profile').all()
    except Testimoni.DoesNotExist:
        testimoni_objs = None

    context={
        "tarif_obj":tarif_obj,
        "diskon_objs":diskon_objs,
        "testimoni_objs":testimoni_objs,
        "star_range":range(1,6)
    }
    return render(request,'home/home.html',context)