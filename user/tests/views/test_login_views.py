from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from http import HTTPStatus

class MasukViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('user:masuk')
        self.user_model = get_user_model()
        self.email = 'test@example.com'
        self.full_name = 'test'
        self.password = 'password123'
        self.user = self.user_model.objects.create_user(
            full_name = self.full_name,
            email=self.email,
            password=self.password,
            is_active=True
        )

    def test_authenticated_user_redirects_to_home(self):
        self.client.login(email=self.email, password=self.password)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home:home'), status_code=302)

    def test_get_request_renders_login_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'user/masuk.html')

    def test_post_request_with_valid_credentials_redirects_to_home(self):
        response = self.client.post(self.url, {'email': self.email, 'password': self.password})
        self.assertRedirects(response, reverse('home:home'), status_code=302)

    def test_post_request_with_invalid_credentials_shows_error_message(self):
        response = self.client.post(self.url, {'email': self.email, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertTemplateUsed(response, 'user/masuk.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Email Atau Password Salah' in str(message) for message in messages))

    def test_post_request_with_inactive_user_shows_activation_message(self):
        inactive_user = self.user_model.objects.create_user(
            email='inactive@example.com',
            password=self.password,
            is_active=False,
            full_name = self.full_name,
        )
        response = self.client.post(self.url, {'email': inactive_user.email, 'password': self.password})
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertTemplateUsed(response, 'user/masuk.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Silahkan aktivasi akun melalui email. hubungi admin jika blum mendapatkan token' in str(message) for message in messages))
