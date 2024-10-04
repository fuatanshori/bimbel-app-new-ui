from django.shortcuts import render, redirect
from django.http import Http404
from django.http import JsonResponse
from .models import MataPelajaran
from .models import Modul
from menu.levelstudy.models import LevelStudy
from config import midtrans
from django.contrib.auth.decorators import login_required
import os
from django.contrib import messages
from .forms import ModulForm
from core.utils.decorator import admin_pemateri_required,transaksi_settlement_required
from menu.utils.encode_url import decode_id
from menu.utils.pagination import pagination_queryset


# Create your views here.
MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS


@login_required(login_url='user:masuk')
@transaksi_settlement_required
def modul_levelstudy(request):
    levelstudy_objs = LevelStudy.objects.all()
    context = {
        'levelstudy_objs': levelstudy_objs,
    }
    return render(request, 'modul/modul_levelstudy.html', context)


@login_required(login_url='user:masuk')
@transaksi_settlement_required
def modul_mapel(request,id_levelstudy):
    pk =decode_id(id_levelstudy)
    mapel_objs = MataPelajaran.objects.filter(level_study__pk=pk)
    context = {
        'mapel_objs': mapel_objs,
        "id_levelstudy":id_levelstudy
    }
    return render(request, 'modul/modul_mapel.html', context)


@login_required(login_url='user:masuk')
@transaksi_settlement_required
def daftar_modul(request,id_levelstudy, id_mapel):
    pk = decode_id(id_mapel)
    custom_range,modul_objs = pagination_queryset(request,Modul.objects.filter(mata_pelajaran__pk=pk),5)
    context = {
        'id_mapel':id_mapel,
        'modul_objs': modul_objs,
        'custom_range':custom_range,
        "id_levelstudy":id_levelstudy
    }
    return render(request, 'modul/daftar_modul.html', context)

@login_required(login_url="user:masuk")
@transaksi_settlement_required
def detailmodul(request,id_levelstudy,id_mapel,id_modul):
    pk_mapel=decode_id(id_mapel)
    pk_modul=decode_id(id_modul)

    try:
        modul_obj = Modul.objects.get(pk=pk_modul,mata_pelajaran__pk=pk_mapel)
    except Modul.DoesNotExist:
        raise Http404
    context = {
        "modul_obj":modul_obj,
        "id_mapel":id_mapel,
        "id_levelstudy":id_levelstudy,
    }
    return render(request,'modul/detail_modul.html',context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapusModul(request,id_levelstudy,id_mapel, id_modul):
    pk_mapel = decode_id(id_mapel)
    pk_modul = decode_id(id_modul)
    try:
        modul_obj = Modul.objects.get(pk=pk_modul)
    except Modul.DoesNotExist:
        return redirect("menu:daftar-modul",id_levelstudy=id_levelstudy,id_mapel=pk_mapel)
    if modul_obj.modul:
        if os.path.isfile(modul_obj.modul.path):
           os.remove(modul_obj.modul.path)
    if modul_obj.vidio:
        if os.path.isfile(modul_obj.vidio.path):
           os.remove(modul_obj.vidio.path)
    messages.success(request,f"selamat modul {modul_obj.nama_modul} berhasil dihapus")
    modul_obj.delete()
    return redirect('menu:daftar-modul',id_levelstudy=id_levelstudy, id_mapel=id_mapel)


@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_modul(request,id_levelstudy,id_mapel):
    if request.method == "POST":
        pk = decode_id(id_mapel)
        try:
            mapel_obj = MataPelajaran.objects.get(pk=pk)
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
                "id_mapel":id_mapel,
                "id_levelstudy":id_levelstudy,
            })
        else:
           
            error_message = ', '.join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            return JsonResponse({"message": error_message}, status=400)
            
    modul_forms = ModulForm(request.POST or None,request.FILES or None)
    context={
        "modul_forms": modul_forms,
        "id_mapel": id_mapel,
        "id_levelstudy":id_levelstudy,
    }
    return render(request, 'modul/tambah_modul.html',context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def edit_modul(request,id_levelstudy, id_mapel, id_modul):
    pk_modul = decode_id(id_modul)
    if request.user.role not in ["pemateri", "admin"]:
        return redirect("menu:daftar-modul", id_mapel=id_mapel)
    modul_obj = Modul.objects.get(pk=pk_modul)
    if request.method == "POST":
        modul_forms = ModulForm(request.POST, request.FILES, instance=modul_obj)  
        if modul_forms.is_valid():
            modul_forms.save()
            messages.success(request,f"selamat modul {modul_obj.nama_modul} berhasil di edit")
            return JsonResponse({
                "message": "data uploaded",
                "id_mapel": id_mapel,
                "id_levelstudy": id_levelstudy,
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
        "id_modul": id_modul,
        "id_levelstudy": id_levelstudy,
    }
    return render(request, 'modul/edit_modul.html', context)
