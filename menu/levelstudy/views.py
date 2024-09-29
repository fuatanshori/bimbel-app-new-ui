from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from core.utils.decorator import admin_pemateri_required
from django.contrib import messages
from .models import LevelStudy
from .forms import LevelStudyForm
from menu.utils.pagination import pagination_queryset
# Create your views here.

@login_required(login_url='user:masuk')
@admin_pemateri_required
def levelstudy(request):
    amount_perpage=5
    custom_range,levelstudy_objs = pagination_queryset(request,LevelStudy.objects.all(),amount_perpage)
    context = {
        "levelstudy_objs":levelstudy_objs,
        "custom_range":custom_range,
    }
    return render(request,"levelstudy/levelstudy.html",context)


@login_required(login_url='user:masuk')
@admin_pemateri_required
def tambah_levelstudy(request):
    if request.method == "POST":
        level_study_form = LevelStudyForm(request.POST)
        if level_study_form.is_valid():
            level_study = level_study_form.cleaned_data['level_study']
            LevelStudy.objects.create(
                level_study=level_study
            ).save()
            messages.success(request,f"Selamat level study {level_study} berhasil di tambahkan")
            return redirect("menu:levelstudy")
    level_study_form = LevelStudyForm(request.POST or None)
    context={
        "level_study_form": level_study_form,
    }
    return render(request, 'levelstudy/tambah_levelstudy.html',context)


@login_required(login_url='user:masuk')
@admin_pemateri_required
def hapus_levelstudy(request, id_levelstudy):
    try:
        levelstudy_obj = LevelStudy.objects.get(pk=id_levelstudy)
        levelstudy_obj.delete()
        messages.success(request, f"Selamat, level study {levelstudy_obj.level_study} berhasil dihapus.")
    except LevelStudy.DoesNotExist:
        messages.error(request, "level Study tidak ditemukan.")
    
    return redirect("menu:levelstudy")


@login_required(login_url='user:masuk')
@admin_pemateri_required
def edit_levelstudy(request,id_levelstudy):
    levelstudy_obj = LevelStudy.objects.get(pk=id_levelstudy)
    if request.method == "POST":
        level_study_form = LevelStudyForm(request.POST,instance=levelstudy_obj)
        if level_study_form.is_valid():
            level_study_form.save()
            messages.success(request,f"Selamat level study {levelstudy_obj.level_study} berhasil di tambahkan")
            return redirect("menu:levelstudy")
    level_study_form = LevelStudyForm(instance=levelstudy_obj)
    context={
        "levelstudy_obj":levelstudy_obj,
        "level_study_form": level_study_form,
    }
    return render(request, 'levelstudy/edit_levelstudy.html',context)