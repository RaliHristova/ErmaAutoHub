from django.urls import path

from .views import CarListApiView, CarDetailApiView

urlpatterns = [
    path('cars/', CarListApiView.as_view(), name='api-car-list'),
    path('cars/<int:pk>/', CarDetailApiView.as_view(), name='api-car-detail'),
]