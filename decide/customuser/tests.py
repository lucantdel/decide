from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from base import mods

from rest_framework import status


class AuthTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        self.client = None

    def tearDown(self):
        self.client = None

    def test_register_user_get_page(self):
        url = "/customuser/registrousuarios/"

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_successful_registration(self):
        url = "/customuser/registrousuarios/"
        data = {
            'username': 'juan_car',
            'password': 'ContraSegUrA123',
            'email': 'juan@example.com',
            'password_conf': 'ContraSegUrA123',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_username_exists(self):
        url = "/customuser/registeruser/"
        self.assertTrue(User.objects.filter(username="voter1").exists())
        data = {
            "username": "voter1",
            "email": "new_user@example.com",
            "password": "thispasswordisactuallysecure123",
            "password_conf": "thispasswordisactuallysecure123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)

    def test_short_password_registration(self):
        url = "/customuser/registrousuarios/"
        data = {
            'username': 'new_user',
            'password': 'Short',
            'email': 'new_user@example.com',
            'password_conf': 'Short',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)