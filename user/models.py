from django.contrib.auth.models import AbstractUser,PermissionsMixin
from django.db import models
from django.utils.translation import gettext as _
from .managers import CustomUserManager
import uuid

from django.core.files.base import ContentFile
from PIL import Image as PILImage
import io
import os

class Users(AbstractUser,PermissionsMixin):
    ROLE = (
        ('pelajar', 'Pelajar'),
        ('pemateri', 'Pemateri'),
        ('admin', 'Admin'),
    )
    id              = None
    username        = None
    first_name      = None
    last_name       = None

    
    id_user         = models.UUIDField(default=uuid.uuid4,primary_key=True,unique=True)
    full_name       = models.CharField(_("full name"), max_length=50)
    email           = models.EmailField(_("email"), unique=True)
    role            = models.CharField(_("role"), max_length=50, choices=ROLE, default='pelajar',help_text=_("To enter the Django dashboard, change to admin or pemateri"),)
    is_active       = models.BooleanField(default=False)
    waktu_aktifasi  = models.DateTimeField(blank=True,null=True)
    last_password_reset_request = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
      
            
    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        elif self.role != 'admin':
            self.is_staff = False
            self.is_superuser = False
        if self.role == 'pemateri':
            self.is_staff = True
        super().save(*args, **kwargs)
        
        
class Token(models.Model):
    user                    = models.ForeignKey(Users,on_delete=models.CASCADE)  
    token                   = models.CharField(max_length=100,blank=True,null=True)
    is_created              = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}"
    

class ActiveSession(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    JENIS_KELAMIN = (
        ('pria', 'Pria'),
        ('wanita', 'Wanita'),
    )
    user            = models.OneToOneField(Users,on_delete=models.CASCADE)
    nama_lengkap    = models.CharField(max_length=100)
    foto            = models.ImageField(upload_to="foto_profile",null=True)
    jenis_kelamin   = models.CharField(max_length=10,choices=JENIS_KELAMIN,null=True)
    tempat_tinggal  = models.CharField(max_length=40,null=True)
    nomor_telepon   = models.CharField(max_length=14,null=True)
    tanggal_lahir   = models.DateField(null=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.nama_lengkap}"