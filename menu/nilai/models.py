from django.db import models
from user.models import Users
from menu.mapel.models import MataPelajaran
from menu.utils.encode_url import encode_id
import uuid

# Create your models here.
class Nilai(models.Model):
    choices ={
        "lulus":"lulus",
        "tidak lulus":"tidak lulus"

    }
    id_nilai            = models.BigAutoField(primary_key=True,unique=True,db_index=True)
    user                = models.ForeignKey(Users,on_delete=models.CASCADE,db_index=True)
    mata_pelajaran_obj  = models.ForeignKey(MataPelajaran,on_delete=models.SET_NULL,db_index=True,null=True)
    mata_pelajaran      = models.CharField(max_length=100,null=True)
    level_study         = models.CharField(max_length=100,null=True)
    nilai               = models.IntegerField()
    predikat            = models.CharField(max_length=2)
    status              = models.CharField(max_length=12,choices=choices)

    def __str__(self) -> str:
        return f"{self.mata_pelajaran} = {self.nilai}"
    
    def get_id_safe(self):
        return encode_id(self.pk)
    
    class Meta:
        verbose_name_plural = "Nilai"
        
class Sertifikat(models.Model):
    no_cert         = models.UUIDField(primary_key=True,unique=True,db_index=True,default=uuid.uuid4)
    nama            = models.CharField(max_length=100)
    tingkat_studi   = models.CharField(max_length=100)
    mata_pelajaran  = models.CharField(max_length=100)
    predikat        = models.CharField(max_length=2)
    nilai           = models.IntegerField()
    tanggal_lahir   = models.DateField()
    user            = models.ForeignKey(Users,on_delete=models.CASCADE,blank=True,null=True)
    nilai_obj       = models.OneToOneField(Nilai,on_delete=models.SET_NULL,null=True)
    created_at      = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Sertifikat"
        
    def get_id_safe(self):
        return encode_id(self.pk)
    
    def __str__(self):
        return f"{self.nama}  -  {self.tingkat_studi}  -  {self.mata_pelajaran}"