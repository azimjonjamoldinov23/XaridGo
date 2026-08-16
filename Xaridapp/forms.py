from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')



class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Telefon raqam yoki Username", widget=forms.TextInput(attrs={'placeholder': '+998 -- --- -- --'}))