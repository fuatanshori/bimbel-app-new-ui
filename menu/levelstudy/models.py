from django.db import models

# Create your models here.

class LevelStudy(models.Model):
    level_study = models.CharField(max_length=100,unique=True)

    def __str__(self) -> str:
        return f"{self.level_study}"
    
    class Meta:
        verbose_name_plural = "Level Study"