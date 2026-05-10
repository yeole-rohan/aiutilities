from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(user_signed_up)
def on_user_signed_up(sender, request, user, **kwargs):
    pass  # welcome email can be wired up when a mail backend is configured
