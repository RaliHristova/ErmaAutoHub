from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models

# Create your models here.
phone_validator = RegexValidator(
    regex=r'^[0-9]{7,15}$',
    message='Въведи валиден телефонен номер , съдържащ само цифри.',
)


class Inquiry(models.Model):
    car = models.ForeignKey(
        'cars.Car',
        on_delete=models.CASCADE,
        related_name='inquiries',
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_inquiries',
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[phone_validator],
    )
    message = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text='Minimum 10 characters.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inquiry'

    def __str__(self):
        return f'Inquiry by {self.sender.username} for {self.car.title}'