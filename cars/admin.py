from django.contrib import admin
from .models import Car, CarImage, CarReviewLog


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'brand', 'car_model')


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'alt_text')
    list_filter = ('car',)


@admin.register(CarReviewLog)
class CarReviewLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'submitted_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('car__title', 'submitted_by__username', 'message')
