from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from menu.levelstudy.models import LevelStudy
from menu.mapel.models import MataPelajaran
from menu.modul.models import Modul
from menu.ujian.models import SoalUjian
from menu.nilai.models import Nilai
from menu.pembayaran.models import Transaksi


@login_required(login_url="user:masuk")
def menu(request):
    if request.user.is_authenticated and request.user.role=="pelajar":
        
        nilai_count = Nilai.objects.filter(user=request.user).count()
        transaksi_count = Transaksi.objects.filter(user=request.user).count()
    else:
        nilai_count = Nilai.objects.all().count()
        transaksi_count = Transaksi.objects.all().count()
    levelstudy_count = LevelStudy.objects.all().count()
    mapel_count = MataPelajaran.objects.all().count()
    modul_count = Modul.objects.all().count()
    ujian_count = SoalUjian.objects.all().count()
    context = {
        "levelstudy_count":levelstudy_count,
        "mapel_count":mapel_count,
        "modul_count":modul_count,
        "ujian_count":ujian_count,
        "transaksi_count":transaksi_count,
        "nilai_count":nilai_count,

    }
    return render(request, "menu/menu.html",context)
