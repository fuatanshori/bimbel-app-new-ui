from django.db import models
from user.models import Users
from config import midtrans
from django.core.exceptions import ValidationError
import uuid
from menu.utils.encode_url import encode_id
PAYMENT_STATUS = midtrans.PAYMENT_STATUS
# Create your models here.


class Tarif(models.Model):
    id_tarif        = models.AutoField(unique=True,primary_key=True)
    subject         = models.CharField(max_length=50)
    harga           = models.PositiveBigIntegerField()
    is_used         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Tarif'
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"{self.subject}"
    
    @classmethod
    def get_tarif_is_used(cls):
        try:
            return cls.objects.get(is_used=True)
        except cls.DoesNotExist:
            return None
            
    def clean(self):
        if self.harga < 1 or self.harga > 99999999999:
            raise ValidationError(f'jumlah kurang dari 1 dan lebih dari 99999999999')

    def get_id_safe(self):
        return encode_id(self.pk)
    
class Diskon(models.Model):
    id_diskon           = models.BigAutoField(unique=True,primary_key=True)
    diskon_name         = models.CharField(max_length=100)
    diskon_code         = models.CharField(max_length=100,db_collation='utf8mb4_bin')
    is_publish           = models.BooleanField(default=False)
    persentase_diskon   = models.SmallIntegerField(help_text='pilih diskon dari 1 sampai 100 akan dihitung sebagai persen')
    tarif               = models.ForeignKey(Tarif,on_delete=models.CASCADE)
    kedaluwarsa         = models.DateField()
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Diskon"
        ordering = ["-created_at"]
        unique_together = ('tarif', 'diskon_code')

    def __str__(self):
        return self.diskon_name
    
    def clean(self):
        if ' ' in self.diskon_code:
            raise ValidationError('diskon code tidak boleh spasi.')
        if self.persentase_diskon > 99 or self.persentase_diskon < 1:
            raise ValidationError(f'diskon tidak boleh melebihi 99 persen atau kurang dari 1 persen')
    
    def get_id_safe(self):
        return encode_id(self.pk)
    
class Transaksi(models.Model):
    id_transaksi        = models.UUIDField(unique=True, primary_key=True)
    user                = models.OneToOneField(Users, on_delete=models.CASCADE)
    tarif               = models.ForeignKey(Tarif,on_delete=models.SET_NULL,null=True,blank=True)
    harga_akhir         = models.PositiveBigIntegerField(null=True,blank=True)
    harga_awal          = models.PositiveBigIntegerField(null=True,blank=True)
    harga_terpotong     = models.PositiveBigIntegerField(null=True,blank=True)
    transaksi_status    = models.CharField(max_length=15, choices=PAYMENT_STATUS,db_index=True)
    va_number           = models.CharField(max_length=18, null=True, blank=True)
    layanan_pembayaran  = models.CharField(max_length=10, null=True, blank=True)
    diskon              = models.ForeignKey(Diskon,null=True,blank=True,on_delete=models.SET_NULL)
    transaction_time    = models.DateTimeField(null=True, blank=True)
    qrcode_link         = models.TextField(null=True,blank=True)
    deep_link_redirect  = models.TextField(null=True,blank=True)
    expiry_time         = models.DateTimeField(null=True, blank=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.id_transaksi == None:
            self.id_transaksi = uuid.uuid4()
        super(Transaksi, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Transaksi'
        
    def __str__(self):
        return f"{self.id_transaksi}"
