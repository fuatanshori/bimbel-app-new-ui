from django import forms
from .models import LevelStudy


class LevelStudyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LevelStudyForm, self).__init__(*args, **kwargs)
        self.fields['level_study'].widget.attrs['class'] = 'form-control'
        self.fields['kelas'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        level_study = cleaned_data.get('level_study')
        kelas_input = cleaned_data.get('kelas')

        # Split the input value into a list of kelas values (assuming comma separated)
        kelas_values = [kelas.strip() for kelas in kelas_input.split(',')]

        # Loop through each kelas value and check if the combination already exists
        for kelas in kelas_values:
            if LevelStudy.objects.filter(level_study=level_study, kelas=kelas).exists():
                raise forms.ValidationError(f'The combination of Level Study and Kelas {kelas} already exists.')

        return cleaned_data

    class Meta:
        model = LevelStudy
        exclude=[]