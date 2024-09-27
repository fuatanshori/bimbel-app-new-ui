from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Users,Profile


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Users
        fields = ("email",'full_name')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Users
        fields = ("email",'full_name')




class ChangePasswordForm(PasswordChangeForm):
   
    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        
        if old_password == new_password1 and old_password == new_password2:
            raise forms.ValidationError("Kata sandi tidak boleh sama dengan sebelumnya")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control w-100 '

class AddProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddProfileForm, self).__init__(*args, **kwargs)
        self.fields['nama_lengkap'].widget.attrs['class'] = 'form-control'
        self.fields['jenis_kelamin'].widget.attrs['class'] = 'form-select'
        self.fields['jenis_kelamin'].widget.attrs['style'] = 'border: 1px solid #2c2e33;'
        self.fields['tempat_tinggal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['foto'].widget.attrs['class'] = 'form-control w-100'
        self.fields['nomor_telepon'].widget.attrs['class'] = 'form-control w-100'
        self.fields['nomor_telepon'].widget.attrs['class'] = 'form-control w-100'
        self.fields['tanggal_lahir'].widget.attrs['class'] = 'form-control'

    
    class Meta:
        model = Profile
        exclude = ["user"]
        widgets = {
              "tanggal_lahir": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
          }