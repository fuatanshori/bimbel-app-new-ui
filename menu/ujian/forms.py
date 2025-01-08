# forms.py
from django import forms
from . models import SoalUjian
from django_ckeditor_5.widgets import CKEditor5Widget

class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['pilih_jawaban_benar'].widget.attrs['class'] = 'form-select'
        
        # Make first 4 answers required
        required_fields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 'jawaban_4']
        for field in required_fields:
            self.fields[field].required = True
            
        # Make other answers optional
        optional_fields = ['jawaban_5', 'jawaban_6', 'jawaban_7']
        for field in optional_fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 'jawaban_4']
        
        for field in required_fields:
            content = cleaned_data.get(field)
            if not content:
                self.add_error(field, f'{field.replace("_", " ").title()} wajib diisi.')
                continue
                
            # Check for empty content
            stripped_content = (content.replace('&nbsp;', '')
                                    .replace('<p></p>', '')
                                    .replace('<p> </p>', '')
                                    .strip())
            if not stripped_content:
                self.add_error(field, f'{field.replace("_", " ").title()} tidak boleh kosong.')
        
        return cleaned_data

    class Meta:
        model = SoalUjian
        exclude = ['mata_pelajaran']
        widgets = {
            "soal": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_1": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_2": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_3": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_4": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_5": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_6": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
            "jawaban_7": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"},
                config_name="extends"
            ),
        }