from django.db import models
from menu.mapel.models import MataPelajaran
from django.core.validators import FileExtensionValidator 
from menu.utils.encode_url import encode_id
import uuid
# Create your models here.
from django_ckeditor_5.fields import CKEditor5Field

class SoalUjian(models.Model):
    choices = {
    "jawaban1":"jawaban_1",
    "jawaban2":"jawaban_2",
    "jawaban3":"jawaban_3",
    "jawaban4":"jawaban_4",
    "jawaban5":"jawaban_5",
    "jawaban6":"jawaban_6",
    "jawaban7":"jawaban_7",
    }
    id_soal     = models.BigAutoField(primary_key=True,unique=True)
    gambar_soal = models.ImageField(upload_to="soal",blank=True,null=True,validators=[FileExtensionValidator(["jpg","png"])])
    soal        = CKEditor5Field('soal', config_name='extends',null=True, blank=True)
    jawaban_1   = CKEditor5Field('jawaban_1', config_name='extends')
    jawaban_2   = CKEditor5Field('jawaban_2', config_name='extends')
    jawaban_3   = CKEditor5Field('jawaban_3', config_name='extends')
    jawaban_4   = CKEditor5Field('jawaban_4', config_name='extends')
    jawaban_5   = CKEditor5Field('jawaban_5', config_name='extends',null=True,blank=True)
    jawaban_6   = CKEditor5Field('jawaban_6', config_name='extends',null=True,blank=True)
    jawaban_7   = CKEditor5Field('jawaban_7', config_name='extends',null=True,blank=True)
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
    
    @property
    def get_id(self):
        return f"soal__{self.pk}"

