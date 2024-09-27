from django.contrib import admin
from .models import Modul
# Register your models here.


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    pass
