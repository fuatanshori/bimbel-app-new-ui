from typing import Any
from django import forms
from .models import Tarif,Diskon

class TarifForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TarifForm, self).__init__(*args, **kwargs)
        self.fields['subject'].widget.attrs['class'] = 'form-control'
        self.fields['harga'].widget.attrs['class'] = 'form-control'
        self.fields['is_used'].widget.attrs['class'] = 'form-check-input'

    class Meta:
        model = Tarif
        exclude=[]

class DiskonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DiskonForm, self).__init__(*args, **kwargs)
        self.fields['diskon_name'].widget.attrs['class'] = 'form-control'
        self.fields['diskon_code'].widget.attrs['class'] = 'form-control'
        self.fields['is_publish'].widget.attrs['class'] = 'form-check-input'
        self.fields['persentase_diskon'].widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = Diskon
        exclude=["tarif"]
        widgets = {
            'kedaluwarsa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'persentase_diskon': forms.NumberInput(attrs={"min":"0","max":"99"}),
        }
