from user.models import Users
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class TestDaftarViews(TestCase):
    def setUp(self):
        self.full_name = "john doe"
        self.email = "johndoe12@gmail.com"
        self.password = "testjohndoe"
        self.masuk_url = reverse("user:masuk")
        self.keluar_url = reverse("user:keluar")
        self.daftar_url = reverse("user:daftar")
        self.home_url = reverse("home:home")
        self.user_obj = Users.objects.create_user(
            email=self.email, full_name=self.full_name, password=self.password)
        self.password1 = self.password
        self.password2 = self.password

    def test_1_daftar_GET(self):
        response = self.client.get(self.daftar_url)
        self.assertTemplateUsed(response, 'user/daftar.html')
        self.assertEqual(response.status_code, 200)

    def test_2_validasi_full_name_kosong_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": "", "email": self.email, "password1": self.password1, "password2": self.password2})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _("Full name is invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_2_1_validasi_full_name_spasi_kosong_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": " ", "email": self.email, "password1": self.password1, "password2": self.password2})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _("Full name is invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_2_2_validasi_full_name_space_diakhir_diawal_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": " word ", "email": self.email, "password1": self.password1, "password2": self.password2})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _("Full name is invalid"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')


    def test_2_3_validasi_full_name_spasi_banyak_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": "john  doe", "email": self.email, "password1": self.password1, "password2": self.password2})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _("The full name has too many spaces"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_3_validasi_email_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": self.full_name, "email": "emailinvalid", "password1": self.password1, "password2": self.password2})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _('Invalid email address'))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_4_1_validasi_password_tidak_sama_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": self.full_name, "email": self.email, "password1": self.password1, "password2": "TESTPASSWORDNOTEQUAL"})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _('Different Passwords'))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_4_2_validasi_password_kosong_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": self.full_name, "email": self.email, "password1": "", "password2": ""})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _(
            "Password cannot contain spaces or be empty"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_4_3_validasi_password_spasi_kosong_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": self.full_name, "email": self.email, "password1": "     ", "password2": "     "})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _(
            "Password cannot contain spaces or be empty"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_4_4_validasi_password_gagal_POST(self):
        data = {"full_name": self.full_name, "email": self.email,
                "password1": "admin", "password2": "admin"}
        response = self.client.post(self.daftar_url, data)
        try:
            validate_password(data["password1"])
        except ValidationError as e:
            expected_password_error = '\n '.join(e)
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, expected_password_error)
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')

    def test_5_validasi_email_sudah_digunakan_gagal_POST(self):
        response = self.client.post(self.daftar_url, {
                                    "full_name": self.full_name, "email": self.email, "password1": self.password1, "password2": self.password2})
        messages = list(response.context['messages'])
        message = str(messages[0])
        self.assertEqual(message, _("User with email already exists"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, 'user/daftar.html')


    def test_6_pengguna_daftar_berhasil_POST(self):
        full_name = "newjohndoe"
        email = "newjohndoe@gmail.com"
        password1 = "mysqladmin"
        password2 = "mysqladmin"
        response = self.client.post(self.daftar_url, {
                                    "full_name": full_name, "email": email, "password1": password1, "password2": password2})
        self.assertRedirects(response, self.masuk_url +
                             f"?command=verification&email={email}")
        
    def tearDown(self):
        self.user_obj.delete()