from django.db import models
from django.core.validators import MaxLengthValidator

class LevelStudy(models.Model):
    level_study = models.CharField(
        max_length=100, 
        unique=True,
        validators=[MaxLengthValidator(100)]  # Validator untuk memastikan tidak lebih dari 100 karakter
    )

    def __str__(self) -> str:
        return self.level_study  # Cukup sederhana

    class Meta:
        verbose_name_plural = "Level Studies"  # Memperbaiki kesesuaian plural
        ordering = ['level_study']  # Mengurutkan berdasarkan level_study