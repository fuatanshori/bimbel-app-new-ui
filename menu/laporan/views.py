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
from django.db.models import Q, Sum, F,Avg
from django.contrib import messages
from core.utils.decorator import admin_pemateri_required,admin_required
from django.contrib.auth.decorators import login_required
from config import midtrans
from menu.levelstudy.models import LevelStudy 
from django.db import connection
from user.models import Profile
from menu.testimoni.models import Testimoni
from django.contrib.sites.shortcuts import get_current_site

@login_required(login_url='user:masuk')
def laporan(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT nama_mapel FROM mapel_matapelajaran")
        unique_mapel = cursor.fetchall()
    mapel_objs = [row[0] for row in unique_mapel]
    levelstudy_objs = LevelStudy.objects.all()

    return render(request,"laporan/laporan.html",{"mapel_objs":mapel_objs,"levelstudy_objs":levelstudy_objs})

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
            'transaksi_status': midtrans.PAYMENT_STATUS[transaksi.transaksi_status],
        })

    total_data = {
        'total_harga_awal': totals['total_harga_awal'] or 0,
        'total_diskon': totals['total_diskon'] or 0,
        'total_potongan': totals['total_potongan'] or 0,
        'total_harga_akhir': totals['total_harga_akhir'] or 0,
    }
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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
        
        diskon_list = diskon_query.annotate(
            jumlah_terpakai=Count('transaksi')
        )
        if diskon_list.exists(): 
            tarif_diskon_data[tarif] = []
            for diskon in diskon_list:
                total_diskon_terpakai += diskon.jumlah_terpakai
                
                potongan_harga_query = Transaksi.objects.filter(diskon=diskon)
                

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
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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
    context = {
        'tarif_diskon_data': tarif_diskon_data,
        'total_diskon_terpakai': total_diskon_terpakai,
        'total_harga_terpotong': total_harga_terpotong,
        'current_date': current_date,
        'filter_type': ft[filter_type],
        'qr_code': qr_code_b64, 
    }

    return render(request, 'laporan/laporan_diskon_terpakai_cetak.html', context)

@login_required(login_url='user:masuk')
@admin_required
def laporan_penggunaan_layanan_pembayaran(request):
    layanan_pembayaran = request.GET.get('layanan_pembayaran')
    filters = Q()
    if layanan_pembayaran:
        filters &= Q(layanan_pembayaran__icontains=layanan_pembayaran)

    payment_method_counts = Transaksi.objects.filter(filters).values('layanan_pembayaran').annotate(jumlah=Count('layanan_pembayaran'))
    payment_method_counts = list(payment_method_counts)
    
    current_date = datetime.date.today()
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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
        'layanan_pembayaran':layanan_pembayaran if layanan_pembayaran else "Semua layanan Pembayaran"
    })


