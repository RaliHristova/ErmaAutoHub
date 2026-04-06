
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from cars.models import Car
from .serializers import CarListSerializer, CarDetailSerializer
# Create your views here.
class CarListApiView(ListAPIView):
    serializer_class = CarListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Car.objects
            .filter(is_published=True, is_approved=True)
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features')
        )
class CarDetailApiView(RetrieveAPIView):
    serializer_class = CarDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Car.objects
            .filter(is_published=True, is_approved=True)
            .select_related('brand', 'car_model', 'owner')
            .prefetch_related('features')
        )