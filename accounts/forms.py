from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from unfold.forms import UserChangeForm as UnfoldUserChangeForm
from unfold.forms import UserCreationForm as UnfoldUserCreationForm

from accounts.models import Contributor, CustomUser, Student, Volunteer


class CustomUserCreationForm(UnfoldUserCreationForm):
    class Meta(UnfoldUserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
        )


class CustomUserChangeForm(UnfoldUserChangeForm):
    class Meta(UnfoldUserChangeForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
        )


class StudentSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.save()
        Student.objects.create(user=user)
        return user


class ContributorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_contributor = True
        user.save()
        Contributor.objects.create(user=user)
        return user


class VolunteerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_volunteer = True
        user.save()
        Volunteer.objects.create(user=user)
        return user
