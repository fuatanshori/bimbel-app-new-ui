from django.db import models
from menu.levelstudy.models import LevelStudy
from menu.utils.encode_url import encode_id
# Create your models here.


class MataPelajaran(models.Model):
    nama_mapel = models.CharField(max_length=20)
    description = models.TextField(max_length=100, blank=True, null=True)
    level_study = models.ForeignKey(LevelStudy,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nama_mapel}"
    
   
    class Meta:
        verbose_name_plural = "Mata Pelajaran"
        unique_together = ('nama_mapel', 'level_study')
        ordering = ['-created_at']
    
    def get_id_safe(self):
        return encode_id(self.pk)