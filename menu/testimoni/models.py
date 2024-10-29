from django.db import models
from user.models import Users

# Create your models here.
class Testimoni(models.Model):
    user = models.OneToOneField(Users,on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    testimonial_review = models.TextField()
    tanggal = models.DateTimeField(auto_now=True)