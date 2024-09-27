from django import forms
from . models import Modul
from django_ckeditor_5.widgets import CKEditor5Widget

class ModulForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModulForm, self).__init__(*args, **kwargs)
        self.fields['nama_modul'].widget.attrs['class'] = 'form-control'
        self.fields['modul'].widget.attrs['class'] = 'form-control w-100'
        self.fields['vidio'].widget.attrs['class'] = 'form-control w-100'
        self.fields["description"].required = False
    
    class Meta:
        model = Modul
        exclude = ['mata_pelajaran','author']
        widgets = {
              "description": CKEditor5Widget(
                  attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }