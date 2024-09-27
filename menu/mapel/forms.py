from django import forms
from .models import MataPelajaran


class MapelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MapelForm, self).__init__(*args, **kwargs)
        self.fields['nama_mapel'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = MataPelajaran
        exclude=["level_study"]
