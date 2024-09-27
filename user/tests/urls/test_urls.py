from django.test import TestCase
from django.urls import reverse,resolve
from user.views import masuk,keluar,daftar,aktifasi,lupaPassword,resetPassword


class TestUrls(TestCase):
    def test_masuk_urls_resolved(self):
        url = reverse("user:masuk")
        self.assertEqual(resolve(url).func,masuk)

    def test_keluar_urls_resolved(self):
        url = reverse("user:keluar")
        self.assertEqual(resolve(url).func,keluar)
        
    def test_daftar_urls_resolved(self):
        url = reverse("user:daftar")
        self.assertEqual(resolve(url).func,daftar)
        
    def test_aktifasi_urls_resolved(self):
        url = reverse("user:aktifasi",args=["uidb64","token"])
        self.assertEqual(resolve(url).func,aktifasi)
    
    def test_lupapassword_urls_resolved(self):
        url = reverse("user:lupapassword")
        self.assertEqual(resolve(url).func,lupaPassword)
    
    def test_resetpassword_urls_resolved(self):
        url = reverse("user:resetpassword", args=["uidb64", "token"])
        self.assertEqual(resolve(url).func,resetPassword)
        
        