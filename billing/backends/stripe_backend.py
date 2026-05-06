"""
Stripe webhook handler (via dj-stripe).
Register this at /billing/stripe/webhook/ in urls.py.
"""

import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djstripe import webhooks

from billing.models import Plan, Subscription

logger = logging.getLogger(__name__)


def _get_or_create_subscription(org):
    sub, _ = Subscription.objects.get_or_create(org=org)
    return sub


@webhooks.handler("checkout.session.completed")
def handle_checkout_completed(event, **kwargs):
    session = event.data["object"]
    customer_id = session.get("customer")
    stripe_sub_id = session.get("subscription")
    metadata = session.get("metadata", {})
    org_id = metadata.get("org_id")

    if not org_id:
        logger.warning("checkout.session.completed: no org_id in metadata")
        return

    from orgs.models import Organization
    try:
        org = Organization.objects.get(pk=org_id)
    except Organization.DoesNotExist:
        logger.error("checkout.session.completed: org %s not found", org_id)
        return

    sub = _get_or_create_subscription(org)
    sub.stripe_customer_id = customer_id or ""
    sub.stripe_subscription_id = stripe_sub_id or ""
    sub.status = Subscription.STATUS_ACTIVE
    # CUSTOMIZE: map Stripe price ID → plan
    sub.plan = Plan.PRO
    sub.save()
    logger.info("Stripe checkout completed for org %s", org_id)


@webhooks.handler("customer.subscription.updated")
def handle_subscription_updated(event, **kwargs):
    stripe_sub = event.data["object"]
    sub_id = stripe_sub.get("id")
    status = stripe_sub.get("status", "active")

    try:
        sub = Subscription.objects.get(stripe_subscription_id=sub_id)
    except Subscription.DoesNotExist:
        return

    sub.status = status if status in dict(Subscription.STATUS_CHOICES) else Subscription.STATUS_ACTIVE
    sub.save(update_fields=["status"])


@webhooks.handler("customer.subscription.deleted")
def handle_subscription_deleted(event, **kwargs):
    stripe_sub = event.data["object"]
    sub_id = stripe_sub.get("id")
    try:
        sub = Subscription.objects.get(stripe_subscription_id=sub_id)
        sub.status = Subscription.STATUS_CANCELLED
        sub.plan = Plan.FREE
        sub.save(update_fields=["status", "plan"])
    except Subscription.DoesNotExist:
        pass


@csrf_exempt
@require_POST
def stripe_webhook(request):
    from djstripe.views import StripeWebhookView
    return StripeWebhookView.as_view()(request)
