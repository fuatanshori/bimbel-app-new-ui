from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse
from .models import MataPelajaran
from menu.pembayaran.models import Transaksi
from config import midtrans
from django.contrib.auth.decorators import login_required
import os
from .forms import SoalUjianForm
from .models import SoalUjian,Nilai,Sertifikat
import random
from cert_generator.certificates import cert
from django.conf import settings
import datetime
import uuid
from menu.levelstudy.models import LevelStudy
from core.utils.decorator import admin_pemateri_required


# Create your views here.

MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS



@login_required(login_url='user:masuk')
def levelstudy_ujian(request):
    levelstudy_objs = LevelStudy.objects.all()
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    context = {
        'levelstudy_objs': levelstudy_objs,
    }
    return render(request, 'ujian/levelstudy_ujian.html', context)

@login_required(login_url='user:masuk')
def ujian_mapel(request,id_levelstudy):
    mapel_objs = MataPelajaran.objects.filter(level_study__pk=id_levelstudy)
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    context = {
        'mapel_objs': mapel_objs,
        
    }
    return render(request, 'ujian/ujian_mapel.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def daftar_ujian_admin_pemateri(request, id_mapel):
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    try:
        soal_ujian_objs = SoalUjian.objects.filter(mata_pelajaran__pk=id_mapel)
        mapel_objs = MataPelajaran.objects.get(pk=id_mapel)
    except SoalUjian.DoesNotExist:
        return HttpResponse("404 soal tidak ditemukan")
    except MataPelajaran.DoesNotExist:
        return HttpResponse("404 mata pelajaran kosong")

    context = {
        'id_mapel':id_mapel,
        'soal_ujian_objs': soal_ujian_objs,
        'mapel':mapel_objs
    }
    return render(request, 'ujian/daftar_ujian_admin.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapusSoalUjian(request,id_mapel, id_soal_ujian):
    try:
        soal_ujian_obj = SoalUjian.objects.get(pk=id_soal_ujian)
    except SoalUjian.DoesNotExist:
        return redirect("menu:daftar-ujian-admin-pemateri",id_mapel=id_mapel)
   
    soal_ujian_obj.delete()
    return redirect('menu:daftar-ujian-admin-pemateri', id_mapel=soal_ujian_obj.mata_pelajaran.pk)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_ujian(request,id_mapel):
    if request.method == "POST":
        mapel_obj = MataPelajaran.objects.get(pk=id_mapel)
        soal_ujian_forms = SoalUjianForm(request.POST,request.FILES)
        if soal_ujian_forms.is_valid():
            gambar_soal = soal_ujian_forms.cleaned_data['gambar_soal']
            soal = soal_ujian_forms.cleaned_data['soal']
            jawaban_1 = soal_ujian_forms.cleaned_data['jawaban_1']
            jawaban_2 = soal_ujian_forms.cleaned_data['jawaban_2']
            jawaban_3 = soal_ujian_forms.cleaned_data['jawaban_3']
            jawaban_4 = soal_ujian_forms.cleaned_data['jawaban_4']
            pilih_jawaban_benar = soal_ujian_forms.cleaned_data['pilih_jawaban_benar']
            
            SoalUjian.objects.create(
                gambar_soal=gambar_soal,
                soal=soal,
                jawaban_1=jawaban_1,
                jawaban_2=jawaban_2,
                jawaban_3=jawaban_3,
                jawaban_4=jawaban_4,
                pilih_jawaban_benar=pilih_jawaban_benar,
                mata_pelajaran = mapel_obj,
            ).save()
            return redirect("menu:daftar-ujian-admin-pemateri",id_mapel=id_mapel)
    soal_ujian_forms = SoalUjianForm(request.POST or None,request.FILES or None)
    context={
        "soal_ujian_forms": soal_ujian_forms,
        "id_mapel": id_mapel
    }
    return render(request, 'ujian/tambah_ujian.html',context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def edit_ujian(request, id_mapel, id_soal_ujian):
    soal_ujian_obj = SoalUjian.objects.get(pk=id_soal_ujian)
    if request.method == "POST":
        soal_ujian_forms = SoalUjianForm(request.POST , request.FILES ,instance=soal_ujian_obj)
        if soal_ujian_forms.is_valid():
            soal_ujian_forms.save()
            return redirect("menu:daftar-ujian-admin-pemateri",id_mapel=id_mapel)
    else:
        soal_ujian_forms = SoalUjianForm(instance=soal_ujian_obj)
    context={
        "soal_ujian_forms": soal_ujian_forms,
        "id_mapel": id_mapel,
        "id_soal_ujian":id_soal_ujian
    }
    return render(request, 'ujian/edit_ujian.html',context)


def ujian(request,id_mapel):
    try:
        status_transaksi=[]
        transaksi_obj = Transaksi.objects.get(
            user=request.user, transaksi_status="settlement")
        status_transaksi.append(PAYMENT_STATUS[transaksi_obj.transaksi_status])
    except Transaksi.DoesNotExist:
        if request.user.role == "admin" or request.user.role == "pemateri":
            status_transaksi = (None,)
        else:
            return redirect("menu:pembayaran")
        
    try:
        mapel_obj = MataPelajaran.objects.get(pk=id_mapel)
        nilai = Nilai.objects.get(user=request.user,mata_pelajaran=mapel_obj)
        return redirect("menu:nilai-setelah-ujian",id_mapel=id_mapel,id_nilai=nilai.pk)
    except Nilai.DoesNotExist:
        pass
    except MataPelajaran.DoesNotExist:
        return HttpResponse("Mata pelajaran tidak ditemukan")

    if request.method == "POST":
        soal_ujian_objs = SoalUjian.objects.filter(mata_pelajaran__pk=id_mapel)
        salah = 0
        benar = 0
        for soal_ujian_obj in soal_ujian_objs:
            if soal_ujian_obj.pilih_jawaban_benar == request.POST.get(soal_ujian_obj.soal):
                benar+=1
            else:
                salah+=1
        
        try:
            nilai = (benar/soal_ujian_objs.count())*100
        except ZeroDivisionError:
            nilai = 0

        if nilai >= 90:
            predikat = "A"
        elif nilai >= 80:
            predikat = "B+"
        elif nilai >= 70:
            predikat = "B"
        elif nilai >= 60:
            predikat = "B-"
        else:
            predikat = "C"
        
        status = "tidak lulus" if nilai <=60 else "lulus"
        nilai_obj = Nilai.objects.create(
            user = request.user,
            mata_pelajaran = mapel_obj,
            nilai = nilai,
            predikat=predikat,
            status = status,
        )
        nilai_obj.save()
        
        if status == "lulus":
            date=datetime.datetime.now().strftime("%d/%m/%Y")
            media_root = os.path.join(settings.MEDIA_ROOT)
            no_cert = cert(media_root=str(media_root),nama=str(request.user.full_name),
                            mata_pelajaran=str(mapel_obj.nama_mapel),date=date,no_cert=str(uuid.uuid4()),
                            request=request)
            cert_obj = Sertifikat.objects.create(
                no_cert=no_cert,
                nilai = nilai_obj,
                sertifikat = f"sertifikat/{no_cert}.png"
            )
            cert_obj.save()
        return redirect("menu:nilai-setelah-ujian",id_mapel=id_mapel,id_nilai=nilai_obj.pk)

    soal_ujian_objs_lists = list(SoalUjian.objects.filter(mata_pelajaran__pk=id_mapel))
    if len(soal_ujian_objs_lists)==0:
        return HttpResponse("soal ujian belum dibuat")
    random.shuffle((soal_ujian_objs_lists))
    
    context = {
        'id_mapel':id_mapel,
        'soal_ujian_objs':soal_ujian_objs_lists,
        'total_soal':SoalUjian.objects.filter(mata_pelajaran__pk=id_mapel).count(),
        'mata_pelajaran': mapel_obj.nama_mapel,
        'status_transaksi': status_transaksi[0],
    }
    return render(request,'ujian/ujian.html',context)

def nilai_setelah_ujian(request,id_mapel,id_nilai):
    try:
        status_transaksi=[]
        transaksi_obj = Transaksi.objects.get(
            user=request.user, transaksi_status="settlement")
        status_transaksi.append(PAYMENT_STATUS[transaksi_obj.transaksi_status])
    except Transaksi.DoesNotExist:
        if request.user.role == "admin" or request.user.role == "pemateri":
            status_transaksi = (None,)
        else:
            return redirect("menu:pembayaran")
    mapel_obj = MataPelajaran.objects.get(pk=id_mapel)
    try:
        nilai_obj = Nilai.objects.get(pk=id_nilai,user=request.user)
    except:
        return redirect("menu:ujian",id_mapel=id_mapel)
    try:
        sertifikat_obj = Sertifikat.objects.get(nilai=nilai_obj)
    except Sertifikat.DoesNotExist:
        sertifikat_obj= None
    context = {
            "nilai_obj":nilai_obj,
            "nilai":nilai_obj.nilai,
            "predikat":nilai_obj.predikat,
            "status":nilai_obj.status,
            'mapel':mapel_obj.nama_mapel,
            'status_transaksi': status_transaksi[0],
            'sertifikat_obj':sertifikat_obj
        }
    return render(request,'ujian/nilai.html',context)