@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan_ujian_diikuti(request):
    mapel = request.GET.get('mapel')
    filters = Q()
    if mapel:
        filters &= Q(nama_mapel__icontains=mapel)
    mapel_dengan_nilai = MataPelajaran.objects.select_related('level_study').values(
        'level_study__level_study',
        'level_study__kelas',
        'nama_mapel'
    ).annotate(
        jumlah_pengikut=Count('nilai', distinct=True)
    ).order_by(
        'level_study__level_study',
        'level_study__kelas',
        'nama_mapel'
    ).filter(filters)
    
    # Format data untuk template dengan informasi rowspan
    formatted_data = []
    current_data = list(mapel_dengan_nilai)
    
    # Hitung rowspan untuk level study dan kelas
    level_count = {}  # Counter untuk level study
    kelas_count = {}  # Counter untuk kombinasi level-kelas
    total_pengikut = 0
    
    for item in current_data:
        level = item['level_study__level_study']
        kelas = item['level_study__kelas']
        level_kelas = f"{level}-{kelas}"
        
        # Hitung untuk level study
        if level not in level_count:
            level_count[level] = 0
        level_count[level] += 1
        
        # Hitung untuk kelas
        if level_kelas not in kelas_count:
            kelas_count[level_kelas] = 0
        kelas_count[level_kelas] += 1
        
        total_pengikut += item['jumlah_pengikut']
    
    # Format data dengan rowspan
    current_level = None
    current_kelas = None
    current_level_kelas = None
    
    for item in current_data:
        level = item['level_study__level_study']
        kelas = item['level_study__kelas']
        level_kelas = f"{level}-{kelas}"
        
        # Tentukan rowspan untuk level study
        level_rowspan = level_count.get(level, 1) if level != current_level else 0
        
        # Tentukan rowspan untuk kelas
        kelas_rowspan = kelas_count.get(level_kelas, 1) if level_kelas != current_level_kelas else 0
        
        formatted_data.append({
            'level_study': level,
            'level_rowspan': level_rowspan,
            'kelas': kelas,
            'kelas_rowspan': kelas_rowspan,
            'mata_pelajaran': item['nama_mapel'],
            'jumlah_pengikut': item['jumlah_pengikut']
        })
        
        current_level = level
        current_level_kelas = level_kelas
    current_date = datetime.date.today()
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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
    context = {
        'data': formatted_data,
        'total_pengikut': total_pengikut,
        'title': 'Laporan Jumlah Peserta Ujian',
        'qr_code': qr_code_b64, 
        'current_date': current_date,
    }
    return render(request, 'laporan/laporan_ujian_diikuti_cetak.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def laporan_nilai(request):
    status_param = request.GET.get('status')
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
        filters &= Q(tanggal_ujian__date__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(tanggal_ujian__date__lte=sampai_tanggal)
    if status_param:
        filters &= Q(status=status_param)

    nilai_objs = Nilai.objects.filter(filters)
    # Menghitung total lulus dan tidak lulus
    total_lulus = nilai_objs.filter(status='lulus').count()
    total_tidak_lulus = nilai_objs.filter(status='tidak lulus').count()

    current_date = datetime.date.today()
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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
    context = {
        'nilai_objs': nilai_objs,
        'total_lulus': total_lulus,
        'total_tidak_lulus': total_tidak_lulus,
        'dari_tanggal': dari_tanggal,
        'sampai_tanggal': sampai_tanggal,
        'qr_code': qr_code_b64, 
        'current_date': current_date,
        'status':status_param if status_param else "Semua Ujian"
    }
    
    return render(request, 'laporan/laporan_nilai.html', context)


@login_required(login_url='user:masuk')
def laporan_nilai_persiswa(request):
    status_param = request.GET.get('status')
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
    
    filters = Q(user=request.user)
    if dari_tanggal:
        filters &= Q(tanggal_ujian__date__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(tanggal_ujian__date__lte=sampai_tanggal)
    if status_param:
        filters &= Q(status=status_param)

    nilai_siswa = Nilai.objects.filter(filters)
    total_nilai = sum(nilai.nilai for nilai in nilai_siswa)
    jumlah_mapel = nilai_siswa.count()
    rata_rata = total_nilai / jumlah_mapel if jumlah_mapel > 0 else 0
    jumlah_lulus = nilai_siswa.filter(status='lulus').count()
    jumlah_tidak_lulus = nilai_siswa.filter(status='tidak lulus').count()

    current_date = datetime.date.today()
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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
    context = {
        'nilai_siswa': nilai_siswa,
        'rata_rata': rata_rata,
        'jumlah_lulus': jumlah_lulus,
        'jumlah_tidak_lulus': jumlah_tidak_lulus,
        'qr_code': qr_code_b64, 
        'current_date': current_date,
        'dari_tanggal': dari_tanggal,
        'sampai_tanggal': sampai_tanggal,
        'status':status_param if status_param else "Semua Ujian",
        'profile_obj':Profile.objects.get(user=request.user)
    }
    return render(request, 'laporan/laporan_nilai_persiswa.html', context)

@login_required(login_url='user:masuk')
@admin_required
def laporan_testimoni(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    testimoni_objs = Testimoni.objects.all().select_related('user')

    if dari_tanggal:
        testimoni_objs = testimoni_objs.filter(tanggal__date__gte=dari_tanggal)
    if sampai_tanggal:
        testimoni_objs = testimoni_objs.filter(tanggal__date__lte=sampai_tanggal)

    total_testimoni = testimoni_objs.count()

    total_puas = testimoni_objs.filter(rating__gte=4).count()
    total_sedang = testimoni_objs.filter(rating=3).count()
    total_kecewa = testimoni_objs.filter(rating__lte=2).count()

    if total_testimoni > 0:
        persen_puas = (total_puas / total_testimoni) * 100
        persen_sedang = (total_sedang / total_testimoni) * 100
        persen_kecewa = (total_kecewa / total_testimoni) * 100
    else:
        persen_puas = persen_sedang = persen_kecewa = 0

    avg_rating = testimoni_objs.aggregate(Avg('rating'))['rating__avg']
    current_date = datetime.date.today()
    domain = get_current_site(request).domain
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}/static/assets/img/signature/signature.jpeg"
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

    context = {
        'testimoni_objs': testimoni_objs,
        'dari_tanggal': dari_tanggal,
        'sampai_tanggal': sampai_tanggal,
        'total_testimoni': total_testimoni,
        'total_puas': total_puas,
        'total_sedang': total_sedang,
        'total_kecewa': total_kecewa,
        'persen_puas': round(persen_puas, 1),
        'persen_sedang': round(persen_sedang, 1),
        'persen_kecewa': round(persen_kecewa, 1),
        'avg_rating': round(avg_rating, 2) if avg_rating else 0,
        'qr_code': qr_code_b64, 
        'current_date': current_date,
    }
    return render(request, 'laporan/laporan_testimoni.html', context)