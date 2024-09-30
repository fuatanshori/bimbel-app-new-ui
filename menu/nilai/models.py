from django.db import models
from user.models import Users
from menu.mapel.models import MataPelajaran
from menu.utils.encode_url import encode_id


# Create your models here.
class Nilai(models.Model):
    choices ={
        "lulus":"lulus",
        "tidak lulus":"tidak lulus"

    }
    id_nilai = models.BigAutoField(primary_key=True,unique=True)
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    mata_pelajaran = models.ForeignKey(MataPelajaran,on_delete=models.PROTECT)
    nilai = models.CharField(max_length=20)
    predikat = models.CharField(max_length=2)
    status = models.CharField(max_length=12,choices=choices)

    def __str__(self) -> str:
        return f"{self.mata_pelajaran} = {self.nilai}"
    
    def get_id_safe(self):
        return encode_id(self.pk)
    
    class Meta:
        verbose_name_plural = "Nilai"