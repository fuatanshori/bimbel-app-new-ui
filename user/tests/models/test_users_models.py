from user.models import Users
from django.test import TestCase
from django.utils.translation import gettext_lazy as _


class TestUserModels(TestCase):
    def setUp(self):
        self.admin = {"full_name": "admin",
                      "email": "admin@gmail.com", "password": "mysqladmin"}
        self.pelajar = {"full_name": "pelajar",
                        "email": "plajar@gmail.com", "password": "mysqladmin"}
    def test_admin_model_CREATE_SUPERUSER(self):
        user = Users.objects.create_superuser(
            full_name=self.admin["full_name"],
            email=self.admin["email"],
            password=self.admin["password"],
        )
        self.assertIsNone(user.id)
        self.assertEqual(user.full_name, self.admin["full_name"])
        self.assertEqual(user.email, self.admin["email"])
        self.assertTrue(user.check_password(self.admin["password"]))
        self.assertEqual(user.role, 'admin')

    def test_pelajar_model_CREATE_USER(self):
        user = Users.objects.create_user(
            full_name=self.pelajar["full_name"],
            email=self.pelajar["email"],
            password=self.pelajar["password"],
        )
        self.assertIsNone(user.id)
        self.assertEqual(user.full_name, self.pelajar["full_name"])
        self.assertEqual(user.email, self.pelajar["email"])
        self.assertTrue(user.check_password(self.pelajar["password"]))
        self.assertEqual(user.role, 'pelajar')

    def test_membuat_user_tanpa_email_gagal_CREATE_USER(self):
        with self.assertRaises(ValueError) as cm:
            user = Users.objects.create_user(
                full_name=self.pelajar["full_name"], email='', password=self.pelajar["password"])
            self.assertIsNone(user.id)
            self.assertEqual(user.full_name, self.pelajar["full_name"])
            self.assertEqual(user.email, self.pelajar["email"])
            self.assertTrue(user.check_password(self.pelajar["password"]))
            self.assertEqual(user.role, 'pelajar')
        self.assertEqual(str(cm.exception), _("The Email must be set"))

    def test_membuat_user_tanpa_full_name_gagal_CREATE_USER(self):
        with self.assertRaises(ValueError) as cm:
            user = Users.objects.create_user(
                full_name='', email=self.pelajar['email'], password=self.pelajar["password"])
            self.assertIsNone(user.id)
            self.assertEqual(user.full_name, self.pelajar["full_name"])
            self.assertEqual(user.email, self.pelajar["email"])
            self.assertTrue(user.check_password(self.pelajar["password"]))
            self.assertEqual(user.role, 'pelajar')
        self.assertEqual(str(cm.exception), _("The Full name must be set"))
