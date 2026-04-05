from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from cars.models import Car

from .forms import InquiryCreateForm, InquiryEditForm
from .models import Inquiry


class InquiryOwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().sender == self.request.user


class InquiryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Inquiry
    form_class = InquiryCreateForm
    template_name = 'inquiries/inquiry-create.html'
    success_message = 'Вашето запитване беше изпратено успешно.'

    def dispatch(self, request, *args, **kwargs):
        self.car = get_object_or_404(Car, pk=self.kwargs['car_id'], is_published=True, is_approved=True)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.sender = self.request.user
        form.instance.car = self.car
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('my-inquiries')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.car
        context['page_title'] = 'Изпращане на запитване'
        context['submit_label'] = 'Изпрати'
        return context


class MyInquiryListView(LoginRequiredMixin, ListView):
    model = Inquiry
    template_name = 'inquiries/my-inquiries.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return (
            Inquiry.objects
            .filter(sender=self.request.user)
            .select_related('car', 'car__brand', 'car__car_model', 'sender')
            .order_by('-created_at')
        )


class InquiryDetailView(LoginRequiredMixin, InquiryOwnerRequiredMixin, DetailView):
    model = Inquiry
    template_name = 'inquiries/inquiry-details.html'

    def get_queryset(self):
        return Inquiry.objects.select_related('car', 'car__brand', 'car__car_model', 'sender')


class InquiryUpdateView(LoginRequiredMixin, InquiryOwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Inquiry
    form_class = InquiryEditForm
    template_name = 'inquiries/inquiry-create.html'
    success_message = 'Запитването беше редактирано успешно.'

    def get_success_url(self):
        return reverse_lazy('inquiry-details', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.object.car
        context['page_title'] = 'Редакция на запитване'
        context['submit_label'] = 'Запази'
        return context


class InquiryDeleteView(LoginRequiredMixin, InquiryOwnerRequiredMixin, DeleteView):
    model = Inquiry
    template_name = 'inquiries/inquiry-delete.html'
    success_url = reverse_lazy('my-inquiries')


class SellerInquiryListView(LoginRequiredMixin, ListView):
    model = Inquiry
    template_name = 'inquiries/seller-inquiries.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return (
            Inquiry.objects
            .filter(car__owner=self.request.user)
            .select_related('car', 'sender', 'car__brand', 'car__car_model')
            .order_by('-created_at')
        )
