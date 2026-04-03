from django.urls import path

from .views import (
    BrandListView,
    BrandCreateView,
    BrandUpdateView,
    BrandDeleteView,
    CarModelListView,
    CarModelCreateView,
    CarModelUpdateView,
    CarModelDeleteView,
    FeatureListView,
    FeatureCreateView,
    FeatureUpdateView,
    FeatureDeleteView,
)

urlpatterns = [
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/create/', BrandCreateView.as_view(), name='brand-create'),
    path('brands/<int:pk>/edit/', BrandUpdateView.as_view(), name='brand-edit'),
    path('brands/<int:pk>/delete/', BrandDeleteView.as_view(), name='brand-delete'),

    path('models/', CarModelListView.as_view(), name='car-model-list'),
    path('models/create/', CarModelCreateView.as_view(), name='car-model-create'),
    path('models/<int:pk>/edit/', CarModelUpdateView.as_view(), name='car-model-edit'),
    path('models/<int:pk>/delete/', CarModelDeleteView.as_view(), name='car-model-delete'),

    path('features/', FeatureListView.as_view(), name='feature-list'),
    path('features/create/', FeatureCreateView.as_view(), name='feature-create'),
    path('features/<int:pk>/edit/', FeatureUpdateView.as_view(), name='feature-edit'),
    path('features/<int:pk>/delete/', FeatureDeleteView.as_view(), name='feature-delete'),
]
