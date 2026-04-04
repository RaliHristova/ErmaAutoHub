from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from catalog.models import Brand, CarModel
from inquiries.models import Inquiry

from cars.forms import CarCreateForm
from cars.models import Car, CarImage, CarReviewLog
from cars.tasks import create_pending_review_log


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


class CarCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='seller',
            password='testpass123',
        )
        self.brand = Brand.objects.create(name='BMW')
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name='X5',
        )

    def test_create_view_returns_form_error_instead_of_500_when_price_is_missing(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('car-create'),
            data={
                'brand': self.brand.pk,
                'car_model': self.car_model.pk,
                'title': 'BMW X5 M Sport',
                'price': '',
                'year': 2024,
                'mileage': 12000,
                'fuel_type': 'diesel',
                'transmission': 'automatic',
                'horsepower': 286,
                'color': 'Black',
                'description': 'Excellent condition and full service history.',
                'main_image': create_test_image(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'price',
            ['This field is required.'],
        )


class CarListViewFilterTests(TestCase):
    def setUp(self):
        self.brand_bmw = Brand.objects.create(name='BMW')
        self.brand_audi = Brand.objects.create(name='Audi')
        self.model_x5 = CarModel.objects.create(brand=self.brand_bmw, name='X5')
        self.model_x3 = CarModel.objects.create(brand=self.brand_bmw, name='X3')
        self.model_a6 = CarModel.objects.create(brand=self.brand_audi, name='A6')
        self.owner = User.objects.create_user(username='owner_filter', password='testpass123')

        Car.objects.create(
            owner=self.owner,
            brand=self.brand_bmw,
            car_model=self.model_x5,
            title='BMW X5',
            price=50000,
            year=2023,
            mileage=10000,
            fuel_type='diesel',
            transmission='automatic',
            horsepower=300,
            color='Black',
            description='BMW X5 description',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )
        Car.objects.create(
            owner=self.owner,
            brand=self.brand_bmw,
            car_model=self.model_x3,
            title='BMW X3',
            price=40000,
            year=2022,
            mileage=12000,
            fuel_type='diesel',
            transmission='automatic',
            horsepower=250,
            color='Blue',
            description='BMW X3 description',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )
        Car.objects.create(
            owner=self.owner,
            brand=self.brand_audi,
            car_model=self.model_a6,
            title='Audi A6',
            price=45000,
            year=2021,
            mileage=15000,
            fuel_type='petrol',
            transmission='automatic',
            horsepower=240,
            color='Gray',
            description='Audi A6 description',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )

    def test_list_view_filters_by_brand_and_model(self):
        response = self.client.get(
            reverse('car-list'),
            data={
                'brand': self.brand_bmw.pk,
                'car_model': self.model_x5.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cars_count'], 1)
        self.assertEqual(
            [car.title for car in response.context['object_list']],
            ['BMW X5'],
        )


class CarFormValidationTests(TestCase):
    def test_create_form_rejects_model_from_another_brand(self):
        brand_bmw = Brand.objects.create(name='BMW')
        brand_audi = Brand.objects.create(name='Audi')
        audi_model = CarModel.objects.create(brand=brand_audi, name='A6')

        form = CarCreateForm(data={
            'brand': brand_bmw.pk,
            'car_model': audi_model.pk,
            'title': 'Invalid brand model pair',
            'price': 10000,
            'year': 2020,
            'mileage': 150000,
            'fuel_type': 'diesel',
            'transmission': 'automatic',
            'horsepower': 150,
            'color': 'Black',
            'description': 'Test description with enough length.',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('car_model', form.errors)


class CarTemplateTagTests(TestCase):
    def test_currency_eur_filter_formats_whole_number(self):
        template = Template('{% load car_tags %}{{ price|currency_eur }}')
        rendered = template.render(Context({'price': 25000}))

        self.assertEqual(rendered, '25 000 EUR')

    def test_nav_match_returns_true_for_matching_route_name(self):
        template = Template('{% load navigation_tags %}{% nav_match current_url "car-list,car-details" as is_cars %}{{ is_cars }}')
        rendered = template.render(Context({'current_url': 'car-details'}))

        self.assertEqual(rendered, 'True')


class CarReviewLogTaskTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='log_owner',
            password='testpass123',
        )
        self.brand = Brand.objects.create(name='Skoda')
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name='Octavia',
        )
        self.car = Car.objects.create(
            owner=self.owner,
            brand=self.brand,
            car_model=self.car_model,
            title='Skoda Octavia',
            price=18000,
            year=2020,
            mileage=95000,
            fuel_type='diesel',
            transmission='manual',
            horsepower=150,
            color='White',
            description='Family car in good condition.',
            main_image=create_test_image(),
            is_published=True,
            is_approved=False,
        )

    def test_create_pending_review_log_creates_log_record(self):
        async_to_sync(create_pending_review_log)(self.car.pk)

        review_log = CarReviewLog.objects.get(car=self.car)
        self.assertEqual(review_log.submitted_by, self.owner)
        self.assertEqual(review_log.status, CarReviewLog.StatusChoices.PENDING_REVIEW)
        self.assertEqual(review_log.message, 'Обявата е изпратена за модераторско одобрение.')


class InquiryOwnerCrudTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='dealer_owner', password='testpass123')
        self.sender = User.objects.create_user(username='sender_user', password='testpass123')
        self.other_user = User.objects.create_user(username='other_user', password='testpass123')
        self.brand = Brand.objects.create(name='Toyota')
        self.car_model = CarModel.objects.create(brand=self.brand, name='Corolla')
        self.car = Car.objects.create(
            owner=self.owner,
            brand=self.brand,
            car_model=self.car_model,
            title='Toyota Corolla',
            price=14000,
            year=2019,
            mileage=80000,
            fuel_type='petrol',
            transmission='manual',
            horsepower=132,
            color='Red',
            description='Compact sedan in great condition.',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )
        self.inquiry = Inquiry.objects.create(
            car=self.car,
            sender=self.sender,
            phone_number='0888123456',
            message='Interested in inspection and service history.',
        )

    def test_sender_can_view_and_edit_own_inquiry(self):
        self.client.force_login(self.sender)

        detail_response = self.client.get(reverse('inquiry-details', kwargs={'pk': self.inquiry.pk}))
        edit_response = self.client.post(
            reverse('inquiry-edit', kwargs={'pk': self.inquiry.pk}),
            data={
                'phone_number': '0888999999',
                'message': 'Interested in inspection and full service history.',
            },
        )

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(edit_response.status_code, 302)
        self.inquiry.refresh_from_db()
        self.assertEqual(self.inquiry.phone_number, '0888999999')

    def test_non_owner_cannot_open_inquiry_detail(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse('inquiry-details', kwargs={'pk': self.inquiry.pk}))

        self.assertEqual(response.status_code, 403)

class CarImageOwnerCrudTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='image_owner', password='testpass123')
        self.other_user = User.objects.create_user(username='image_other', password='testpass123')
        self.brand = Brand.objects.create(name='Ford')
        self.car_model = CarModel.objects.create(brand=self.brand, name='Focus')
        self.car = Car.objects.create(
            owner=self.owner,
            brand=self.brand,
            car_model=self.car_model,
            title='Ford Focus',
            price=9000,
            year=2018,
            mileage=120000,
            fuel_type='diesel',
            transmission='manual',
            horsepower=120,
            color='Blue',
            description='Practical hatchback.',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )
        self.image = CarImage.objects.create(
            car=self.car,
            image=create_test_image(),
            alt_text='Front view',
        )

    def test_owner_can_add_gallery_image(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('car-image-create', kwargs={'car_pk': self.car.pk}),
            data={
                'image': create_test_image(),
                'alt_text': 'Rear view',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CarImage.objects.filter(car=self.car).count(), 2)

    def test_non_owner_cannot_access_gallery_management(self):
        self.client.force_login(self.other_user)

        response = self.client.get(reverse('car-image-list', kwargs={'car_pk': self.car.pk}))

        self.assertEqual(response.status_code, 403)
