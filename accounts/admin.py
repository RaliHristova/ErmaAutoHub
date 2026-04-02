from django.contrib import admin

from .models import Profile, Favorite

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone_number', 'location', 'is_dealer')
    search_fields = ('user__username', 'phone_number', 'location')
    list_filter = ('is_dealer',)
    filter_horizontal = ('favorite_brands',)
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car', 'created_at')
    search_fields = ('user__username', 'car__title')
    list_filter = ('created_at',)
