from django import forms
from .models import Tarif


class TarifForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TarifForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs['class'] = 'form-control'
        self.fields['harga'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Tarif
        exclude=[]
