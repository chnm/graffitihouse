from django.test import TestCase

from .forms import ContributorSignUpForm, StudentSignUpForm, VolunteerSignUpForm
from .models import Contributor, Student, Volunteer


class SignupFormTests(TestCase):
    def test_signup_forms_set_their_role_and_create_a_profile(self):
        cases = (
            (StudentSignUpForm, "is_student", Student),
            (ContributorSignUpForm, "is_contributor", Contributor),
            (VolunteerSignUpForm, "is_volunteer", Volunteer),
        )

        for index, (form_class, role_field, profile_model) in enumerate(cases):
            with self.subTest(role=role_field):
                form = form_class(
                    data={
                        "username": f"user-{index}",
                        "password1": "a-secure-test-password",
                        "password2": "a-secure-test-password",
                    }
                )

                self.assertTrue(form.is_valid(), form.errors)
                user = form.save()
                self.assertTrue(getattr(user, role_field))
                self.assertTrue(profile_model.objects.filter(user=user).exists())
