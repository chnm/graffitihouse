from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction 

from accounts.models import Student, Contributor, Volunteer, CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email',)

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email',)

class StudentSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student=True
        user.save()
        student = Student.objects.create(user=user)
        return user

class ContributorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student=True
        user.save()
        contributor = Contributor.objects.create(user=user)
        return user
    
class VolunteerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student=True
        user.save()
        volunteer = Volunteer.objects.create(user=user)
        return user