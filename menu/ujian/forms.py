from django import forms
from . models import SoalUjian
from django_ckeditor_5.widgets import CKEditor5Widget

class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['pilih_jawaban_benar'].widget.attrs['class'] = 'form-select'

    def clean(self):
        cleaned_data = super().clean()
        
        # Field yang wajib diisi
        required_fields = ['soal', 'jawaban_1', 'jawaban_2', 'jawaban_3', 'jawaban_4']
        
        # Cek setiap field required
        for field_name in required_fields:
            value = cleaned_data.get(field_name)
            if not value or value.strip() == '':
                self.add_error(field_name, f'{field_name.replace("_", " ").title()} tidak boleh kosong.')

        # Validasi pilihan jawaban benar
        pilih_jawaban = cleaned_data.get('pilih_jawaban_benar')
        if not pilih_jawaban:
            self.add_error('pilih_jawaban_benar', 'Pilih jawaban yang benar.')

        return cleaned_data

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