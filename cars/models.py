
from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models

from catalog.models import Brand, CarModel, Feature

class Car(models.Model):
    class FuelTypeChoices(models.TextChoices):
        PETROL = 'petrol', 'Бензин'
        DIESEL = 'diesel', 'Дизел'
        HYBRID = 'hybrid', 'Хибрид'
        ELECTRIC = 'electric', 'Електрически'

    class TransmissionChoices(models.TextChoices):
        MANUAL = 'manual', 'Ръчна'
        AUTOMATIC = 'automatic', 'Автоматична'
    owner = models.ForeignKey(User,
        on_delete=models.CASCADE,
        related_name='cars',
    )
    brand = models.ForeignKey(Brand,
        on_delete=models.CASCADE,
        related_name='cars',
    )
    car_model = models.ForeignKey(CarModel,
        on_delete=models.CASCADE,
        related_name='cars',
    )
    features = models.ManyToManyField(Feature,
        blank=True,
        related_name='cars',
    )

    title = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(5)],
        help_text='Въведи заглавие.',
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField()
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelTypeChoices.choices,
    )
    transmission = models.CharField(
        max_length=20,
        choices=TransmissionChoices.choices,
    )
    horsepower = models.PositiveIntegerField()
    color = models.CharField(max_length=30)
    description = models.TextField()
    main_image = models.ImageField(upload_to='cars/')
    is_published = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Car'

    def clean(self):
        current_year = datetime.now().year

        if self.year is not None and (self.year < 1950 or self.year > current_year + 1):
            raise ValidationError({
                'year': 'Въведи валидна дата на производство.',
            })

        if self.price is not None and self.price <= 0:
            raise ValidationError({
                'price': 'Цената трябва да е положително число.',
            })

        if self.horsepower is not None and self.horsepower <= 0:
            raise ValidationError({
                'horsepower': 'К.С трябва да е положително число.',
            })

        if self.mileage is not None and self.mileage < 0:
            raise ValidationError({
                'mileage': 'Километри не може да е отрицателно число.',
            })

        if self.brand_id and self.car_model_id:
            if self.car_model.brand_id != self.brand_id:
                raise ValidationError({
                    'car_model': 'Избраният модел не отговаря на избраната марка.',
                })

    def __str__(self):
        return f'{self.brand.name} {self.car_model.name} ({self.year})'

class CarImage(models.Model):
    car = models.ForeignKey(Car,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='cars/gallery/')
    alt_text = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Car Image'

    def __str__(self):
        return f'Image for {self.car.title}'


class CarReviewLog(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING_REVIEW = 'pending_review', 'Pending review'

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='review_logs',
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='car_review_logs',
    )
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING_REVIEW,
    )
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Car Review Log'
        verbose_name_plural = 'Car Review Logs'

    def __str__(self):
        return f'{self.car.title} - {self.status}'
