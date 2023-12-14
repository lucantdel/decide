from rest_framework.test import APITestCase
from rest_framework import status

class AuthTestCase(APITestCase):

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


    def test_missing_password_(self):
        url = "/customuser/registrousuarios/"
        data = {
            'username': 'new_user',
            'email': 'new_user@example.com',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_passwordconf(self):
        url = "/customuser/registrousuarios/"
        data = {
            'username': 'new_user',
            'password': 'decidepass123',
            'email': 'new_user@example.com',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_email(self):
        url = "/customuser/registrousuarios/"
        data = {
            'username': 'new_user',
            'password': 'Short',
            'password_conf': 'Short',
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)