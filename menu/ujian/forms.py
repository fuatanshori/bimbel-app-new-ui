from django import forms
from . models import SoalUjian


class SoalUjianForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SoalUjianForm, self).__init__(*args, **kwargs)
        self.fields['gambar_soal'].widget.attrs['class'] = 'form-control w-100'
        self.fields['soal'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_1'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_2'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_3'].widget.attrs['class'] = 'form-control '
        self.fields['jawaban_4'].widget.attrs['class'] = 'form-control '
        self.fields['pilih_jawaban_benar'].widget.attrs['class'] = 'form-select'
    
    

    class Meta:
        model = SoalUjian
        exclude = ['mata_pelajaran']
