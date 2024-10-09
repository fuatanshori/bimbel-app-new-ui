from django.contrib import admin
from .models import Tarif ,Transaksi,Diskon

    

# Register your models here.
class DiskonAdminInline(admin.TabularInline):
    model = Diskon
    
    
@admin.register(Tarif)
class TarifAdmin(admin.ModelAdmin):
    list_display = ['subject','harga', 'is_used',]
    min_objects = 1
    actions = None
    search_fields = ['subject']
    inlines=[DiskonAdminInline]
    def has_delete_permission(self, request, obj=None):
        queryset = self.model.objects.all()
        if queryset.count() <= self.min_objects:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        queryset = self.model.objects.all()
        if queryset.count() < self.min_objects:
            return self.readonly_fields + ['is_used']
        return self.readonly_fields
            
@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    list_display =["id_transaksi","user","harga","transaksi_status","va_number","layanan_pembayaran","expiry_time"]
    readonly_fields = ["id_transaksi","va_number","qrcode_link","deep_link_redirect","layanan_pembayaran","expiry_time"]


