from django.shortcuts import render
from menu.pembayaran.models import Transaksi
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from core.utils.decorator import admin_pemateri_required,admin_required
from django.contrib.auth.decorators import login_required

@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan(request):
    return render(request,"laporan/laporan.html")


@login_required(login_url='user:masuk')
@admin_required
def laporan_transaksi(request):
    cari_transaksi = request.GET.get('cari_transaksi', "")
    transaksi_objs = Transaksi.objects.filter(Q(pk__icontains=cari_transaksi))
    if not transaksi_objs.exists():
        messages.warning(request, "Tidak ada transaksi ditemukan.")
    context = {
        "transaksi_objs": transaksi_objs,
    }
    return render(request, 'laporan/laporan_transaksi.html', context)