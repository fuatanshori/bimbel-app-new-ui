from django.contrib import admin
from .models import SoalUjian
# Register your models here.

@admin.register(SoalUjian)
class SoalUjianAdmin(admin.ModelAdmin):
    pass

