import qrcode
import base64
from django.shortcuts import render,redirect
from io import BytesIO
import datetime
from django.db.models import Count, Q,Sum
from django.utils import timezone
from menu.pembayaran.models import Transaksi,Tarif,Diskon
from menu.mapel.models import MataPelajaran
from menu.nilai.models import Nilai
from django.db.models import Q, Sum, F,Avg,Min,Max,StdDev
from django.contrib import messages
from core.utils.decorator import admin_pemateri_required,admin_required
from django.contrib.auth.decorators import login_required
from config import midtrans
from menu.levelstudy.models import LevelStudy 

@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan(request):
    return render(request,"laporan/laporan.html")


@login_required(login_url='user:masuk')
@admin_required
def laporan_transaksi(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')
    payment_status = request.GET.get('payment_status')
    try:
        if dari_tanggal:
            dari_tanggal = timezone.make_aware(timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d'))
        if sampai_tanggal:
            sampai_tanggal = timezone.make_aware(timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d'))

        if dari_tanggal and sampai_tanggal and dari_tanggal > sampai_tanggal:
            messages.error(request, "Tanggal 'dari' tidak boleh lebih besar dari tanggal 'sampai'.")
            return redirect("menu:laporan")
    except ValueError:
        messages.error(request, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
        return redirect("menu:laporan")
    
    filters = Q()
    if dari_tanggal:
        filters &= Q(transaction_time__date__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(transaction_time__date__lte=sampai_tanggal)
    if payment_status:
        filters &= Q(transaksi_status=payment_status)

    transaksi_list = Transaksi.objects.filter(filters)
    totals = transaksi_list.aggregate(
        total_harga_awal=Sum('harga_awal'),
        total_diskon=Sum(F('diskon__persentase_diskon'), default=0),
        total_potongan=Sum('harga_terpotong'),
        total_harga_akhir=Sum('harga_akhir')
    )

    laporan_data = []
    for transaksi in transaksi_list:
        diskon_persen = transaksi.diskon.persentase_diskon if transaksi.diskon else 0

        laporan_data.append({
            'nama': transaksi.user.full_name,
            'tanggal_transaksi': timezone.localtime(transaksi.transaction_time).strftime("%d/%m/%Y") if transaksi.transaction_time else 'N/A',
            'harga_awal': transaksi.harga_awal,
            'diskon': diskon_persen,
            'potongan': transaksi.harga_terpotong,
            'harga_akhir': transaksi.harga_akhir,
        })

    total_data = {
        'total_harga_awal': totals['total_harga_awal'] or 0,
        'total_diskon': totals['total_diskon'] or 0,
        'total_potongan': totals['total_potongan'] or 0,
        'total_harga_akhir': totals['total_harga_akhir'] or 0,
    }

    qr_data = "Dummy Signature Data"
    qr_img = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_img.add_data(qr_data)
    qr_img.make(fit=True)

    img = qr_img.make_image(fill_color="black", back_color="transparent")

    qr_io = BytesIO()
    img.save(qr_io, format='PNG')
    qr_io.seek(0)

    qr_code_b64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')

    return render(request, 'laporan/laporan_transaksi_cetak.html', {
        'laporan_data': laporan_data,
        'total_data': total_data,
        'qr_code': qr_code_b64, 
        'current_date': datetime.date.today(),
        'dari_tanggal': dari_tanggal,
        'sampai_tanggal': sampai_tanggal,
        'payment_status':"Semua Transaksi" if not payment_status else midtrans.PAYMENT_STATUS[payment_status],
    })

@login_required(login_url='user:masuk')
@admin_required
def laporan_penggunaan_diskon(request):
    filter_type = request.GET.get('filter', 'all')
    payment_status = request.GET.get('payment_status', 'all')
    
    tarif_list = Tarif.objects.all()
    
    tarif_diskon_data = {}
    total_diskon_terpakai = 0
    total_harga_terpotong = 0
    today = timezone.now().date()
    ft = {
        'active':'Diskon Aktif',
        'all':'Semua Diskon',
        'expired':"Diskon Kedaluwarsa"
    }
    for tarif in tarif_list:
        diskon_query = Diskon.objects.filter(tarif=tarif)
        if filter_type == 'active':
            diskon_query = diskon_query.filter(kedaluwarsa__gte=today)
        elif filter_type == 'expired':
            diskon_query = diskon_query.filter(kedaluwarsa__lt=today)
        
        if payment_status != "all":
            diskon_list = diskon_query.annotate(
                jumlah_terpakai=Count('transaksi',filter=Q(transaksi__transaksi_status=payment_status))
            )
        else:
            diskon_list = diskon_query.annotate(
                jumlah_terpakai=Count('transaksi')
            )
        if diskon_list.exists(): 
            tarif_diskon_data[tarif] = []
            for diskon in diskon_list:
                total_diskon_terpakai += diskon.jumlah_terpakai
                
                potongan_harga_query = Transaksi.objects.filter(diskon=diskon)
                
                if payment_status != 'all':
                    potongan_harga_query = potongan_harga_query.filter(transaksi_status=payment_status)
                
                potongan_harga = potongan_harga_query.aggregate(
                    total_potongan=Sum('harga_terpotong')
                )['total_potongan'] or 0
                
                total_harga_terpotong += potongan_harga
                
                tarif_diskon_data[tarif].append({
                    'nama_diskon': diskon.diskon_name,
                    'jumlah_terpakai': diskon.jumlah_terpakai,
                    'kedaluwarsa': diskon.kedaluwarsa,
                    'status': 'Aktif' if diskon.kedaluwarsa >= today else 'Kedaluwarsa',
                    'potongan_harga': potongan_harga,
                })

    current_date = datetime.date.today()
    
    context = {
        'tarif_diskon_data': tarif_diskon_data,
        'total_diskon_terpakai': total_diskon_terpakai,
        'total_harga_terpotong': total_harga_terpotong,
        'current_date': current_date,
        'filter_type': ft[filter_type],
        'payment_status': "Semua Transaksi" if payment_status == "all" else midtrans.PAYMENT_STATUS[payment_status],
    }

    return render(request, 'laporan/laporan_diskon_terpakai_cetak.html', context)

@login_required(login_url='user:masuk')
@admin_required
def laporan_penggunaan_layanan_pembayaran(request):
    payment_status = request.GET.get('payment_status')
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')
    try:
        if dari_tanggal:
            dari_tanggal = timezone.make_aware(timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d'))
        if sampai_tanggal:
            sampai_tanggal = timezone.make_aware(timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d'))

        if dari_tanggal and sampai_tanggal and dari_tanggal > sampai_tanggal:
            messages.error(request, "Tanggal 'dari' tidak boleh lebih besar dari tanggal 'sampai'.")
            return redirect("menu:laporan")
    except ValueError:
        messages.error(request, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD.")
        return redirect("menu:laporan")
    
    filters = Q()
    if dari_tanggal:
        filters &= Q(transaction_time__date__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(transaction_time__date__lte=sampai_tanggal)
    if payment_status:
        filters &= Q(transaksi_status=payment_status)
    payment_method_counts = Transaksi.objects.filter(filters).values('layanan_pembayaran').annotate(jumlah=Count('layanan_pembayaran'))
    payment_method_counts = list(payment_method_counts)
    
    current_date = datetime.date.today()
    qr_data = "Dummy Signature Data"
    qr_img = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_img.add_data(qr_data)
    qr_img.make(fit=True)

    img = qr_img.make_image(fill_color="black", back_color="transparent")
    qr_io = BytesIO()
    img.save(qr_io, format='PNG')
    qr_io.seek(0)
    qr_code_b64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
    return render(request, 'laporan/laporan_layanan_pembayaran_cetak.html', {
        'payment_method_counts': payment_method_counts,
        'current_date': current_date,
        'qr_code':qr_code_b64,
        'dari_tanggal': dari_tanggal,
        'sampai_tanggal': sampai_tanggal,
        'payment_status':"Semua Transaksi" if not payment_status else midtrans.PAYMENT_STATUS[payment_status],
    })


@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan_ujian_diikuti(request):
    level_studies = LevelStudy.objects.all()
    mata_pelajarans = MataPelajaran.objects.all()
    
    nilai_counts = Nilai.objects.values(
        'level_study', 
        'mata_pelajaran'
    ).annotate(
        jumlah_pengikut=Count('user')
    ).order_by('level_study', 'mata_pelajaran')
    
    peserta_count_dict = {}
    for item in nilai_counts:
        key = (item['level_study'], item['mata_pelajaran'])
        peserta_count_dict[key] = item['jumlah_pengikut']
        
    grouped_data = {}
    total_peserta = 0
    
    for level in level_studies:
        level_name = level.level_study
        if level_name not in grouped_data:
            grouped_data[level_name] = []
            
        mapels = mata_pelajarans.filter(level_study=level)
        for mapel in mapels:
            mapel_name = mapel.nama_mapel
            jumlah = peserta_count_dict.get((level_name, mapel_name), 0)
            grouped_data[level_name].append({
                'mata_pelajaran': mapel_name,
                'jumlah_pengikut': jumlah
            })
            total_peserta += jumlah
    
    context = {
        'level_mapel_data': grouped_data,
        'total_peserta': total_peserta,
    }
    return render(request, 'laporan/laporan_ujian_diikuti_cetak.html', context)