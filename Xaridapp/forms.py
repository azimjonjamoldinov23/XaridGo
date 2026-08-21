from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):

    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Parol kiriting',
                'class': 'form-control'
            }
        ),
        min_length=1,
        required=True
    )

    password2 = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Parolni qayta kiriting',
                'class': 'form-control'
            }
        ),
        min_length=1,
        required=True
    )

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

    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # Django'ning standart password validatorlarini o'tkazib yuboramiz
        return password


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