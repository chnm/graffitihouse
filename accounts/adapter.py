from allauth.account.adapter import DefaultAccountAdapter


class InviteOnlyAccountAdapter(DefaultAccountAdapter):
    """Accounts are created by staff in the admin; there is no public signup."""

    def is_open_for_signup(self, request):
        return False
