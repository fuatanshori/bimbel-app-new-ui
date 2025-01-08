from django import forms
from . models import SoalUjian
from django_ckeditor_5.widgets import CKEditor5Widget

class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SoalUjianForm, self).__init__(*args, **kwargs)
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['jawaban_1'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_2'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_3'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_4'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_5'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_6'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_7'].widget.attrs['class'] = 'form-control '
        self.fields['pilih_jawaban_benar'].widget.attrs['class'] = 'form-select'
        
    def clean(self):
        cleaned_data = super().clean()
        required_fields = ['soal']
        
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
    

    class Meta:
        model = SoalUjian
        exclude = ['mata_pelajaran']

    class Meta:
        model = SoalUjian
        widgets = {
              "soal": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
              )
          }