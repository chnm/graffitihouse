from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class LoginTests(TestCase):
    def test_signup_is_closed(self):
        response = self.client.get(reverse("account_signup"))
        self.assertTemplateUsed(response, "account/signup_closed.html")

    def test_existing_user_receives_login_code_by_email(self):
        get_user_model().objects.create_user("jane", "jane@example.org")

        response = self.client.post(
            reverse("account_request_login_code"), {"email": "jane@example.org"}
        )

        self.assertRedirects(response, reverse("account_confirm_login_code"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["jane@example.org"])

    def test_admin_login_uses_allauth(self):
        response = self.client.get("/admin/login/?next=/admin/")
        self.assertRedirects(
            response,
            reverse("account_login") + "?next=/admin/",
            fetch_redirect_response=False,
        )

    def test_login_with_username_or_email_and_password(self):
        get_user_model().objects.create_user("jane", "jane@example.org", "pw-123456")
        for login in ("jane", "jane@example.org"):
            self.client.logout()
            response = self.client.post(
                reverse("account_login"), {"login": login, "password": "pw-123456"}
            )
            self.assertRedirects(response, "/admin/", fetch_redirect_response=False)
