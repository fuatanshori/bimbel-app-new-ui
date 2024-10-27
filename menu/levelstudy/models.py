from django.db import models
from django.core.validators import MaxLengthValidator
from menu.utils.encode_url import decode_id,encode_id

class LevelStudy(models.Model):
    level_study = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100)]  # Validator untuk memastikan tidak lebih dari 100 karakter
    )
    kelas = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.level_study  # Cukup sederhana

    class Meta:
        verbose_name_plural = "Level Studi"  # Memperbaiki kesesuaian plural
        ordering = ['-created_at']  # Mengurutkan berdasarkan level_study
        unique_together=("kelas","level_study")
    
    def get_id_safe(self):
        return encode_id(self.pk)