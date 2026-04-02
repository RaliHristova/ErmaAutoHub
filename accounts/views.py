from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from cars.models import Car

from .forms import ProfileEditForm, UserRegisterForm
from .models import Favorite, Profile


class RegisterView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    success_message = 'Твоят акаунт беше създаден успешно.'


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile-details.html'

    def get_queryset(self):
        return Profile.objects.select_related('user').prefetch_related('favorite_brands')

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return queryset.get(user=self.request.user)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = 'accounts/profile-edit.html'
    success_url = reverse_lazy('profile-details')
    success_message = 'Твоят профил беше актуализиран успешно.'

    def get_object(self):
        return self.request.user.profile


class FavoriteCarsListView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'accounts/favorite-cars.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return (
            Favorite.objects
            .filter(user=self.request.user)
            .select_related('car', 'car__brand', 'car__car_model')
        )


class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, car_id, *args, **kwargs):
        car = get_object_or_404(Car, pk=car_id, is_published=True, is_approved=True)

        Favorite.objects.get_or_create(
            user=request.user,
            car=car,
        )

        messages.success(request, 'Автомобилът беше добавен в любими.')
        return HttpResponseRedirect(
            request.META.get('HTTP_REFERER', reverse_lazy('car-details', kwargs={'pk': car_id}))
        )


class RemoveFavoriteView(LoginRequiredMixin, View):
    def post(self, request, car_id, *args, **kwargs):
        car = get_object_or_404(Car, pk=car_id)

        Favorite.objects.filter(
            user=request.user,
            car=car,
        ).delete()

        messages.success(request, 'Автомобилът беше премахнат от любими.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse_lazy('favorite-cars')))
