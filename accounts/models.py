from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Roles are Django groups; see accounts/migrations for the defaults."""
