from django.db import models
from menu.mapel.models import MataPelajaran
from django.core.validators import FileExtensionValidator 
from user.models import Users
from django_ckeditor_5.fields import CKEditor5Field
from menu.utils.encode_url import encode_id

# Create your models here.
class Modul(models.Model):
    nama_modul = models.CharField(max_length=50)
    mata_pelajaran = models.ForeignKey(MataPelajaran, on_delete=models.SET_NULL,null=True)
    description = CKEditor5Field('description', config_name='extends',null=True)
    modul = models.FileField(upload_to='pdf',validators=[FileExtensionValidator(allowed_extensions=["pdf"])])
    vidio = models.FileField(upload_to="vidio",validators=[FileExtensionValidator(allowed_extensions=["mp4"])],null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Users,on_delete=models.CASCADE,null=True,blank=True)
    
    def __str__(self):
        return f"{self.nama_modul}"

    class Meta:
        verbose_name_plural = "Modul"
        ordering = ['-created_at']
    
    def get_id_safe(self):
        return encode_id(self.pk)
    
class Chat(models.Model):
    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    modul = models.ForeignKey(Modul,on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    