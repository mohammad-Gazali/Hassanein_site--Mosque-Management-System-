from django import forms
from .models import ControlSettings


class SettingForm(forms.ModelForm):
    class Meta:
        model = ControlSettings
        fields = ['double_points', 'point_value']
        widgets = {
            'double_points': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'point_value': forms.NumberInput(attrs={'class': 'form-control w-50 d-inline-block'})
        }