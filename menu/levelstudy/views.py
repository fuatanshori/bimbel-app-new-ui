from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils.decorator import admin_pemateri_required
from .models import LevelStudy
from .forms import LevelStudyForm
from menu.utils.pagination import pagination_queryset
from menu.utils.encode_url import encode_id,decode_id

@login_required(login_url='user:masuk')
@admin_pemateri_required
def levelstudy(request):
    amount_perpage = 5
    levelstudy_queryset = LevelStudy.objects.all()  # Ambil queryset
    custom_range, levelstudy_objs = pagination_queryset(request, levelstudy_queryset, amount_perpage)
    context = {
        "levelstudy_objs": levelstudy_objs,
        "custom_range": custom_range,
    }
    return render(request, "levelstudy/levelstudy.html", context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_levelstudy(request):
    if request.method == "POST":
        level_study_form = LevelStudyForm(request.POST)
        if level_study_form.is_valid():
            level_study_form.save()  # Simpan objek menggunakan save() langsung
            messages.success(request, f"Selamat, level study {level_study_form.cleaned_data['level_study']} berhasil ditambahkan.")
            return redirect("menu:levelstudy")
    else:
        level_study_form = LevelStudyForm()  # Hanya inisialisasi untuk GET

    context = {
        "level_study_form": level_study_form,
    }
    return render(request, 'levelstudy/tambah_levelstudy.html', context)

@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapus_levelstudy(request, id_levelstudy):
    pk = decode_id(id_levelstudy)
    levelstudy_obj = get_object_or_404(LevelStudy, pk=pk)  # Menggunakan get_object_or_404
    levelstudy_obj.delete()
    messages.success(request, f"Selamat, level study {levelstudy_obj.level_study} berhasil dihapus.")
    return redirect("menu:levelstudy")

@login_required(login_url='user:masuk')
@admin_pemateri_required
def edit_levelstudy(request, id_levelstudy):
    pk = decode_id(id_levelstudy)
    levelstudy_obj = get_object_or_404(LevelStudy, pk=pk)  # Menggunakan get_object_or_404
    if request.method == "POST":
        level_study_form = LevelStudyForm(request.POST, instance=levelstudy_obj)
        if level_study_form.is_valid():
            level_study_form.save()
            messages.success(request, f"Selamat, level study {levelstudy_obj.level_study} berhasil diperbarui.")
            return redirect("menu:levelstudy")
    else:
        level_study_form = LevelStudyForm(instance=levelstudy_obj)

    context = {
        "levelstudy_obj": levelstudy_obj,
        "level_study_form": level_study_form,
    }
    return render(request, 'levelstudy/edit_levelstudy.html', context)
