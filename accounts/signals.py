from allauth.account.signals import user_signed_up
from django.dispatch import receiver

from tasks.email import send_welcome_email


@receiver(user_signed_up)
def on_user_signed_up(sender, request, user, **kwargs):
    send_welcome_email.delay(user.pk)
