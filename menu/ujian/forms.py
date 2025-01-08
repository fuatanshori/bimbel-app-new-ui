from django import forms
from . models import SoalUjian
from django_ckeditor_5.widgets import CKEditor5Widget

class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['pilih_jawaban_benar'].widget.attrs['class'] = 'form-select'
        
        # Add required validation for CKEditor fields
        required_fields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 
                         'jawaban_4']
        
        for field in required_fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        # Validate all CKEditor fields
        ckeditor_fields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 
                          'jawaban_4']
        
        for field in ckeditor_fields:
            content = cleaned_data.get(field)
            if content:
                # Remove common empty editor patterns
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
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_1": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_2": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_3": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_4": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_5": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_6": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
            "jawaban_7": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5", "required": "required"}, 
                config_name="extends"
            ),
        }