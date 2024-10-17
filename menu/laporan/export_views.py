import pandas as pd
from django.http import HttpResponse,Http404
from django.utils import timezone
from menu.pembayaran.models import Transaksi,Tarif
from user.models import Profile
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
from core.utils.decorator import admin_pemateri_required,admin_required
from django.contrib.auth.decorators import login_required
from menu.mapel.models import MataPelajaran
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO
import babel
import datetime
from config import midtrans
from reportlab.lib.pagesizes import A4

@login_required(login_url='user:masuk')
@admin_required
def laporan_transaksi_invoice(request,id_transaksi):
    try:
        transaksi_obj = Transaksi.objects.get(pk=id_transaksi)
    except Transaksi.DoesNotExist:
        raise Http404()
    waktu_transaksi = timezone.localtime(transaksi_obj.transaction_time)
    data = {
        'title': 'Bimbingan belajar banua',
        'date': babel.dates.format_date(datetime.date.today(),locale="id"),
        'nama' :transaksi_obj.user.full_name,
        'invoice_number': f'#{str(transaksi_obj.id_transaksi)}',
        'price': transaksi_obj.harga,
        'status': midtrans.PAYMENT_STATUS[transaksi_obj.transaksi_status],
        'virtual_number': transaksi_obj.va_number,
        'layanan_pembayaran': str(transaksi_obj.layanan_pembayaran).upper(),
        'waktu_transaksi':waktu_transaksi.strftime("%d-%m-%Y %H:%M WIB"),
        'note': '*Invoice ini sah diterbitkan langsung oleh pihak bimbingan belajar banua'
    }
    half_A4 = (A4[0], A4[1] / 2)

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=half_A4)
    p.setTitle("Invoice - Bimbingan Belajar Banua")
    width, height = half_A4

    p.setFont("Helvetica", 10)
    p.drawString(15 * cm, height - 1 * cm, f"Tanggal Dicetak: {data['date']}")
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(1 * cm, height - 2.9 * cm, data['title'])

    # Date and Invoice Label
    p.setFillColor(colors.black)
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(width - 10 * cm, height - 2.7 * cm, "Invoice")

    p.setFont("Helvetica", 12)
    p.drawString(width - 10 * cm, height - 3.2 * cm, data['invoice_number'])

    p.setStrokeColor(colors.black)
    p.line(1 * cm, height - 3.9 * cm, width - 1 * cm, height - 3.9 * cm)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(2 * cm, height - 5 * cm, "Detail Pembayaran")

    p.setFont("Helvetica", 12)
    p.drawString(2 * cm, height - 6 * cm, f"Nama: {data["nama"]} ")

    p.setFont("Helvetica", 12)
    p.drawString(2 * cm, height - 7 * cm, f"Layanan Pembayaran: {data['layanan_pembayaran']}")#5.2
    if data['virtual_number']:
        p.drawString(2 * cm, height - 8 * cm, f"Virtual number: {data['virtual_number']}")#5.9
        p.drawString(2 * cm, height - 9 * cm, f"Status: {data['status']}")#6.6
        p.drawString(2 * cm, height - 10 * cm, f"Waktu Transaksi: {data['waktu_transaksi']}")#6.6
        p.setStrokeColor(colors.black)
        p.line(1 * cm, height - 11 * cm, width - 1 * cm, height - 11 * cm)

        p.setFont("Helvetica-Bold", 14)
        p.drawString(2 * cm, height - 12 * cm, f"Total Harga: Rp. {data['price']}")#8
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 10)
        p.drawString(2 * cm, 1.5 * cm, data['note'])
    else:
        p.drawString(2 * cm, height - 8 * cm, f"Status: {data['status']}")#6.6
        p.drawString(2 * cm, height - 9 * cm, f"Waktu Transaksi: {data['waktu_transaksi']}")#6.6
        
        
        p.setStrokeColor(colors.black)
        p.line(1 * cm, height - 11 * cm, width - 1 * cm, height - 11 * cm)

        p.setFont("Helvetica-Bold", 14)
        p.drawString(2 * cm, height - 12 * cm, f"Total Harga: Rp. {data['price']}")#8
        p.setFillColor(colors.black)
        p.setFont("Helvetica", 10)
        p.drawString(2 * cm, 1.5 * cm, data['note'])
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response


