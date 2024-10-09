import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from menu.pembayaran.models import Transaksi,Tarif,Diskon
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q,Prefetch
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


@login_required(login_url='user:masuk')
@admin_required
def export_tarif_excel(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    if dari_tanggal and sampai_tanggal:
        try:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
            if dari_tanggal > sampai_tanggal:
                messages.error(request, "Tanggal 'dari' tidak boleh lebih besar dari tanggal 'sampai'.")
                return redirect("menu:laporan-tarif")
        except ValueError:
            messages.error(request, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
            return redirect("menu:laporan-tarif")

    # Create filters based on created_at date range
    filters = Q()
    if dari_tanggal:
        filters &= Q(created_at__gte=dari_tanggal)  # Assuming you want to filter by created_at of Tarif
    if sampai_tanggal:
        filters &= Q(created_at__lte=sampai_tanggal)

    # Fetching all Tarif with related Diskon
    tarif_data = Tarif.objects.filter(filters).prefetch_related('diskon_set') if filters else Tarif.objects.prefetch_related('diskon_set').all()

    data = []
    for tarif in tarif_data:
        # Prepare the presentase diskon as a list of percentages
        presentase_diskon = [diskon.persentase_diskon for diskon in tarif.diskon_set.all()]

        # Format the creation date
        tanggal_dibuat = tarif.created_at.astimezone().strftime("%d %b. %Y")

        # Collect data for each tarif
        data.append({
            'Nama Tarif': tarif.subject,
            'Harga': tarif.harga,
            'Sedang Digunakan': "Ya" if tarif.is_used else "Tidak",
            'Jumlah Presentase Diskon': presentase_diskon if len(presentase_diskon)>0 else "Tidak ada diskon",
            'Tanggal Dibuat': tanggal_dibuat,
        })

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Create Excel response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Tarif.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Laporan Tarif', index=False)

    return response


@login_required(login_url='user:masuk')
@admin_required
def export_tarif_csv(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    if dari_tanggal and sampai_tanggal:
        try:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
            if dari_tanggal > sampai_tanggal:
                messages.error(request, "Tanggal 'dari' tidak boleh lebih besar dari tanggal 'sampai'.")
                return redirect("menu:laporan-tarif")
        except ValueError:
            messages.error(request, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
            return redirect("menu:laporan-tarif")

    # Create filters based on created_at date range
    filters = Q()
    if dari_tanggal:
        filters &= Q(created_at__gte=dari_tanggal)  # Assuming you want to filter by created_at of Tarif
    if sampai_tanggal:
        filters &= Q(created_at__lte=sampai_tanggal)

    # Fetching all Tarif with related Diskon
    tarif_data = Tarif.objects.filter(filters).prefetch_related('diskon_set') if filters else Tarif.objects.prefetch_related('diskon_set').all()

    data = []
    for tarif in tarif_data:
        # Prepare the presentase diskon as a list of percentages
        presentase_diskon = [diskon.persentase_diskon for diskon in tarif.diskon_set.all()]

        # Format the creation date
        tanggal_dibuat = tarif.created_at.astimezone().strftime("%d %b. %Y")

        # Collect data for each tarif
        data.append({
            'Nama Tarif': tarif.subject,
            'Harga': tarif.harga,
            'Sedang Digunakan': "Ya" if tarif.is_used else "Tidak",
            'Jumlah Presentase Diskon': presentase_diskon if len(presentase_diskon) > 0 else "Tidak ada diskon",
            'Tanggal Dibuat': tanggal_dibuat,
        })

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Tarif.csv'
    
    # Use Pandas to write the DataFrame to the CSV response
    df.to_csv(path_or_buf=response, index=False, encoding='utf-8')

    return response