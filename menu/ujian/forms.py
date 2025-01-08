from django import forms
from . models import SoalUjian
from django_ckeditor_5.widgets import CKEditor5Widget

class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['soal'].required = True
        self.fields['jawaban_1'].required = True
        self.fields['jawaban_2'].required = True
        self.fields['jawaban_3'].required = True
        self.fields['jawaban_4'].required = True
        self.fields['jawaban_5'].required = False
        self.fields['jawaban_6'].required = False
        self.fields['jawaban_7'].required = False
        self.fields['pilih_jawaban_benar'].widget.attrs['class'] = 'form-select'
    
    

    class Meta:
        model = SoalUjian
        exclude = ['mata_pelajaran']
        widgets = {
            "soal": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_1": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_2": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_3": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_4": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_5": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_6": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
            "jawaban_7": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }
        