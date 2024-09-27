from django.shortcuts import render,redirect
from django.http import Http404
from menu.ujian.models import Nilai
from menu.mapel.models import MataPelajaran
from menu.pembayaran.models import Transaksi
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required(login_url='user:masuk')
def daftar_nilai(request):
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    try:
        if request.user.role in ['pemateri',"admin"]:
            nilai_objs = Nilai.objects.all().select_related('sertifikat')
        else:
            nilai_objs = Nilai.objects.filter(user=request.user).select_related('sertifikat')

    except Nilai.DoesNotExist:
        pass
    mapel_objs = MataPelajaran.objects.all()
    context = {
        "nilai_objs": nilai_objs,
        "mapel_objs":mapel_objs,
    }
    return render(request, 'nilai/nilai.html', context)

@login_required(login_url='user:masuk')
def lakukan_ujian_ulang(request,id_mapel,id_nilai):
    try:
        mapel_obj = MataPelajaran.objects.get(pk=id_mapel)
        if request.user.role == "pemateri" or request.user.role == "admin":
            nilai_obj = Nilai.objects.get(pk=id_nilai,status="tidak lulus",mata_pelajaran=mapel_obj)
            nilai_obj.delete()
            return redirect("menu:daftar-nilai")
        elif request.user.role == "pelajar":
            nilai_obj = Nilai.objects.get(pk=id_nilai,status="tidak lulus",mata_pelajaran=mapel_obj,user=request.user)
            nilai_obj.delete()
            return redirect("menu:ujian",id_mapel=id_mapel)
    except MataPelajaran.DoesNotExist:
        raise Http404()
    except Nilai.DoesNotExist:
        raise Http404()

@login_required(login_url='user:masuk')
def daftar_nilai_permapel(request,id_mapel):
    try:
        Transaksi.objects.get(user=request.user, transaksi_status="settlement")
    except Transaksi.DoesNotExist:
        if request.user.role not in ["pemateri","admin"]:
            return redirect("menu:pembayaran")
    try:
        if request.user.role in ['pemateri',"admin"]:
            nilai_objs = Nilai.objects.filter(mata_pelajaran__pk=id_mapel).select_related('sertifikat')
        else:
            nilai_objs = Nilai.objects.filter(user=request.user,mata_pelajaran__pk=id_mapel).select_related('sertifikat')

    except Nilai.DoesNotExist:
        pass
    mapel_objs = MataPelajaran.objects.all()
    nama_mapel = MataPelajaran.objects.get(pk=id_mapel).nama_mapel
    context = {
        "nilai_objs": nilai_objs,
        "mapel_objs":mapel_objs,
        "nama_mapel":nama_mapel,
    }
    return render(request, 'nilai/nilai.html', context)