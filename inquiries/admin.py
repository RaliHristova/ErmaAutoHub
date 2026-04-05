from django.contrib import admin

from .models import Inquiry

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'sender', 'phone_number', 'created_at')
    search_fields = ('car__title', 'sender__username', 'phone_number')
    list_filter = ('created_at',)
