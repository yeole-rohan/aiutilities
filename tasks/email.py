from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email(self, user_pk: int) -> None:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return
    try:
        send_mail(
            subject="Welcome!",
            message=(
                f"Hi {user.first_name or user.email},\n\n"
                "Welcome aboard. Head to your dashboard to get started.\n\n"
                "— The team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_invite_email(self, invite_pk: int, base_url: str) -> None:
    from orgs.models import Invite
    try:
        invite = Invite.objects.select_related("org", "invited_by").get(pk=invite_pk)
    except Invite.DoesNotExist:
        return
    accept_url = f"{base_url.rstrip('/')}/dashboard/invite/{invite.token}/"
    try:
        send_mail(
            subject=f"You're invited to join {invite.org.name}",
            message=(
                f"Hi,\n\n"
                f"{invite.invited_by} has invited you to join {invite.org.name}.\n\n"
                f"Accept the invite: {accept_url}\n\n"
                "— The team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invite.email],
        )
    except Exception as exc:
        raise self.retry(exc=exc)
