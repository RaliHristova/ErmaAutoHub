from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.roles import user_is_moderator

from .forms import BrandForm, CarModelForm, FeatureForm
from .models import Brand, CarModel, Feature


class ModeratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_is_moderator(self.request.user)


class BrandListView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = Brand
    template_name = 'catalog/brand-list.html'
    context_object_name = 'object_list'


class BrandCreateView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'catalog/brand-create.html'
    success_url = reverse_lazy('brand-list')
    success_message = 'Марката беше добавена успешно.'


class BrandUpdateView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'catalog/brand-edit.html'
    success_url = reverse_lazy('brand-list')
    success_message = 'Марката беше редактирана успешно.'


class BrandDeleteView(LoginRequiredMixin, ModeratorRequiredMixin, DeleteView):
    model = Brand
    template_name = 'catalog/brand-delete.html'
    success_url = reverse_lazy('brand-list')


class CarModelListView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = CarModel
    template_name = 'catalog/car-model-list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return CarModel.objects.select_related('brand')


class CarModelCreateView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, CreateView):
    model = CarModel
    form_class = CarModelForm
    template_name = 'catalog/car-model-create.html'
    success_url = reverse_lazy('car-model-list')
    success_message = 'Моделът беше добавен успешно.'


class CarModelUpdateView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CarModel
    form_class = CarModelForm
    template_name = 'catalog/car-model-edit.html'
    success_url = reverse_lazy('car-model-list')
    success_message = 'Моделът беше редактиран успешно.'


class CarModelDeleteView(LoginRequiredMixin, ModeratorRequiredMixin, DeleteView):
    model = CarModel
    template_name = 'catalog/car-model-delete.html'
    success_url = reverse_lazy('car-model-list')


class FeatureListView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = Feature
    template_name = 'catalog/feature-list.html'
    context_object_name = 'object_list'


class FeatureCreateView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, CreateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'catalog/feature-create.html'
    success_url = reverse_lazy('feature-list')
    success_message = 'Екстрата беше добавена успешно.'


class FeatureUpdateView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Feature
    form_class = FeatureForm
    template_name = 'catalog/feature-edit.html'
    success_url = reverse_lazy('feature-list')
    success_message = 'Екстрата беше редактирана успешно.'


class FeatureDeleteView(LoginRequiredMixin, ModeratorRequiredMixin, DeleteView):
    model = Feature
    template_name = 'catalog/feature-delete.html'
    success_url = reverse_lazy('feature-list')
