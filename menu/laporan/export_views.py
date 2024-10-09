import pandas as pd
from django.http import HttpResponse
from django.utils import timezone
from menu.pembayaran.models import Transaksi

def export_transaksi_excel(request):
    # Mengambil query params untuk rentang tanggal
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    # Mengonversi string tanggal menjadi objek datetime
    if dari_tanggal and sampai_tanggal:
        try:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
        except ValueError:
            return HttpResponse("Format tanggal tidak valid. Gunakan YYYY-MM-DD.", status=400)
        
        # Filter transaksi berdasarkan rentang tanggal
        transaksi_data = Transaksi.objects.select_related('user', 'tarif', 'diskon').filter(
            transaction_time__date__range=(dari_tanggal, sampai_tanggal)
        )
    else:
        # Jika tidak ada rentang tanggal, ambil semua data transaksi
        transaksi_data = Transaksi.objects.select_related('user', 'tarif', 'diskon').all()

    data = []
    
    for transaksi in transaksi_data:
        user_name = transaksi.user.full_name if transaksi.user else 'N/A'
        layanan_pembayaran = transaksi.layanan_pembayaran if transaksi.layanan_pembayaran else "N/A"
        harga_awal = transaksi.tarif.harga if transaksi.tarif else 0
        transaksi_harga = transaksi.harga if transaksi.harga else 0
        diskon = transaksi.diskon if transaksi.diskon else None
        diskon_persen = diskon.persentase_diskon if diskon else 0
        diskon_nama = diskon.diskon_name if diskon else "N/A"

        # Mengonversi transaction_time ke naive datetime (tanpa timezone)
        transaction_time = transaksi.transaction_time.astimezone().replace(tzinfo=None) if transaksi.transaction_time else 'N/A'

        # Menambahkan data transaksi ke dalam list
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

    # Mengonversi data ke dalam DataFrame pandas
    df = pd.DataFrame(data)

    # Membuat file Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Transaksi.xlsx'

    # Menggunakan Pandas untuk menulis data ke Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Laporan Transaksi', index=False)

    return response



import pandas as pd
from django.http import HttpResponse
from django.utils import timezone

def export_transaksi_csv(request):
    # Mengambil query params untuk rentang tanggal
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    # Mengonversi string tanggal menjadi objek datetime
    if dari_tanggal and sampai_tanggal:
        try:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
        except ValueError:
            return HttpResponse("Format tanggal tidak valid. Gunakan YYYY-MM-DD.", status=400)
        
        # Filter transaksi berdasarkan rentang tanggal
        transaksi_data = Transaksi.objects.select_related('user', 'tarif', 'diskon').filter(
            transaction_time__date__range=(dari_tanggal, sampai_tanggal)
        )
    else:
        # Jika tidak ada rentang tanggal, ambil semua data transaksi
        transaksi_data = Transaksi.objects.select_related('user', 'tarif', 'diskon').all()

    data = []
    
    for transaksi in transaksi_data:
        user_name = transaksi.user.full_name if transaksi.user else 'N/A'
        layanan_pembayaran = transaksi.layanan_pembayaran if transaksi.layanan_pembayaran else "N/A"
        harga_awal = transaksi.tarif.harga if transaksi.tarif else 0
        transaksi_harga = transaksi.harga if transaksi.harga else 0
        diskon = transaksi.diskon if transaksi.diskon else None
        diskon_persen = diskon.persentase_diskon if diskon else 0
        diskon_nama = diskon.diskon_name if diskon else "N/A"

        # Mengonversi transaction_time ke naive datetime (tanpa timezone)
        transaction_time = transaksi.transaction_time.astimezone().replace(tzinfo=None) if transaksi.transaction_time else 'N/A'

        # Menambahkan data transaksi ke dalam list
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

    # Mengonversi data ke dalam DataFrame pandas
    df = pd.DataFrame(data)

    # Membuat file CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Transaksi.csv'

    # Menggunakan Pandas untuk menulis data ke CSV
    df.to_csv(response, index=False)

    return response
