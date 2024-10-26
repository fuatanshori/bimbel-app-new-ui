from django.contrib import admin
from .models import Nilai,Sertifikat
# Register your models here.

@admin.register(Nilai)
class NilaiAdmin(admin.ModelAdmin):
    readonly_fields=["level_study","mata_pelajaran","nilai","predikat","status","mata_pelajaran_obj","user"]


admin.site.register(Sertifikat)