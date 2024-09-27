from django.contrib import admin
from .models import LevelStudy

# Register your models here.

@admin.register(LevelStudy)
class LevelStudyAdmin(admin.ModelAdmin):
    pass