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
        level_study_objs = LevelStudy.objects.filter(level_study=level_study)
        for level_study_obj in level_study_objs:
            kelas = level_study_obj.kelas
            integer_kelas = [int(x) for x in kelas.split(",")]
            if kelas_input in integer_kelas:
                raise forms.ValidationError(f'tidak bisa ditambahkan karena {kelas_input} berada didalam rentang {integer_kelas}')

        return cleaned_data

    class Meta:
        model = LevelStudy
        exclude=[]