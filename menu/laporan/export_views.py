import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from menu.pembayaran.models import Transaksi
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from core.utils.decorator import admin_pemateri_required,admin_required
from django.contrib.auth.decorators import login_required

@login_required(login_url='user:masuk')
@admin_required
def export_transaksi_excel(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    if dari_tanggal and sampai_tanggal:
        try:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
            if dari_tanggal > sampai_tanggal:
                messages.error(request, "Tanggal 'dari' tidak boleh lebih besar dari tanggal 'sampai'.")
                return redirect("menu:laporan-transaksi")
        except ValueError:
            messages.error(request, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
            return redirect("menu:laporan-transaksi")
    
    filters = Q()
    if dari_tanggal:
        filters &= Q(transaction_time__date__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(transaction_time__date__lte=sampai_tanggal)
    transaksi_data = Transaksi.objects.filter(filters) if filters else Transaksi.objects.all()
    data = []
    
    for transaksi in transaksi_data:
        user_name = transaksi.user.full_name if transaksi.user else 'N/A'
        layanan_pembayaran = transaksi.layanan_pembayaran if transaksi.layanan_pembayaran else "N/A"
        harga_awal = transaksi.tarif.harga if transaksi.tarif else 0
        transaksi_harga = transaksi.harga if transaksi.harga else 0
        diskon = transaksi.diskon if transaksi.diskon else None
        diskon_persen = diskon.persentase_diskon if diskon else 0
        diskon_nama = diskon.diskon_name if diskon else "N/A"

        transaction_time = transaksi.transaction_time.astimezone().replace(tzinfo=None).strftime("%d/%m/%Y") if transaksi.transaction_time else 'N/A'
        data.append({
            'ID Transaksi': transaksi.id_transaksi,
            'Nama Pengguna': user_name,
            'layanan_pembayaran': layanan_pembayaran,
            'Harga Awal': harga_awal,
            'Diskon Nama': diskon_nama,
            'Diskon (%)': diskon_persen,
            'Status Transaksi': transaksi.transaksi_status,
            'Harga Akhir': transaksi_harga,
            'Waktu Transaksi': transaction_time,
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Transaksi.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Laporan Transaksi', index=False)

    return response


@login_required(login_url='user:masuk')
@admin_required
def export_transaksi_csv(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')
    if dari_tanggal and sampai_tanggal:
        try:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
            if dari_tanggal > sampai_tanggal:
                messages.error(request, "Tanggal 'dari' tidak boleh lebih besar dari tanggal 'sampai'.")
                return redirect("menu:laporan-transaksi")
        except ValueError:
            messages.error(request, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
            return redirect("menu:laporan-transaksi")
        
    filters = Q()
    if dari_tanggal:
        filters &= Q(transaction_time__date__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(transaction_time__date__lte=sampai_tanggal)
    transaksi_data = Transaksi.objects.filter(filters) if filters else Transaksi.objects.all()
    data = []

    
    for transaksi in transaksi_data:
        user_name = transaksi.user.full_name if transaksi.user else 'N/A'
        layanan_pembayaran = transaksi.layanan_pembayaran if transaksi.layanan_pembayaran else "N/A"
        harga_awal = transaksi.tarif.harga if transaksi.tarif else 0
        transaksi_harga = transaksi.harga if transaksi.harga else 0
        diskon = transaksi.diskon if transaksi.diskon else None
        diskon_persen = diskon.persentase_diskon if diskon else 0
        diskon_nama = diskon.diskon_name if diskon else "N/A"

        transaction_time = transaksi.transaction_time.astimezone().replace(tzinfo=None) if transaksi.transaction_time else 'N/A'
        data.append({
            'ID Transaksi': transaksi.id_transaksi,
            'Nama Pengguna': user_name,
            'Layanan Pembayaran': layanan_pembayaran,
            'Harga Awal': harga_awal,
            'Diskon Nama': diskon_nama,
            'Diskon (%)': diskon_persen,
            'Status Transaksi': transaksi.transaksi_status,
            'Harga Akhir': transaksi_harga,
            'Waktu Transaksi': transaction_time,
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Transaksi.csv'
    df.to_csv(response, index=False)
    return response
