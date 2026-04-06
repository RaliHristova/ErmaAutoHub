from rest_framework import serializers

from cars.models import Car


class CarListSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name')
    car_model = serializers.CharField(source='car_model.name')
    fuel_type = serializers.CharField(source='get_fuel_type_display')
    transmission = serializers.CharField(source='get_transmission_display')

    class Meta:
        model = Car
        fields = (
            'id',
            'title',
            'brand',
            'car_model',
            'year',
            'mileage',
            'fuel_type',
            'transmission',
            'price',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            data.pop('price', None)

        return data
class CarDetailSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name')
    car_model = serializers.CharField(source='car_model.name')
    fuel_type = serializers.CharField(source='get_fuel_type_display')
    transmission = serializers.CharField(source='get_transmission_display')
    owner = serializers.CharField(source='owner.username')
    features = serializers.StringRelatedField(many=True)

    class Meta:
        model = Car
        fields = (
            'id',
            'title',
            'brand',
            'car_model',
            'year',
            'mileage',
            'fuel_type',
            'transmission',
            'horsepower',
            'color',
            'description',
            'owner',
            'features',
            'price',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            data.pop('price', None)

        return data