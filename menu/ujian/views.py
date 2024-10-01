from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from .models import MataPelajaran
from menu.pembayaran.models import Transaksi
from config import midtrans
from django.contrib.auth.decorators import login_required
import os
from .forms import SoalUjianForm
from .models import SoalUjian,Nilai,Sertifikat
import random

from django.conf import settings
import datetime
import uuid
from menu.levelstudy.models import LevelStudy
from core.utils.decorator import admin_pemateri_required,transaksi_settlement_required
from menu.utils.encode_url import decode_id
from menu.utils.pagination import pagination_queryset
from django.contrib import messages


MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS



@login_required(login_url='user:masuk')
@transaksi_settlement_required
def levelstudy_ujian(request):
    levelstudy_objs = LevelStudy.objects.all()
    context = {
        'levelstudy_objs': levelstudy_objs,
    }
    return render(request, 'ujian/levelstudy_ujian.html', context)

@login_required(login_url='user:masuk')
@transaksi_settlement_required
def ujian_mapel(request,id_levelstudy):
    pk = decode_id(id_levelstudy)
    mapel_objs = MataPelajaran.objects.filter(level_study__pk=pk)
    context = {
        'mapel_objs': mapel_objs,
        
    }
    return render(request, 'ujian/ujian_mapel.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def daftar_ujian_admin_pemateri(request, id_mapel):
    pk = decode_id(id_mapel)
    try:
        custom_range,soal_ujian_objs = pagination_queryset(request,SoalUjian.objects.filter(mata_pelajaran__pk=pk),5)
        mapel_objs = MataPelajaran.objects.get(pk=pk)
    except SoalUjian.DoesNotExist:
        return HttpResponse("404 soal tidak ditemukan")
    except MataPelajaran.DoesNotExist:
        return HttpResponse("404 mata pelajaran kosong")

    context = {
        'id_mapel':id_mapel,
        'soal_ujian_objs': soal_ujian_objs,
        'mapel':mapel_objs,
        "custom_range":custom_range,
    }
    return render(request, 'ujian/daftar_ujian_admin.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapusSoalUjian(request,id_mapel, id_soal_ujian):
    try:
        pk = decode_id(id_soal_ujian)
        soal_ujian_obj = get_object_or_404(SoalUjian,pk=pk)
    except SoalUjian.DoesNotExist:
        return redirect("menu:daftar-ujian-admin-pemateri",id_mapel=id_mapel)
   
    soal_ujian_obj.delete()
    messages.success(request,"berhasil dihapus")
    return redirect('menu:daftar-ujian-admin-pemateri', id_mapel=id_mapel)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_ujian(request,id_mapel):
    if request.method == "POST":
        pk = decode_id(id_mapel)
        mapel_obj = MataPelajaran.objects.get(pk=pk)
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
    pk = decode_id(id_soal_ujian)
    soal_ujian_obj = SoalUjian.objects.get(pk=pk)
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


@login_required(login_url='user:masuk')
@admin_pemateri_required
def detail_ujian(request, id_mapel, id_soal_ujian):
    pk = decode_id(id_soal_ujian)
    soal_ujian_obj = get_object_or_404(SoalUjian,pk=pk)
    context={
        "id_mapel": id_mapel,
        "soal_ujian_obj":soal_ujian_obj
    }
    return render(request, 'ujian/detail_ujian.html',context)

@login_required(login_url='user:masuk')
@transaksi_settlement_required
def ujian(request,id_mapel):
    pk = decode_id(id_mapel)
    try:
        mapel_obj = MataPelajaran.objects.get(pk=pk)
        nilai = Nilai.objects.get(user=request.user,mata_pelajaran=mapel_obj)
        return redirect("menu:nilai-setelah-ujian",id_mapel=id_mapel,id_nilai=nilai.get_id_safe())
    except Nilai.DoesNotExist:
        pass
    except MataPelajaran.DoesNotExist:
        return HttpResponse("Mata pelajaran tidak ditemukan")

    if request.method == "POST":
        soal_ujian_objs = SoalUjian.objects.filter(mata_pelajaran__pk=pk)
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
            cert_obj = Sertifikat.objects.create(
                nilai=nilai_obj
            )
            cert_obj.save()

        return redirect("menu:nilai-setelah-ujian",id_mapel=id_mapel,id_nilai=nilai_obj.get_id_safe())

    soal_ujian_objs_lists = list(SoalUjian.objects.filter(mata_pelajaran__pk=pk))
    if len(soal_ujian_objs_lists)==0:
        return HttpResponse("soal ujian belum dibuat")
    random.shuffle((soal_ujian_objs_lists))
    
    context = {
        'id_mapel':id_mapel,
        'soal_ujian_objs':soal_ujian_objs_lists,
        'total_soal':SoalUjian.objects.filter(mata_pelajaran__pk=pk).count(),
        'mata_pelajaran': mapel_obj.nama_mapel,
    }
    return render(request,'ujian/ujian.html',context)

@login_required(login_url='user:masuk')
@transaksi_settlement_required
def nilai_setelah_ujian(request,id_mapel,id_nilai):
    pk_mapel = decode_id(id_mapel)
    pk_nilai = decode_id(id_nilai)
   
    mapel_obj = MataPelajaran.objects.get(pk=pk_mapel)
    try:
        nilai_obj = Nilai.objects.get(pk=pk_nilai,user=request.user)
    except Nilai.DoesNotExist:
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
            'sertifikat_obj':sertifikat_obj
        }
    return render(request,'ujian/nilai.html',context)