@login_required(login_url='user:masuk')
@admin_required
def export_transaksi_excel(request):
    dari_tanggal = request.GET.get('dari_tanggal')
    sampai_tanggal = request.GET.get('sampai_tanggal')

    try:
        if dari_tanggal:
            dari_tanggal = timezone.datetime.strptime(dari_tanggal, '%Y-%m-%d')
        if sampai_tanggal:
            sampai_tanggal = timezone.datetime.strptime(sampai_tanggal, '%Y-%m-%d')
        if dari_tanggal and sampai_tanggal and dari_tanggal > sampai_tanggal:
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

    # total_status = {'settlement': 0, 'pending': 0, 'expire': 0}
    data = []

    for transaksi in transaksi_data:
        user_name = transaksi.user.full_name if transaksi.user else 'N/A'
        layanan_pembayaran = transaksi.layanan_pembayaran or "N/A"
        harga_awal = transaksi.tarif.harga if transaksi.tarif else 0
        transaksi_harga = transaksi.harga or 0
        diskon = transaksi.diskon
        diskon_persen = diskon.persentase_diskon if diskon else 0
        diskon_nama = diskon.diskon_name if diskon else "N/A"
        transaction_time = transaksi.transaction_time.astimezone().replace(tzinfo=None).strftime("%d/%m/%Y") if transaksi.transaction_time else 'N/A'
        
        # total_status[transaksi.transaksi_status] = total_status.get(transaksi.transaksi_status, 0) + transaksi_harga
        
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

    # for status, total in total_status.items():
    #     data.append({
    #         'ID Transaksi': 'Total',
    #         'Nama Pengguna': '',
    #         'Layanan Pembayaran': '',
    #         'Harga Awal': '',
    #         'Diskon Nama': '',
    #         'Diskon (%)': '',
    #         'Status Transaksi': status.capitalize(),
    #         'Harga Akhir': total,
    #         'Waktu Transaksi': '',
    #     })

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

    filters = Q()
    if dari_tanggal:
        filters &= Q(created_at__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(created_at__lte=sampai_tanggal)

    tarif_data = Tarif.objects.filter(filters).prefetch_related('diskon_set') if filters else Tarif.objects.prefetch_related('diskon_set').all()

    data = []
    for tarif in tarif_data:
        presentase_diskon = [diskon.persentase_diskon for diskon in tarif.diskon_set.all()]

        tanggal_dibuat = tarif.created_at.astimezone().strftime("%d %b. %Y")

        data.append({
            'Nama Tarif': tarif.subject,
            'Harga': tarif.harga,
            'Sedang Digunakan': "Ya" if tarif.is_used else "Tidak",
            'Jumlah Presentase Diskon': presentase_diskon if len(presentase_diskon)>0 else "Tidak ada diskon",
            'Tanggal Dibuat': tanggal_dibuat,
        })

    df = pd.DataFrame(data)

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

    filters = Q()
    if dari_tanggal:
        filters &= Q(created_at__gte=dari_tanggal)
    if sampai_tanggal:
        filters &= Q(created_at__lte=sampai_tanggal)

    tarif_data = Tarif.objects.filter(filters).prefetch_related('diskon_set') if filters else Tarif.objects.prefetch_related('diskon_set').all()

    data = []
    for tarif in tarif_data:
        presentase_diskon = [diskon.persentase_diskon for diskon in tarif.diskon_set.all()]

        tanggal_dibuat = tarif.created_at.astimezone().strftime("%d %b. %Y")

        data.append({
            'Nama Tarif': tarif.subject,
            'Harga': tarif.harga,
            'Sedang Digunakan': "Ya" if tarif.is_used else "Tidak",
            'Jumlah Presentase Diskon': presentase_diskon if len(presentase_diskon) > 0 else "Tidak ada diskon",
            'Tanggal Dibuat': tanggal_dibuat,
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Tarif.csv'
    
    df.to_csv(path_or_buf=response, index=False, encoding='utf-8')

    return response

@login_required(login_url='user:masuk')
@admin_required
def export_data_pelanggan_excel(request):
    profiles = Profile.objects.all()
    data = []
    for profile in profiles:
        data.append({
            'Nama Lengkap': profile.nama_lengkap,
            'Jenis Kelamin': profile.get_jenis_kelamin_display() if profile.jenis_kelamin else 'Tidak diisi',
            'Tempat Tinggal': profile.tempat_tinggal if profile.tempat_tinggal else 'Tidak diisi',
            'Nomor Telepon': profile.nomor_telepon if profile.nomor_telepon else 'Tidak diisi',
            'Tanggal Lahir': profile.tanggal_lahir.strftime('%d %b. %Y') if profile.tanggal_lahir else 'Tidak diisi',
            'Role': profile.user.role,
            'Tanggal Bergabung': profile.user.date_joined.strftime('%d %b. %Y') if profile.user else 'Tidak diisi',
            'Last Login': profile.user.last_login.strftime('%d %b. %Y %H:%M:%S') if profile.user.last_login else 'Belum pernah login',
            'Created At': profile.user.date_joined.strftime('%d %b. %Y') if profile.user else 'Tidak diisi',
        })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Data_Pelanggan.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Data Pelanggan', index=False)

    return response


@login_required(login_url='user:masuk')
@admin_required
def export_data_pelanggan_csv(request):
    profiles = Profile.objects.all()
    data = []
    for profile in profiles:
        data.append({
            'Nama Lengkap': profile.nama_lengkap,
            'Jenis Kelamin': profile.get_jenis_kelamin_display() if profile.jenis_kelamin else 'Tidak diisi',
            'Tempat Tinggal': profile.tempat_tinggal if profile.tempat_tinggal else 'Tidak diisi',
            'Nomor Telepon': profile.nomor_telepon if profile.nomor_telepon else 'Tidak diisi',
            'Tanggal Lahir': profile.tanggal_lahir.strftime('%d %b. %Y') if profile.tanggal_lahir else 'Tidak diisi',
            'Role': profile.user.role if profile.user else 'Tidak diisi',
            'Tanggal Bergabung': profile.user.date_joined.strftime('%d %b. %Y') if profile.user else 'Tidak diisi',
            'Last Login': profile.user.last_login.strftime('%d %b. %Y %H:%M:%S') if profile.user.last_login else 'Belum pernah login',
            'Created At': profile.user.date_joined.strftime('%d %b. %Y') if profile.user else 'Tidak diisi',
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Data_Pelanggan.csv'
    df.to_csv(path_or_buf=response, index=False, encoding='utf-8')
    return response


@login_required(login_url='user:masuk')
@admin_pemateri_required
def export_data_mapel_excel(request):
    mata_pelajaran = MataPelajaran.objects.select_related('level_study').all()
    
    data = []
    for mp in mata_pelajaran:
        data.append({
            'Nama Mata Pelajaran': mp.nama_mapel,
            'Level Studi': mp.level_study.level_study,
            'Dibuat Pada': mp.created_at.strftime('%d %b. %Y'),
            'Diupdate Pada': mp.updated_at.strftime('%d %b. %Y'),
        })
    
    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Mata_Pelajaran.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Mata Pelajaran', index=False)

    return response

@login_required(login_url='user:masuk')
@admin_pemateri_required
def export_data_mapel_csv(request):
    mata_pelajaran = MataPelajaran.objects.select_related('level_study').all()
    data = []
    for mp in mata_pelajaran:
        data.append({
            'Nama Mata Pelajaran': mp.nama_mapel,
            'Level Studi': mp.level_study.level_study,
            'Dibuat Pada': mp.created_at.strftime('%d %b. %Y'),
            'Diupdate Pada': mp.updated_at.strftime('%d %b. %Y'),
        })
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Laporan_Mata_Pelajaran.csv'
    df.to_csv(path_or_buf=response, index=False, encoding='utf-8')
    return response