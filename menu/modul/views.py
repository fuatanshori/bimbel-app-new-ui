from django.shortcuts import render, redirect
from django.http import Http404
from django.http import JsonResponse
from .models import MataPelajaran
from .models import Modul
from menu.levelstudy.models import LevelStudy
from menu.pembayaran.models import Transaksi
from config import midtrans
from django.contrib.auth.decorators import login_required
import os
from django.contrib import messages
from .forms import ModulForm
from core.utils.decorator import admin_pemateri_required


# Create your views here.
MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS


@login_required(login_url='user:masuk')
def modul_levelstudy(request):
    levelstudy_objs = LevelStudy.objects.all()
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    
    context = {
        'levelstudy_objs': levelstudy_objs,
    }
    return render(request, 'modul/modul_levelstudy.html', context)


@login_required(login_url='user:masuk')
def modul_mapel(request,id_levelstudy):
    mapel_objs = MataPelajaran.objects.filter(level_study__pk=id_levelstudy)
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    
    context = {
        'mapel_objs': mapel_objs,
    }
    return render(request, 'modul/modul_mapel.html', context)


@login_required(login_url='user:masuk')
def daftar_modul(request, id_mapel):
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    
    modul_objs = Modul.objects.filter(mata_pelajaran__pk=id_mapel)
    context = {
        'id_mapel':id_mapel,
        'modul_objs': modul_objs,
    }
    return render(request, 'modul/daftar_modul.html', context)


@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapusModul(request,id_mapel, id_modul):
    try:
        modul_obj = Modul.objects.get(pk=id_modul)
    except Modul.DoesNotExist:
        return redirect("menu:daftar-modul",id_mapel=id_mapel)
    if modul_obj.modul:
        if os.path.isfile(modul_obj.modul.path):
           os.remove(modul_obj.modul.path)
    messages.success(request,f"selamat modul {modul_obj.nama_modul} berhasil dihapus")
    modul_obj.delete()
    return redirect('menu:daftar-modul', id_mapel=modul_obj.mata_pelajaran.pk)


@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_modul(request,id_mapel):
    if request.method == "POST":
        try:
            mapel_obj = MataPelajaran.objects.get(pk=id_mapel)
        except MataPelajaran.DoesNotExist:
            return JsonResponse({
                "message":"data not a valid",
            })
        modul_forms = ModulForm(request.POST,request.FILES)
        if modul_forms.is_valid():
            nama_modul = modul_forms.cleaned_data['nama_modul']
            description = modul_forms.cleaned_data['description']
            vidio = modul_forms.cleaned_data['vidio']
            modul = modul_forms.cleaned_data['modul']
            Modul.objects.create(
                nama_modul = nama_modul,
                description=description,
                modul = modul,
                mata_pelajaran = mapel_obj,
                author = request.user,
                vidio=vidio,
            ).save()
            messages.success(request,f"selamat modul {nama_modul} berhasil di tambahkan")
            return JsonResponse({
                "message":"data uploaded",
                "id_mapel":id_mapel
            })
        else:
            return JsonResponse({
                "message":modul_forms.errors.as_text()
            })
    modul_forms = ModulForm(request.POST or None,request.FILES or None)
    context={
        "modul_forms": modul_forms,
        "id_mapel": id_mapel
    }
    return render(request, 'modul/tambah_modul.html',context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def edit_modul(request, id_mapel, id_modul):
    if request.user.role not in ["pemateri", "admin"]:
        return redirect("menu:daftar-modul", id_mapel=id_mapel)

    modul_obj = Modul.objects.get(pk=id_modul)
    
    if request.method == "POST":
        modul_forms = ModulForm(request.POST, request.FILES, instance=modul_obj)
        if modul_forms.is_valid():
            modul_forms.save()
            messages.success(request,f"selamat modul {modul_obj.nama_modul} berhasil di edit")
            return JsonResponse({
                "message": "data uploaded",
                "id_mapel": id_mapel
            })
        else:
            return JsonResponse({
                "message": modul_forms.errors.as_text()
            })
    else:
        modul_forms = ModulForm(instance=modul_obj)
    
    context = {
        "modul_forms": modul_forms,
        "id_mapel": id_mapel,
        "id_modul": id_modul
    }
    return render(request, 'modul/edit_modul.html', context)

@login_required(login_url="user:masuk")
def detailmodul(request,id_mapel,id_modul):
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    try:
        modul_obj = Modul.objects.get(pk=id_modul,mata_pelajaran__pk=id_mapel)
    except Modul.DoesNotExist:
        raise Http404
    context = {
        "modul_obj":modul_obj
    }
    return render(request,'modul/detail_modul.html',context)