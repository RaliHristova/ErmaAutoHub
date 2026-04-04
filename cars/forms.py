from datetime import datetime

from django import forms

from catalog.models import Brand, CarModel

from .models import Car, CarImage


class BrandFilteredModelSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        instance = getattr(value, "instance", None)

        if instance is not None:
            option["attrs"]["data-brand-id"] = str(instance.brand_id)

        return option


class CarBaseForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = (
            "brand",
            "car_model",
            "features",
            "title",
            "price",
            "year",
            "mileage",
            "fuel_type",
            "transmission",
            "horsepower",
            "color",
            "description",
            "main_image",
        )
        widgets = {
            "brand": forms.Select(attrs={
                "data-brand-select": "true",
            }),
            "car_model": BrandFilteredModelSelect(attrs={
                "data-model-select": "true",
            }),
            "features": forms.CheckboxSelectMultiple(),
            "title": forms.TextInput(attrs={
                "placeholder": "Напр: BMW X5 M Sport",
            }),
            "price": forms.NumberInput(attrs={
                "placeholder": "Цена в евро",
            }),
            "year": forms.NumberInput(attrs={
                "placeholder": "Година на производство",
            }),
            "mileage": forms.NumberInput(attrs={
                "placeholder": "Пробег в километри",
            }),
            "fuel_type": forms.Select(),
            "transmission": forms.Select(),
            "horsepower": forms.NumberInput(attrs={
                "placeholder": "Конски сили",
            }),
            "color": forms.TextInput(attrs={
                "placeholder": "Цвят",
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Добавете описание на автомобила",
                "rows": 5,
            }),
            "main_image": forms.ClearableFileInput(),
        }
        labels = {
            "brand": "Марка",
            "car_model": "Модел",
            "features": "Екстри",
            "title": "Заглавие",
            "price": "Цена",
            "year": "Година",
            "mileage": "Пробег",
            "fuel_type": "Гориво",
            "transmission": "Скоростна кутия",
            "horsepower": "Конски сили",
            "color": "Цвят",
            "description": "Описание",
            "main_image": "Основна снимка",
        }
        help_texts = {
            "features": "Изберете една или повече екстри.",
            "description": "Опишете състоянието, сервизната история и важните детайли.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].queryset = Brand.objects.order_by("name")
        self.fields["car_model"].queryset = CarModel.objects.select_related("brand").order_by("brand__name", "name")

class CarCreateForm(CarBaseForm):
    pass


class CarEditForm(CarBaseForm):
    pass


class CarDeleteForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = (
            "title",
            "brand",
            "car_model",
            "year",
            "price",
            "mileage",
        )
        labels = {
            "title": "Заглавие",
            "brand": "Марка",
            "car_model": "Модел",
            "year": "Година",
            "price": "Цена",
            "mileage": "Пробег",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _, field in self.fields.items():
            field.disabled = True


class CarApproveForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = (
            "title",
            "is_approved",
        )
        labels = {
            "title": "Обява",
            "is_approved": "Одобрена",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].disabled = True


class CarFilterForm(forms.Form):
    SORT_CHOICES = (
        ("newest", "Най-нови обяви"),
        ("price_asc", "Цена: възходящо"),
        ("price_desc", "Цена: низходящо"),
        ("year_desc", "Година: нови към стари"),
        ("mileage_asc", "Пробег: нисък към висок"),
    )

    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        empty_label="Всички марки",
        label="Марка:",
        widget=forms.Select(attrs={
            "data-brand-select": "true",
        }),
    )
    car_model = forms.ModelChoiceField(
        queryset=CarModel.objects.select_related("brand").all(),
        required=False,
        empty_label="Всички модели",
        label="Модел:",
        widget=BrandFilteredModelSelect(attrs={
            "data-model-select": "true",
        }),
    )
    fuel_type = forms.ChoiceField(
        choices=[("", "Всички")] + list(Car.FuelTypeChoices.choices),
        required=False,
        label="Гориво:",
        widget=forms.Select(),
    )
    transmission = forms.ChoiceField(
        choices=[("", "Всички")] + list(Car.TransmissionChoices.choices),
        required=False,
        label="Скоростна кутия:",
        widget=forms.Select(),
    )
    min_year = forms.IntegerField(
        required=False,
        label="Година от:",
        widget=forms.NumberInput(attrs={
            "placeholder": "Напр. 2002",
        }),
    )
    max_year = forms.IntegerField(
        required=False,
        label="Година до:",
        widget=forms.NumberInput(attrs={
            "placeholder": "Напр. 2026",
        }),
    )
    min_price = forms.DecimalField(
        required=False,
        label="Цена от:",
        widget=forms.NumberInput(attrs={
            "placeholder": "Напр. 1000",
        }),
    )
    max_price = forms.DecimalField(
        required=False,
        label="Цена до:",
        widget=forms.NumberInput(attrs={
            "placeholder": "Напр. 50000",
        }),
    )
    sort_by = forms.ChoiceField(
        choices=[("", "Без сортиране")] + list(SORT_CHOICES),
        required=False,
        label="Сортиране",
        widget=forms.Select(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].queryset = Brand.objects.order_by("name")
        self.fields["car_model"].queryset = CarModel.objects.select_related("brand").order_by("brand__name", "name")

    def clean_min_year(self):
        value = self.cleaned_data.get("min_year")
        current_year = datetime.now().year

        if value is not None:
            if value < 1950:
                raise forms.ValidationError("Минималната година не може да е по-малка от 1950.")
            if value > current_year + 1:
                raise forms.ValidationError("Минималната година не може да е по-голяма от следващата календарна година.")

        return value

    def clean_max_year(self):
        value = self.cleaned_data.get("max_year")
        current_year = datetime.now().year

        if value is not None:
            if value < 1950:
                raise forms.ValidationError("Максималната година не може да е по-малка от 1950.")
            if value > current_year + 1:
                raise forms.ValidationError("Максималната година не може да е по-голяма от следващата календарна година.")

        return value

    def clean_min_price(self):
        value = self.cleaned_data.get("min_price")

        if value is not None and value < 0:
            raise forms.ValidationError("Минималната цена не може да е отрицателна.")

        return value

    def clean_max_price(self):
        value = self.cleaned_data.get("max_price")

        if value is not None and value < 0:
            raise forms.ValidationError("Максималната цена не може да е отрицателна.")

        return value

    def clean(self):
        cleaned_data = super().clean()

        brand = cleaned_data.get("brand")
        car_model = cleaned_data.get("car_model")
        min_year = cleaned_data.get("min_year")
        max_year = cleaned_data.get("max_year")
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        if brand and car_model and car_model.brand != brand:
            self.add_error("car_model", "Избраният модел не принадлежи на избраната марка.")

        if min_year is not None and max_year is not None and min_year > max_year:
            self.add_error("max_year", "Максималната година трябва да е по-голяма или равна на минималната.")

        if min_price is not None and max_price is not None and min_price > max_price:
            self.add_error("max_price", "Максималната цена трябва да е по-голяма или равна на минималната.")

        return cleaned_data


class CarImageForm(forms.ModelForm):
    class Meta:
        model = CarImage
        fields = ('image', 'alt_text')
        widgets = {
            'image': forms.ClearableFileInput(),
            'alt_text': forms.TextInput(attrs={
                'placeholder': 'Напр. Изглед отпред',
            }),
        }
        labels = {
            'image': 'Снимка',
            'alt_text': 'Алтернативен текст',
        }
        help_texts = {
            'alt_text': 'Кратко описание на снимката.',
        }
