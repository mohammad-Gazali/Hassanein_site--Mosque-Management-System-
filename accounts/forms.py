from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django import forms
from django.contrib.auth.models import User

attrs = {'class': 'form-control'}

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs=attrs)
    )

    password = forms.CharField(
        label='كلمة المرور',
        widget= forms.PasswordInput(attrs=attrs)
    )