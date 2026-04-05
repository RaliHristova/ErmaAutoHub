from django import forms

from .models import Inquiry


class InquiryBaseForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('phone_number', 'message')
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Въведете телефонен номер',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Напишете вашето запитване',
                'rows': 5,
            }),
        }
        labels = {
            'phone_number': 'Телефонен номер',
            'message': 'Съобщение',
        }
        help_texts = {
            'message': 'Минимум 10 символа.',
        }

class InquiryCreateForm(InquiryBaseForm):
    pass


class InquiryEditForm(InquiryBaseForm):
    pass
