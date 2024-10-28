from django.db import models
from user.models import Users

# Create your models here.
class Testimoni(models.Model):
    user = models.OneToOneField(Users,on_delete=models.CASCADE)
    rating = models.SmallIntegerField()
    testimonial_review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)