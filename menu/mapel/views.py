from django.shortcuts import render, redirect,get_object_or_404
from .models import MataPelajaran
from menu.pembayaran.models import Transaksi
from config import midtrans
from django.contrib.auth.decorators import login_required
from .forms import MapelForm
from core.utils.decorator import admin_pemateri_required
from django.contrib import messages
from django.db.models import ProtectedError
from django.core.exceptions import ValidationError
from menu.levelstudy.models import LevelStudy

# Create your views here.

MIDTRANS_CORE = midtrans.MIDTRANS_CORE
PAYMENT_STATUS = midtrans.PAYMENT_STATUS


@login_required(login_url='user:masuk')
@admin_pemateri_required
def levelstudy_mapel(request):
    levelstudy_objs = LevelStudy.objects.all()
    context = {
        'levelstudy_objs': levelstudy_objs,
    }
    return render(request, 'mapel/levelstudy_mapel.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def mapel(request,id_levelstudy):
    mapel_objs = MataPelajaran.objects.filter(level_study__pk=id_levelstudy)
    context = {
        'mapel_objs': mapel_objs,
        'id_levelstudy':id_levelstudy,
    }
    return render(request, 'mapel/mapel.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapus_mapel(request,id_levelstudy, id_mapel):
    try:
        mapel_obj = MataPelajaran.objects.get(pk=id_mapel,level_study__pk=id_levelstudy)
        mapel_obj.delete()
        messages.success(request, f"Selamat, mata pelajaran {mapel_obj.nama_mapel} berhasil dihapus.")
    except MataPelajaran.DoesNotExist:
        messages.error(request, "Mata pelajaran tidak ditemukan.")
    except ProtectedError:
        messages.error(request, f"Mata pelajaran {mapel_obj.nama_mapel} tidak dapat dihapus karena masih digunakan oleh objek nilai.")
    
    return redirect("menu:mapel",id_levelstudy=id_levelstudy)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_mapel(request, id_levelstudy):
    levelstudy_obj = get_object_or_404(LevelStudy, pk=id_levelstudy)
    if request.method == "POST":
        mapel_forms = MapelForm(request.POST)
        if mapel_forms.is_valid():
            nama_mapel = mapel_forms.cleaned_data['nama_mapel']
            description = mapel_forms.cleaned_data['description']
            try:
                mapel_obj = MataPelajaran(
                    nama_mapel=nama_mapel,
                    description=description,
                    level_study=levelstudy_obj,
                )
                mapel_obj.full_clean()
                mapel_obj.save()
                messages.success(request, f"Selamat mata pelajaran {nama_mapel} berhasil ditambahkan")
                return redirect("menu:mapel", id_levelstudy=id_levelstudy)
            except ValidationError:
                mapel_forms.add_error(None, f"Mata pelajaran dengan nama {nama_mapel} telah dibuat untuk level studi ini.")
                
    else:
        mapel_forms = MapelForm()
    
    context = {
        "mapel_forms": mapel_forms,
        "id_levelstudy": id_levelstudy,
    }
    return render(request, 'mapel/tambah_mapel.html', context)


@login_required(login_url='user:masuk')
@admin_pemateri_required
def edit_mapel(request, id_levelstudy, id_mapel):
    mapel_obj = get_object_or_404(MataPelajaran, pk=id_mapel, level_study__pk=id_levelstudy)
    
    if request.method == "POST":
        mapel_forms = MapelForm(request.POST, instance=mapel_obj)
        if mapel_forms.is_valid():
            try:
                # Manually trigger validation to catch unique_together constraint
                mapel_obj = mapel_forms.save(commit=False)
                mapel_obj.full_clean()  # This will raise a ValidationError if unique_together is violated
                mapel_obj.save()
                messages.success(request, f"Selamat mata pelajaran {mapel_obj.nama_mapel} berhasil di-edit")
                return redirect("menu:mapel", id_levelstudy=id_levelstudy)
            except ValidationError as e:
                mapel_forms.add_error(None,f"Mata pelajaran dengan nama {mapel_obj.nama_mapel} telah dibuat untuk level studi ini.")
    else:
        mapel_forms = MapelForm(instance=mapel_obj)
    
    context = {
        "mapel_obj": mapel_obj,
        "mapel_forms": mapel_forms,
    }
    return render(request, 'mapel/edit_mapel.html', context)