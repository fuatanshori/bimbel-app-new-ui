from django import forms
from . models import SoalUjian
from django_ckeditor_5.widgets import CKEditor5Widget

class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mengatur atribut class untuk widget gambar_soal
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        
        # Mengatur field yang wajib diisi (required)
        required_fields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 'jawaban_4']
        for field in required_fields:
            self.fields[field].required = True
            
        # Mengatur field yang opsional (tidak required)
        optional_fields = ['jawaban_5', 'jawaban_6', 'jawaban_7']
        for field in optional_fields:
            self.fields[field].required = False
        
        # Mengatur class untuk pilihan jawaban benar
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