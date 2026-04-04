from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.roles import user_is_moderator

from .forms import (
    CarApproveForm,
    CarCreateForm,
    CarDeleteForm,
    CarEditForm,
    CarFilterForm,
    CarImageForm,
)
from .models import Car, CarImage
from .tasks import enqueue_pending_review_log


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user


class ModeratorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return user_is_moderator(self.request.user)


class CarImageOwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().car.owner == self.request.user


class CarImageCarOwnerMixin(UserPassesTestMixin):
    car = None

    def dispatch(self, request, *args, **kwargs):
        self.car = get_object_or_404(Car, pk=self.kwargs['car_pk'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.car is not None and self.car.owner == self.request.user


class CarListView(ListView):
    model = Car
    template_name = 'cars/car-list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        queryset = (
            Car.objects
            .filter(is_published=True, is_approved=True)
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features')
        )

        self.filter_form = CarFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            brand = self.filter_form.cleaned_data.get('brand')
            car_model = self.filter_form.cleaned_data.get('car_model')
            fuel_type = self.filter_form.cleaned_data.get('fuel_type')
            transmission = self.filter_form.cleaned_data.get('transmission')
            min_year = self.filter_form.cleaned_data.get('min_year')
            max_year = self.filter_form.cleaned_data.get('max_year')
            min_price = self.filter_form.cleaned_data.get('min_price')
            max_price = self.filter_form.cleaned_data.get('max_price')
            sort_by = self.filter_form.cleaned_data.get('sort_by')

            if brand:
                queryset = queryset.filter(brand=brand)

            if car_model:
                queryset = queryset.filter(car_model=car_model)

            if fuel_type:
                queryset = queryset.filter(fuel_type=fuel_type)

            if transmission:
                queryset = queryset.filter(transmission=transmission)

            if min_year is not None:
                queryset = queryset.filter(year__gte=min_year)

            if max_year is not None:
                queryset = queryset.filter(year__lte=max_year)

            if min_price is not None:
                queryset = queryset.filter(price__gte=min_price)

            if max_price is not None:
                queryset = queryset.filter(price__lte=max_price)

            if sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort_by == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort_by == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort_by == 'year_desc':
                queryset = queryset.order_by('-year')
            elif sort_by == 'mileage_asc':
                queryset = queryset.order_by('mileage')

        self.filtered_queryset = queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(self, 'filter_form', CarFilterForm())
        context['cars_count'] = getattr(self, 'filtered_queryset', self.object_list).count()
        return context


class CarDetailView(DetailView):
    model = Car
    template_name = 'cars/car-details.html'

    def get_queryset(self):
        return (
            Car.objects
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features', 'favorites', 'images')
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        user = self.request.user

        if obj.is_published and obj.is_approved:
            return obj

        if user.is_authenticated and (obj.owner == user or user_is_moderator(user)):
            return obj

        raise Http404('Тази обява не е налична.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_favorite'] = (
            self.request.user.is_authenticated
            and self.object.favorites.filter(user=self.request.user).exists()
        )
        return context


class CarCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Car
    form_class = CarCreateForm
    template_name = 'cars/car-create.html'
    success_message = 'Обявата беше създадена успешно.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_published = True
        form.instance.is_approved = False
        response = super().form_valid(form)
        enqueue_pending_review_log(self.object.pk)
        return response

    def get_success_url(self):
        return reverse_lazy('car-details', kwargs={'pk': self.object.pk})


class CarUpdateView(LoginRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Car
    form_class = CarEditForm
    template_name = 'cars/car-edit.html'
    success_message = 'Обявата беше редактирана успешно.'

    def form_valid(self, form):
        form.instance.is_approved = False
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('car-details', kwargs={'pk': self.object.pk})


class CarDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Car
    template_name = 'cars/car-delete.html'
    success_url = reverse_lazy('my-cars')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CarDeleteForm(instance=self.object)
        return context


class MyCarsListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'cars/my-cars.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return (
            Car.objects
            .filter(owner=self.request.user)
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features')
        )


class PendingCarsListView(LoginRequiredMixin, ModeratorRequiredMixin, ListView):
    model = Car
    template_name = 'cars/pending-cars.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return (
            Car.objects
            .filter(is_approved=False, is_published=True)
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features')
        )


class CarApproveView(LoginRequiredMixin, ModeratorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Car
    form_class = CarApproveForm
    template_name = 'cars/car-approve.html'
    success_url = reverse_lazy('pending-cars')
    success_message = 'Обявата беше одобрена успешно.'


class CarImageListView(LoginRequiredMixin, CarImageCarOwnerMixin, ListView):
    model = CarImage
    template_name = 'cars/car-image-list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return CarImage.objects.filter(car=self.car).select_related('car')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.car
        return context


class CarImageCreateView(LoginRequiredMixin, CarImageCarOwnerMixin, SuccessMessageMixin, CreateView):
    model = CarImage
    form_class = CarImageForm
    template_name = 'cars/car-image-form.html'
    success_message = 'Снимката беше добавена успешно.'

    def form_valid(self, form):
        form.instance.car = self.car
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('car-image-list', kwargs={'car_pk': self.car.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.car
        context['page_title'] = 'Добавяне на снимка'
        context['submit_label'] = 'Добави'
        return context


class CarImageUpdateView(LoginRequiredMixin, CarImageOwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CarImage
    form_class = CarImageForm
    template_name = 'cars/car-image-form.html'
    success_message = 'Снимката беше редактирана успешно.'

    def get_success_url(self):
        return reverse_lazy('car-image-list', kwargs={'car_pk': self.object.car.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['car'] = self.object.car
        context['page_title'] = 'Редакция на снимка'
        context['submit_label'] = 'Запази'
        return context


class CarImageDeleteView(LoginRequiredMixin, CarImageOwnerRequiredMixin, DeleteView):
    model = CarImage
    template_name = 'cars/car-image-delete.html'

    def get_success_url(self):
        return reverse_lazy('car-image-list', kwargs={'car_pk': self.object.car.pk})
