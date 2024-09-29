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
    

    
    def save(self, *args, **kwargs):
        if self.foto:
            # Open the uploaded image
            img = PILImage.open(self.foto)

            # Convert image to RGB if it's in RGBA mode
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Get the size for cropping
            width, height = img.size
            new_size = min(width, height)  # Use the smaller dimension for the square size

            # Calculate cropping box
            left = (width - new_size) / 2
            top = (height - new_size) / 2
            right = (width + new_size) / 2
            bottom = (height + new_size) / 2

            # Crop the image to a square
            img = img.crop((left, top, right, bottom))

            # Save the image to a BytesIO object
            img_io = io.BytesIO()
            img.save(img_io, format='JPEG', quality=85)  # Adjust quality as needed
            img_file = ContentFile(img_io.getvalue(), name=os.path.basename(self.foto.name))

            # Delete the old image if it exists
            if self.pk:  # Only do this if the object already exists
                try:
                    # Get the old file path and delete the old file
                    old_file = self.__class__.objects.get(pk=self.pk).foto.path
                    if os.path.isfile(old_file):
                        os.remove(old_file)
                except Exception as e:
                    print(f"Error deleting old file: {e}")

            # Replace the original image with the cropped image
            self.foto.save(os.path.basename(self.foto.name), img_file, save=False)

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nama_lengkap}"