from django import forms
from .models import LevelStudy


class LevelStudyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LevelStudyForm, self).__init__(*args, **kwargs)
        self.fields['level_study'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = LevelStudy
        exclude=[]