from django.shortcuts import render
from django.views.generic import TemplateView

from cars.models import Car


class HomePageView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_cars'] = (
            Car.objects
            .filter(is_published=True, is_approved=True)
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features')[:6]
        )
        return context

