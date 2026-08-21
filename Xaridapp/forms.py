from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = "Foydalanuvchi nomi"
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username kiriting',
            'class': 'form-control'
        })

        self.fields['email'].label = "Elektron pochta"
        self.fields['email'].widget.attrs.update({
            'placeholder': 'example@gmail.com',
            'class': 'form-control'
        })

        self.fields['password1'].label = "Parol"
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Parol kiriting',
            'class': 'form-control'
        })

        self.fields['password2'].label = "Parolni tasdiqlang"
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Parolni qayta kiriting',
            'class': 'form-control'
        })


class CustomLoginForm(AuthenticationForm):

    username = forms.CharField(
        label="Foydalanuvchi nomi",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username kiriting',
                'autocomplete': 'username'
            }
        )
    )

    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Parol kiriting',
                'autocomplete': 'current-password'
            }
        )
    )