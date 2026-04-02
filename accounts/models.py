from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
phone_validator = RegexValidator(
    regex=r'^[0-9]{7,15}$',
    message='Въведи валиден телефонен номер, съдържащ само цифри.',
)
class Profile(models.Model):
    user = models.OneToOneField(User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[phone_validator],
    )
    location = models.CharField(
        max_length=100,
        blank=True,
    )

    is_dealer = models.BooleanField(default=False)
    info = models.TextField(blank=True)
    favorite_brands = models.ManyToManyField(
        'catalog.Brand',
        blank=True,
        related_name='favored_by_profiles',
    )

    class Meta:
        ordering = ['user__username']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'{self.user.username} profile'

class Favorite(models.Model):
    user = models.ForeignKey(User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'car')
        verbose_name = 'Favorite'


    def __str__(self):
        return f'{self.user.username} -> {self.car.title}'

