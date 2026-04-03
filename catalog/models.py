from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify


class Brand(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        error_messages={
            'unique': 'Марка с това име вече съществува.',
        },
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Brand'


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='car_models',
    )
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['brand__name', 'name']
        unique_together = ('brand', 'name')
        verbose_name = 'Car Model'


    def __str__(self):
        return f'{self.brand.name} {self.name}'

class Feature(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text='Пример: Кожен салон, Навигация, Подгрев на седалките',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Feature'
        verbose_name_plural = 'Features'

    def __str__(self):
        return self.name