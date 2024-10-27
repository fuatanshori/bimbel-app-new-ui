from django.contrib import admin
from .models import Nilai,Sertifikat
# Register your models here.

@admin.register(Nilai)
class NilaiAdmin(admin.ModelAdmin):
    list_display = ("level_study","mata_pelajaran","nilai","predikat","status","mata_pelajaran_obj","user",'tanggal_ujian')

admin.site.register(Sertifikat)