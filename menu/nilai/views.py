from django.shortcuts import render,redirect,get_object_or_404
from django.http import Http404
from menu.nilai.models import Nilai
from menu.mapel.models import MataPelajaran
from menu.levelstudy.models import LevelStudy
from django.contrib.auth.decorators import login_required
from core.utils.decorator import transaksi_settlement_required
from menu.utils.encode_url import decode_id
import qrcode
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
from django.conf import settings
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from user.models import Profile
from menu.nilai.models import Sertifikat
from menu.utils.encode_url import decode_id
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

# Create your views here.

@login_required(login_url='user:masuk')
@transaksi_settlement_required
def daftar_nilai(request):
    try:
        if request.user.role in ['pemateri',"admin"]:
            nilai_objs = Nilai.objects.all().select_related('sertifikat')
        else:
            nilai_objs = Nilai.objects.filter(user=request.user).select_related('sertifikat')

    except Nilai.DoesNotExist:
        pass
    levelstudy_objs = LevelStudy.objects.all()
    context = {
        "nilai_objs": nilai_objs,
        "levelstudy_objs":levelstudy_objs,
    }
    return render(request, 'nilai/nilai.html', context)

@login_required(login_url='user:masuk')
def lakukan_ujian_ulang(request,id_mapel,id_nilai):
    pk_mapel = decode_id(id_mapel)
    pk_nilai = decode_id(id_nilai)
    try:
        mapel_obj = MataPelajaran.objects.get(pk=pk_mapel)
        if request.user.role == "pemateri" or request.user.role == "admin":
            nilai_obj = Nilai.objects.get(pk=pk_nilai,status="tidak lulus",mata_pelajaran=mapel_obj)
            nilai_obj.delete()
            return redirect("menu:daftar-nilai")
        elif request.user.role == "pelajar":
            nilai_obj = Nilai.objects.get(pk=pk_nilai,status="tidak lulus",mata_pelajaran=mapel_obj,user=request.user)
            nilai_obj.delete()
            return redirect("menu:ujian",id_mapel=id_mapel)
    except MataPelajaran.DoesNotExist:
        raise Http404()
    except Nilai.DoesNotExist:
        raise Http404()

@login_required(login_url='user:masuk')
@transaksi_settlement_required
def daftar_nilai_perlevelstudy(request,id_levelstudy):
    pk = decode_id(id_levelstudy)
    try:
        if request.user.role in ['pemateri',"admin"]:
            nilai_objs = Nilai.objects.filter(mata_pelajaran_obj__level_study__pk=pk).select_related('sertifikat')
        else:
            nilai_objs = Nilai.objects.filter(user=request.user,mata_pelajaran_obj__level_study__pk=pk).select_related('sertifikat')

    except Nilai.DoesNotExist:
        pass
    levelstudy_objs = LevelStudy.objects.all()
    level_study = get_object_or_404(LevelStudy,pk=pk).level_study
    context = {
        "nilai_objs": nilai_objs,
        "levelstudy_objs":levelstudy_objs,
        "level_study":level_study,
        "id_levelstudy":id_levelstudy
    }
    return render(request, 'nilai/nilai.html', context)


