from django.contrib import admin
from .models import Testimoni

# Register your models here.
@admin.register(Testimoni)
class TestimoniAdmin(admin.ModelAdmin):
    pass