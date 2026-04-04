from django.urls import path

from .views import (
    CarApproveView,
    CarCreateView,
    CarDeleteView,
    CarDetailView,
    CarImageCreateView,
    CarImageDeleteView,
    CarImageListView,
    CarImageUpdateView,
    CarListView,
    CarUpdateView,
    MyCarsListView,
    PendingCarsListView,
)

urlpatterns = [
    path('', CarListView.as_view(), name='car-list'),
    path('create/', CarCreateView.as_view(), name='car-create'),
    path('my-cars/', MyCarsListView.as_view(), name='my-cars'),
    path('pending/', PendingCarsListView.as_view(), name='pending-cars'),
    path('<int:pk>/', CarDetailView.as_view(), name='car-details'),
    path('<int:pk>/edit/', CarUpdateView.as_view(), name='car-edit'),
    path('<int:pk>/delete/', CarDeleteView.as_view(), name='car-delete'),
    path('<int:pk>/approve/', CarApproveView.as_view(), name='car-approve'),
    path('<int:car_pk>/images/', CarImageListView.as_view(), name='car-image-list'),
    path('<int:car_pk>/images/add/', CarImageCreateView.as_view(), name='car-image-create'),
    path('images/<int:pk>/edit/', CarImageUpdateView.as_view(), name='car-image-edit'),
    path('images/<int:pk>/delete/', CarImageDeleteView.as_view(), name='car-image-delete'),
]
