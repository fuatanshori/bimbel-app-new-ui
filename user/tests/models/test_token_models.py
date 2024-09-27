from user.models import Users, Token
from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator

class TestTokenModels(TestCase):
    def setUp(self):
        self.user = {"full_name": "john",
                        "email": "johndoe@gmail.com", "password": "mysqladmin"}
        self.user = Users.objects.create_user(
            full_name=self.user["full_name"],
            email=self.user["email"],
            password=self.user["password"],
        )
    def test_create_token(self):
        token = default_token_generator.make_token(self.user)
        token_obj = Token.objects.create(
            user=self.user,
            token=token,
            is_created=True,
        )
        token_obj.save()
        self.assertFalse(token_obj.is_used)
        self.assertEqual(token_obj.token, token)
        self.assertEqual(token_obj.user, self.user)
        self.assertTrue(token_obj.is_created)
    
    def tearDown(self):
        self.user.delete