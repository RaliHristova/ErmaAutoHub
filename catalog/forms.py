from django import forms

from .models import Brand, CarModel, Feature


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Напр.: BMW',
            }),
        }
        labels = {
            'name': 'Име на марка',
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if len(name) < 2:
            raise forms.ValidationError('Името трябва да съдържа поне 2 символа.')

        return name


class FeatureForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Напр: Навигация',
            }),
        }
        labels = {
            'name': 'Име на екстра',
        }
        help_texts = {
            'name': 'Пример: Кожен салон, Подгрев на седалки, Навигация.',
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if len(name) < 2:
            raise forms.ValidationError('Името трябва да съдържа поне 2 символа.')

        return name


class CarModelForm(forms.ModelForm):
    class Meta:
        model = CarModel
        fields = ('brand', 'name')
        widgets = {
            'brand': forms.Select(),
            'name': forms.TextInput(attrs={
                'placeholder': 'Напр: X5',
            }),
        }
        labels = {
            'brand': 'Марка',
            'name': 'Име на модел',
        }
        help_texts = {
            'name': 'Напр: A6, X5, C-Class.',
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if len(name) < 1:
            raise forms.ValidationError('Името на модела е задължително.')

        return name

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        name = cleaned_data.get('name')

        if brand and name:
            queryset = CarModel.objects.filter(brand=brand, name__iexact=name)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                self.add_error('name', 'Този модел вече съществува за избраната марка.')

        return cleaned_data
