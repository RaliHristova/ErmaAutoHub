from django.urls import path

from .views import (
    InquiryCreateView,
    InquiryDeleteView,
    InquiryDetailView,
    InquiryUpdateView,
    MyInquiryListView,
    SellerInquiryListView,
)

urlpatterns = [
    path('create/<int:car_id>/', InquiryCreateView.as_view(), name='inquiry-create'),
    path('my/', MyInquiryListView.as_view(), name='my-inquiries'),
    path('received/', SellerInquiryListView.as_view(), name='seller-inquiries'),
    path('<int:pk>/', InquiryDetailView.as_view(), name='inquiry-details'),
    path('<int:pk>/edit/', InquiryUpdateView.as_view(), name='inquiry-edit'),
    path('<int:pk>/delete/', InquiryDeleteView.as_view(), name='inquiry-delete'),
]