def generate_certificate(request,id_sertifikat):
    sertifikat_obj = get_object_or_404(Sertifikat,pk=decode_id(id_sertifikat))
    
    BASE_DIR = settings.BASE_DIR
    image_path = BASE_DIR / 'cert_generator/sertifikat_template.png'

    certificate_image = Image.open(image_path)
    image_width, image_height = certificate_image.size

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=(image_width, image_height))

    pdf.drawImage(image_path, 0, 0, width=image_width, height=image_height)

    font_path1 = BASE_DIR / 'cert_generator/font/LeagueSpartan-Bold.ttf'
    font_path2 = BASE_DIR / 'cert_generator/font/LeagueSpartan-Medium.ttf'
    font_path3 = BASE_DIR / 'cert_generator/font/LeagueSpartan-Regular.ttf'
    pdfmetrics.registerFont(TTFont('LeagueSpartan-Bold', font_path1))
    pdfmetrics.registerFont(TTFont('LeagueSpartan-Medium', font_path2))
    pdfmetrics.registerFont(TTFont('LeagueSpartan-Regular', font_path3))

    nama = str(sertifikat_obj.nama).upper()
    id_cert = str(sertifikat_obj.pk).upper()
    tingkat_studi = sertifikat_obj.tingkat_studi.upper()
    mata_pelajaran = sertifikat_obj.mata_pelajaran.upper()
    predikat = sertifikat_obj.predikat.upper()
    nilai = sertifikat_obj.nilai
    tanggal_lahir = sertifikat_obj.tanggal_lahir
    tanggal_dibuat = sertifikat_obj.created_at

    positions = {
        "nama": (image_width / 2, 620),
        "id_sertifikat": (550, 770),
        "tingkat_studi": (550, 830),
        "mata_pelajaran": (550, 890),
        "predikat": (550, 950),
        "nilai": (550, 1010),
        "tanggal_lahir": (550, 1070),
        "tanggal_dibuat": (550, 1130),
    }

    pdf.setFont("LeagueSpartan-Bold", 100)

    nama_width = pdf.stringWidth(nama, "LeagueSpartan-Bold", 100)
    nama_x_position = (image_width - nama_width) / 2 

    pdf.drawString(nama_x_position, image_height - positions['nama'][1], nama)

    pdf.setFont("LeagueSpartan-Regular", 32)

    pdf.drawString(positions['id_sertifikat'][0], image_height - positions['id_sertifikat'][1], "ID SERTIFIKAT")
    pdf.drawString(positions['tingkat_studi'][0], image_height - positions['tingkat_studi'][1], "TINGKAT STUDI")
    pdf.drawString(positions['mata_pelajaran'][0], image_height - positions['mata_pelajaran'][1], "MATA PELAJARAN")
    pdf.drawString(positions['predikat'][0], image_height - positions['predikat'][1], "PREDIKAT")
    pdf.drawString(positions['nilai'][0], image_height - positions['nilai'][1], "NILAI")
    pdf.drawString(positions['tanggal_lahir'][0], image_height - positions['tanggal_lahir'][1], "TANGGAL LAHIR")
    pdf.drawString(positions['tanggal_dibuat'][0], image_height - positions['tanggal_dibuat'][1], "TANGGAL DIBUAT")

    pdf.drawString(860, image_height - positions['id_sertifikat'][1], ":")
    pdf.drawString(860, image_height - positions['tingkat_studi'][1], ":")
    pdf.drawString(860, image_height - positions['mata_pelajaran'][1], ":")
    pdf.drawString(860, image_height - positions['predikat'][1], ":")
    pdf.drawString(860, image_height - positions['nilai'][1], ":")
    pdf.drawString(860, image_height - positions['tanggal_lahir'][1], ":")
    pdf.drawString(860, image_height - positions['tanggal_dibuat'][1], ":")
 
    pdf.drawString(880, image_height - positions['id_sertifikat'][1], f"{id_cert}")
    pdf.drawString(880, image_height - positions['tingkat_studi'][1], f"{tingkat_studi}")
    pdf.drawString(880, image_height - positions['mata_pelajaran'][1], f"{mata_pelajaran}")
    pdf.drawString(880, image_height - positions['predikat'][1], f"{predikat}")
    pdf.drawString(880, image_height - positions['nilai'][1], f"{nilai}")
    pdf.drawString(880, image_height - positions['tanggal_lahir'][1], f"{tanggal_lahir}")
    pdf.drawString(880, image_height - positions['tanggal_dibuat'][1], f"{tanggal_dibuat}")

    domain = get_current_site(request).domain
    endpoint = reverse("menu:generate-certificate",args=[id_sertifikat])
    protocol = request.scheme
    qr_data = f"{protocol}://{domain}{endpoint}"
    qr_code_image = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_code_image.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)

    qr_code_position = (50, 50)
    qr_code_size = 150 

    pdf.drawImage(qr_image, qr_code_position[0], qr_code_position[1], qr_code_size, qr_code_size)
     
    pdf.save()

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filenama="certificate_with_qr.pdf"'

    return response


