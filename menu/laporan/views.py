import qrcode
import base64
from django.shortcuts import render
from io import BytesIO
import datetime
from django.db.models import Count, Q,Sum
from django.utils import timezone
from menu.pembayaran.models import Transaksi,Tarif,Diskon
from menu.mapel.models import MataPelajaran
from menu.nilai.models import Nilai
from django.db.models import Q
from django.contrib import messages
from core.utils.decorator import admin_pemateri_required,admin_required
from django.contrib.auth.decorators import login_required
from user.models import Profile

@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan(request):
    return render(request,"laporan/laporan.html")

def laporan_pendapatan(request):
    # Query all transactions
    transaksi_list = Transaksi.objects.filter(transaksi_status="settlement")

    # Initialize variables for calculations
    total_harga_awal = 0
    total_diskon = 0
    total_potongan = 0
    total_harga_akhir = 0

    # Prepare the data for rendering
    laporan_data = []
    
    for transaksi in transaksi_list:
        harga_awal = transaksi.tarif.harga if transaksi.tarif is not None else 0
        diskon_persen = transaksi.diskon.persentase_diskon if transaksi.diskon else 0
        potongan = harga_awal * (diskon_persen / 100)
        harga_akhir = harga_awal - potongan

        # Append data for each transaction
        laporan_data.append({
            'nama': transaksi.user.full_name,
            'tanggal_transaksi': transaksi.transaction_time.strftime("%d/%m/%Y") if transaksi.transaction_time else 'N/A',
            'harga_awal': harga_awal,
            'diskon': diskon_persen,
            'potongan': potongan,
            'harga_akhir': harga_akhir,
        })

        # Update total values
        total_harga_awal += harga_awal
        total_diskon += diskon_persen
        total_potongan += potongan
        total_harga_akhir += harga_akhir

    # Prepare totals for rendering
    total_data = {
        'total_harga_awal': total_harga_awal,
        'total_diskon': total_diskon,
        'total_potongan': total_potongan,
        'total_harga_akhir': total_harga_akhir,
    }

    qr_data = "Dummy Signature Data"  # Replace with actual data
    qr_img = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_img.add_data(qr_data)
    qr_img.make(fit=True)

    # Create a QR code image
    img = qr_img.make_image(fill_color="black", back_color="transparent")

    # Save the transparent QR code to a BytesIO object
    qr_io = BytesIO()
    img.save(qr_io, format='PNG')
    qr_io.seek(0)

    # Encode the image in base64
    qr_code_b64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')

    # Render the template with the data and QR code
    return render(request, 'laporan/laporan_transaksi_cetak.html', {
        'laporan_data': laporan_data,
        'total_data': total_data,
        'qr_code': qr_code_b64,  # Pass the base64 encoded QR code image
        "current_date": datetime.date.today(),
    })

def get_tarif_diskon(request):
    filter_type = request.GET.get('filter', 'all')  # Default 'all'
    tarif_list = Tarif.objects.all()
    tarif_diskon_data = {}
    total_diskon_terpakai = 0
    total_harga_terpotong = 0  # Untuk menghitung total harga yang terpotong
    today = timezone.now().date()

    for tarif in tarif_list:
        diskon_query = Diskon.objects.filter(tarif=tarif)
        
        if filter_type == 'active':
            diskon_query = diskon_query.filter(kedaluwarsa__gte=today)
        elif filter_type == 'expired':
            diskon_query = diskon_query.filter(kedaluwarsa__lt=today)
        
        diskon_list = diskon_query.annotate(
            jumlah_terpakai=Count('transaksi')
        )
        
        if diskon_list.exists():
            tarif_diskon_data[tarif] = []
            for diskon in diskon_list:
                total_diskon_terpakai += diskon.jumlah_terpakai
                
                # Hitung total harga terpotong dari transaksi yang menggunakan diskon ini
                potongan_harga = Transaksi.objects.filter(diskon=diskon,transaksi_status="settlement").aggregate(
                    total_potongan=Sum('harga_terpotong')
                )['total_potongan'] or 0
                
                total_harga_terpotong += potongan_harga
                
                tarif_diskon_data[tarif].append({
                    'nama_diskon': diskon.diskon_name,
                    'jumlah_terpakai': diskon.jumlah_terpakai,
                    'kedaluwarsa': diskon.kedaluwarsa,
                    'status': 'Aktif' if diskon.kedaluwarsa >= today else 'Kedaluwarsa',
                    'potongan_harga': potongan_harga,  # Ambil potongan harga dari database
                })

    current_date = datetime.date.today()

    context = {
        'tarif_diskon_data': tarif_diskon_data,
        'total_diskon_terpakai': total_diskon_terpakai,
        'total_harga_terpotong': total_harga_terpotong,  # Tambahkan total harga yang terpotong ke context
        'current_date': current_date,
        'filter_type': filter_type,
    }

    return render(request, 'laporan/laporan_diskon_terpakai_cetak.html', context)
