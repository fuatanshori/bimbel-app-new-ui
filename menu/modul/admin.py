from django.contrib import admin
from .models import Modul,Chat
# Register your models here.


@admin.register(Modul)
class ModulAdmin(admin.ModelAdmin):
    pass

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass