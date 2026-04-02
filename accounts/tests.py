from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from cars.models import Car
from catalog.models import Brand, CarModel

from .roles import (
    DEALERS_GROUP_NAME,
    MODERATORS_GROUP_NAME,
    ensure_role_groups,
    user_is_admin,
    user_is_moderator,
)


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


class RoleGroupTests(TestCase):
    def test_default_groups_are_created(self):
        ensure_role_groups()

        self.assertTrue(Group.objects.filter(name=DEALERS_GROUP_NAME).exists())
        self.assertTrue(Group.objects.filter(name=MODERATORS_GROUP_NAME).exists())

    def test_regular_user_is_added_to_dealers_group(self):
        user = User.objects.create_user(
            username='dealer_user',
            password='testpass123',
        )

        self.assertTrue(user.groups.filter(name=DEALERS_GROUP_NAME).exists())

    def test_plain_staff_user_is_not_treated_as_moderator(self):
        user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            is_staff=True,
        )

        self.assertFalse(user_is_moderator(user))

    def test_moderator_group_member_is_treated_as_moderator(self):
        ensure_role_groups()
        user = User.objects.create_user(
            username='moderator_user',
            password='testpass123',
        )
        moderators_group = Group.objects.get(name=MODERATORS_GROUP_NAME)
        user.groups.add(moderators_group)

        self.assertTrue(user_is_moderator(user))

    def test_superuser_is_treated_as_moderator(self):
        user = User.objects.create_superuser(
            username='super_admin',
            email='admin@example.com',
            password='testpass123',
        )

        self.assertTrue(user_is_admin(user))
        self.assertTrue(user_is_moderator(user))


class FavoriteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='favorite_user',
            password='testpass123',
        )
        self.owner = User.objects.create_user(
            username='owner_user',
            password='testpass123',
        )
        self.brand = Brand.objects.create(name='Mercedes')
        self.car_model = CarModel.objects.create(
            brand=self.brand,
            name='E220',
        )
        self.car = Car.objects.create(
            owner=self.owner,
            brand=self.brand,
            car_model=self.car_model,
            title='Mercedes E220',
            price=30000,
            year=2021,
            mileage=55000,
            fuel_type='diesel',
            transmission='automatic',
            horsepower=194,
            color='Silver',
            description='Reliable sedan.',
            main_image=create_test_image(),
            is_published=True,
            is_approved=True,
        )

    def test_add_favorite_creates_favorite_record(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('add-favorite', kwargs={'car_id': self.car.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.user.favorites.filter(car=self.car).exists())

    def test_remove_favorite_deletes_favorite_record(self):
        self.user.favorites.create(car=self.car)
        self.client.force_login(self.user)

        response = self.client.post(reverse('remove-favorite', kwargs={'car_id': self.car.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.user.favorites.filter(car=self.car).exists())


class ProfileFavoriteBrandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='profile_user',
            password='testpass123',
        )
        self.brand_bmw = Brand.objects.create(name='BMW')
        self.brand_audi = Brand.objects.create(name='Audi')

    def test_profile_edit_saves_favorite_brands(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile-edit'),
            data={
                'phone_number': '0888123456',
                'location': 'Sofia',
                'info': 'Active buyer',
                'favorite_brands': [self.brand_bmw.pk, self.brand_audi.pk],
                'is_dealer': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(
            list(self.user.profile.favorite_brands.order_by('name').values_list('name', flat=True)),
            ['Audi', 'BMW'],
        )
