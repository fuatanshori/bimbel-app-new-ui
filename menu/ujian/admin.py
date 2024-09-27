from django.contrib import admin
from .models import SoalUjian,Nilai,Sertifikat
# Register your models here.

@admin.register(SoalUjian)
class SoalUjianAdmin(admin.ModelAdmin):
    pass

admin.site.register(Nilai)
admin.site.register(Sertifikat)