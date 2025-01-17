from django.db import models
from user.models import Users
from menu.mapel.models import MataPelajaran
from menu.utils.encode_url import encode_id
import uuid
from django.utils import timezone
# Create your models here.
class Nilai(models.Model):
    choices ={
        "lulus":"lulus",
        "tidak lulus":"tidak lulus"

    }
    id_nilai            = models.BigAutoField(primary_key=True,unique=True,db_index=True)
    user                = models.ForeignKey(Users,on_delete=models.CASCADE,db_index=True)
    mata_pelajaran_obj  = models.ForeignKey(MataPelajaran,on_delete=models.CASCADE,db_index=True,null=True)
    mata_pelajaran      = models.CharField(max_length=100,null=True)
    kelas               = models.CharField(max_length=100,null=True)
    level_study         = models.CharField(max_length=100,null=True)
    nilai               = models.IntegerField()
    predikat            = models.CharField(max_length=2)
    status              = models.CharField(max_length=12,choices=choices)
    tanggal_ujian       = models.DateTimeField(auto_now_add=True,editable=False)

    def save(self, *args, **kwargs):
        if self.level_study:
            self.level_study = self.level_study.strip().lower()
        if self.mata_pelajaran:
            self.mata_pelajaran = self.mata_pelajaran.strip().lower()
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return f"{self.mata_pelajaran} = {self.nilai}"
    
    def get_id_safe(self):
        return encode_id(self.pk)
    
    class Meta:
        verbose_name_plural = "Nilai"
        ordering = ['mata_pelajaran']
        
class Sertifikat(models.Model):
    no_cert         = models.UUIDField(primary_key=True,unique=True,db_index=True,default=uuid.uuid4)
    nama            = models.CharField(max_length=100)
    tingkat_studi   = models.CharField(max_length=100)
    kelas           = models.CharField(max_length=100,null=True)
    mata_pelajaran  = models.CharField(max_length=100)
    predikat        = models.CharField(max_length=2)
    nilai           = models.IntegerField()
    tanggal_lahir   = models.DateField()
    user            = models.ForeignKey(Users,on_delete=models.CASCADE,blank=True,null=True)
    nilai_obj       = models.OneToOneField(Nilai,on_delete=models.SET_NULL,null=True)
    created_at      = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        verbose_name_plural = "Sertifikat"
        
    def get_id_safe(self):
        return encode_id(self.pk)
    
    def __str__(self):
        return f"{self.nama}  -  {self.tingkat_studi}  -  {self.mata_pelajaran}"