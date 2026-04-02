from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email address',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Въведи имейл',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Избери потребителско име',
            }),
        }
        help_texts = {
            'username': 'Задължително поле.',
        }
        labels = {
            'username': 'Потребителско име',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Въведи парола',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Повтори парола',
        })
        self.fields['password1'].help_text = 'Паролата трябва да съдържа минимум 8 символа.'
        self.fields['password2'].help_text = 'Повтори паролата.'

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Потребител с такъв имейл вече съществува.')

        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone_number', 'location', 'info', 'favorite_brands', 'is_dealer')
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Въведи телефонен номер.',
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Въведи локация.',
            }),
            'info': forms.Textarea(attrs={
                'placeholder': 'Въведи информация',
                'rows': 4,
            }),
            'favorite_brands': forms.CheckboxSelectMultiple(),
            'is_dealer': forms.CheckboxInput(),
        }
        labels = {
            'phone_number': 'Телефонен номер',
            'location': 'Локация',
            'info': 'Кратка информация',
            'favorite_brands': 'Любими марки',
            'is_dealer': 'Търговец / Автокъща',
        }
        help_texts = {
            'phone_number': 'Използвай само цифри.',
            'favorite_brands': 'Избери марки, които искаш да следиш.',
            'is_dealer': 'Маркирай за професионална употреба.',
        }
