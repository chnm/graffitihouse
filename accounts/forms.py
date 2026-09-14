from unfold.forms import UserChangeForm as UnfoldUserChangeForm
from unfold.forms import UserCreationForm as UnfoldUserCreationForm

from accounts.models import CustomUser


class CustomUserCreationForm(UnfoldUserCreationForm):
    class Meta(UnfoldUserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UnfoldUserChangeForm):
    class Meta(UnfoldUserChangeForm.Meta):
        model = CustomUser
        fields = ("username", "email")
