from django.db import models
from menu.mapel.models import MataPelajaran
from menu.nilai.models import Nilai
from django.core.validators import FileExtensionValidator 
from menu.utils.encode_url import encode_id
import uuid
# Create your models here.


class SoalUjian(models.Model):
    choices = {
    "jawaban1":"jawaban_1",
    "jawaban2":"jawaban_2",
    "jawaban3":"jawaban_3",
    "jawaban4":"jawaban_4",
    }
    id_soal = models.BigAutoField(primary_key=True,unique=True)
    gambar_soal = models.ImageField(upload_to="soal",blank=True,null=True,validators=[FileExtensionValidator(["jpg","png"])])
    soal = models.CharField(max_length=200)
    jawaban_1 = models.CharField(max_length=200,blank=True,null=True)
    jawaban_2 = models.CharField(max_length=200,blank=True,null=True)
    jawaban_3 = models.CharField(max_length=200)
    jawaban_4 = models.CharField(max_length=200)
    pilih_jawaban_benar = models.CharField(choices=choices,max_length=200)
    mata_pelajaran = models.ForeignKey(MataPelajaran,on_delete=models.CASCADE)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.soal
    class Meta:
        verbose_name_plural = "Soal Ujian"
        ordering = ["-created_at"]
    
    def get_id_safe(self):
        return encode_id(self.pk)


class Sertifikat(models.Model):
    no_cert     = models.UUIDField(primary_key=True,unique=True,db_index=True,default=uuid.uuid4)
    nilai        = models.OneToOneField(Nilai,on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Sertifikat"
        
    def get_id_safe(self):
        return encode_id(self.pk)