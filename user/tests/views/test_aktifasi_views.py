from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from user.token import account_activation_token
from user.views import aktifasi  # Assuming aktifasi is the view function to be tested
import base64

class UserActivationTest(TestCase):
    def setUp(self):
        self.full_name = "john doe"
        self.email = "johndoe12@gmail.com"
        self.password = "testjohndoe"
        self.factory = RequestFactory()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(email=self.email, full_name=self.full_name, password=self.password)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = account_activation_token.make_token(self.user)

    def test_successful_activation(self):
        request = self.factory.get(reverse("user:aktifasi", kwargs={"uidb64": self.uidb64, "token": self.token}))
        request.user = AnonymousUser()
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        request._messages = messages
        
        response = aktifasi(request, self.uidb64, self.token)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNotNone(self.user.waktu_aktifasi)
        self.assertEqual(str(request._messages._queued_messages[0]), f'Selamat {self.user.full_name}, akunmu telah aktif.')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user:masuk'))

    def test_invalid_uidb64(self):
        invalid_uidb64 = base64.urlsafe_b64encode(b'invalid_uid').decode()
        request = self.factory.get(reverse("user:aktifasi", kwargs={"uidb64": invalid_uidb64, "token": self.token}))
        request.user = AnonymousUser()
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        request._messages = messages
        
        response = aktifasi(request, invalid_uidb64, self.token)
        
        self.assertEqual(str(request._messages._queued_messages[0]), 'Link Token tidak valid.')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user:daftar'))

    def test_invalid_token(self):
        invalid_token = 'invalid-token'
        request = self.factory.get(reverse("user:aktifasi", kwargs={"uidb64": self.uidb64, "token": invalid_token}))
        request.user = AnonymousUser()
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        request._messages = messages
        
        response = aktifasi(request, self.uidb64, invalid_token)
        
        self.assertEqual(str(request._messages._queued_messages[0]), 'Link Token tidak valid.')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('user:daftar'))