def search_certificate(request):
    id_sertifikat = request.GET.get('id_sertifikat')
    try:
        sertifikat_obj = Sertifikat.objects.get(pk__iexact=id_sertifikat)
    except Sertifikat.DoesNotExist:
        raise Http404()
    
    BASE_DIR = settings.BASE_DIR
    image_path = BASE_DIR / 'cert_generator/sertifikat_template.png'

    certificate_image = Image.open(image_path)
    image_width, image_height = certificate_image.size

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=(image_width, image_height))

    pdf.drawImage(image_path, 0, 0, width=image_width, height=image_height)

    font_path1 = BASE_DIR / 'cert_generator/font/LeagueSpartan-Bold.ttf'
    font_path2 = BASE_DIR / 'cert_generator/font/LeagueSpartan-Medium.ttf'
    font_path3 = BASE_DIR / 'cert_generator/font/LeagueSpartan-Regular.ttf'
    pdfmetrics.registerFont(TTFont('LeagueSpartan-Bold', font_path1))
    pdfmetrics.registerFont(TTFont('LeagueSpartan-Medium', font_path2))
    pdfmetrics.registerFont(TTFont('LeagueSpartan-Regular', font_path3))

    nama = str(sertifikat_obj.nama).upper()
    id_cert = str(sertifikat_obj.pk).upper()
    tingkat_studi = sertifikat_obj.tingkat_studi
    mata_pelajaran = sertifikat_obj.mata_pelajaran
    predikat = sertifikat_obj.predikat
    nilai = sertifikat_obj.nilai
    tanggal_lahir = sertifikat_obj.tanggal_lahir
    tanggal_dibuat = sertifikat_obj.created_at

    positions = {
        "nama": (image_width / 2, 620),
        "id_sertifikat": (550, 770),
        "tingkat_studi": (550, 830),
        "mata_pelajaran": (550, 890),
        "predikat": (550, 950),
        "nilai": (550, 1010),
        "tanggal_lahir": (550, 1070),
        "tanggal_dibuat": (550, 1130),
    }

    pdf.setFont("LeagueSpartan-Bold", 100)

    nama_width = pdf.stringWidth(nama, "LeagueSpartan-Bold", 100)
    nama_x_position = (image_width - nama_width) / 2 

    pdf.drawString(nama_x_position, image_height - positions['nama'][1], nama)

    pdf.setFont("LeagueSpartan-Regular", 32)

    pdf.drawString(positions['id_sertifikat'][0], image_height - positions['id_sertifikat'][1], "ID SERTIFIKAT")
    pdf.drawString(positions['tingkat_studi'][0], image_height - positions['tingkat_studi'][1], "TINGKAT STUDI")
    pdf.drawString(positions['mata_pelajaran'][0], image_height - positions['mata_pelajaran'][1], "MATA PELAJARAN")
    pdf.drawString(positions['predikat'][0], image_height - positions['predikat'][1], "PREDIKAT")
    pdf.drawString(positions['nilai'][0], image_height - positions['nilai'][1], "NILAI")
    pdf.drawString(positions['tanggal_lahir'][0], image_height - positions['tanggal_lahir'][1], "TANGGAL LAHIR")
    pdf.drawString(positions['tanggal_dibuat'][0], image_height - positions['tanggal_dibuat'][1], "TANGGAL DIBUAT")

    pdf.drawString(860, image_height - positions['id_sertifikat'][1], ":")
    pdf.drawString(860, image_height - positions['tingkat_studi'][1], ":")
    pdf.drawString(860, image_height - positions['mata_pelajaran'][1], ":")
    pdf.drawString(860, image_height - positions['predikat'][1], ":")
    pdf.drawString(860, image_height - positions['nilai'][1], ":")
    pdf.drawString(860, image_height - positions['tanggal_lahir'][1], ":")
    pdf.drawString(860, image_height - positions['tanggal_dibuat'][1], ":")
 
    pdf.drawString(880, image_height - positions['id_sertifikat'][1], f"{id_cert}")
    pdf.drawString(880, image_height - positions['tingkat_studi'][1], f"{tingkat_studi}")
    pdf.drawString(880, image_height - positions['mata_pelajaran'][1], f"{mata_pelajaran}")
    pdf.drawString(880, image_height - positions['predikat'][1], f"{predikat}")
    pdf.drawString(880, image_height - positions['nilai'][1], f"{nilai}")
    pdf.drawString(880, image_height - positions['tanggal_lahir'][1], f"{tanggal_lahir}")
    pdf.drawString(880, image_height - positions['tanggal_dibuat'][1], f"{tanggal_dibuat}")

    domain = get_current_site(request).domain
    endpoint = reverse("menu:generate-certificate",args=[id_sertifikat])
    qr_data = f"http://{domain}{endpoint}"
    qr_code_image = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr_code_image.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)

    qr_code_position = (50, 50)
    qr_code_size = 150 

    pdf.drawImage(qr_image, qr_code_position[0], qr_code_position[1], qr_code_size, qr_code_size)
     
    pdf.save()

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filenama="certificate_with_qr.pdf"'

    return response
