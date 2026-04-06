from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase

from cars.models import Car
from catalog.models import Brand, CarModel


def create_test_image():
    return SimpleUploadedFile(
        'car.gif',
        (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00'
            b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01'
            b'\x00\x3b'
        ),
        content_type='image/gif',
    )


class CarApiViewTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='api_owner',
            password='testpass123',
        )
        self.viewer = User.objects.create_user(
            username='api_viewer',
            password='testpass123',
        )
        self.brand = Brand.objects.create(name='Volkswagen')
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name='Passat',
        )
        self.published_car = Car.objects.create(
            owner=self.owner,
            brand=self.brand,
            car_model=self.car_model,
            title='VW Passat',
            price=22000,
            year=2021,
            mileage=80000,
            fuel_type='diesel',
            transmission='automatic',
            horsepower=190,
            color='White',
            description='Published approved car.',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )
        self.pending_car = Car.objects.create(
            owner=self.owner,
            brand=self.brand,
            car_model=self.car_model,
            title='VW Passat Pending',
            price=21000,
            year=2020,
            mileage=90000,
            fuel_type='diesel',
            transmission='manual',
            horsepower=150,
            color='Black',
            description='Pending car.',
            main_image=create_test_image(),
            is_published=True,
            is_approved=False,
        )

    def test_car_list_api_hides_price_for_anonymous_user(self):
        response = self.client.get(reverse('api-car-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertNotIn('price', response.data[0])

    def test_car_list_api_shows_price_for_authenticated_user(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(reverse('api-car-list'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['price'], '22000.00')

    def test_car_detail_api_hides_price_for_anonymous_user(self):
        response = self.client.get(reverse('api-car-detail', kwargs={'pk': self.published_car.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('price', response.data)

    def test_car_detail_api_returns_404_for_unapproved_car(self):
        response = self.client.get(reverse('api-car-detail', kwargs={'pk': self.pending_car.pk}))

        self.assertEqual(response.status_code, 404)
