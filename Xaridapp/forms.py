from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Product


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [super(MultipleImageField, self).clean(item, None) for item in data]


class SignUpForm(UserCreationForm):

    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Parol kiriting',
                'class': 'form-control'
            }
        ),
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


class ProductForm(forms.ModelForm):
    gallery_images = MultipleImageField(required=False, label="Qo‘shimcha rasmlar")

    class Meta:
        model = Product
        fields = ("category", "name", "description", "price", "image", "stock", "is_available")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Narx noldan katta bo‘lishi kerak.")
        return price
