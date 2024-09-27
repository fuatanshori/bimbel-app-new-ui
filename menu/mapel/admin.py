from django.contrib import admin
from .models import MataPelajaran
# Register your models here.


@admin.register(MataPelajaran)
class MataPelajaranAdmin(admin.ModelAdmin):
    pass
