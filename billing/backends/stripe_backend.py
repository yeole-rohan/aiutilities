"""
Stripe webhook handler (via dj-stripe 2.9+).

dj-stripe fires per-event Django signals via djstripe.signals.WEBHOOK_SIGNALS.
Connect receivers here; the URL uses djstripe's built-in ProcessWebhookView
which handles HMAC verification and DB storage automatically.
"""

import logging

from django.dispatch import receiver
from djstripe.signals import WEBHOOK_SIGNALS

from billing.models import Plan, Subscription

logger = logging.getLogger(__name__)


@receiver(WEBHOOK_SIGNALS["checkout.session.completed"])
def handle_checkout_completed(sender, event, **kwargs):
    session = event.data["object"]
    customer_id = session.get("customer", "")
    stripe_sub_id = session.get("subscription", "")
    org_id = (session.get("metadata") or {}).get("org_id")

    if not org_id:
        logger.warning("checkout.session.completed: no org_id in metadata")
        return

    from orgs.models import Organization
    try:
        org = Organization.objects.get(pk=org_id)
    except Organization.DoesNotExist:
        logger.error("checkout.session.completed: org %s not found", org_id)
        return

    sub, _ = Subscription.objects.get_or_create(org=org)
    sub.stripe_customer_id = customer_id
    sub.stripe_subscription_id = stripe_sub_id
    sub.status = Subscription.STATUS_ACTIVE
    sub.plan = Plan.PRO  # CUSTOMIZE: map price_id → plan
    sub.save()


@receiver(WEBHOOK_SIGNALS["customer.subscription.updated"])
def handle_subscription_updated(sender, event, **kwargs):
    stripe_sub = event.data["object"]
    try:
        sub = Subscription.objects.get(stripe_subscription_id=stripe_sub["id"])
        status = stripe_sub.get("status", "active")
        sub.status = status if status in dict(Subscription.STATUS_CHOICES) else Subscription.STATUS_ACTIVE
        sub.save(update_fields=["status"])
    except Subscription.DoesNotExist:
        pass


@receiver(WEBHOOK_SIGNALS["customer.subscription.deleted"])
def handle_subscription_deleted(sender, event, **kwargs):
    stripe_sub = event.data["object"]
    try:
        sub = Subscription.objects.get(stripe_subscription_id=stripe_sub["id"])
        sub.status = Subscription.STATUS_CANCELLED
        sub.plan = Plan.FREE
        sub.save(update_fields=["status", "plan"])
    except Subscription.DoesNotExist:
        pass
