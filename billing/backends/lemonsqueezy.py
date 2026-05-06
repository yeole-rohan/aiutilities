"""
Lemon Squeezy webhook handler.
Register at /billing/lemonsqueezy/webhook/.
"""

import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from billing.models import Plan, Subscription

logger = logging.getLogger(__name__)

# CUSTOMIZE: map your LS variant IDs to plan slugs
def _variant_to_plan(variant_id: str) -> str:
    mapping = {
        settings.LS_PRO_VARIANT_ID: Plan.PRO,
        settings.LS_TEAM_VARIANT_ID: Plan.TEAM,
    }
    return mapping.get(str(variant_id), Plan.PRO)


def _verify(raw_body: bytes, sig_header: str) -> bool:
    secret = settings.LEMON_SQUEEZY_SIGNING_SECRET
    if not secret:
        logger.warning("LEMON_SQUEEZY_SIGNING_SECRET not set — skipping verification")
        return True
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sig_header or "")


def _handle_subscription_created(data: dict) -> None:
    attrs = data.get("attributes", {})
    custom_data = attrs.get("custom_data") or {}
    org_id = custom_data.get("org_id")
    ls_sub_id = str(data.get("id", ""))
    variant_id = str(attrs.get("variant_id", ""))
    status = attrs.get("status", "active")

    if not org_id:
        logger.warning("LS subscription_created: no org_id in custom_data")
        return

    from orgs.models import Organization
    try:
        org = Organization.objects.get(pk=org_id)
    except Organization.DoesNotExist:
        logger.error("LS subscription_created: org %s not found", org_id)
        return

    sub, _ = Subscription.objects.get_or_create(org=org)
    sub.ls_subscription_id = ls_sub_id
    sub.plan = _variant_to_plan(variant_id)
    sub.status = Subscription.STATUS_ACTIVE if status == "active" else status
    sub.save()
    logger.info("LS subscription created for org %s → %s", org_id, sub.plan)


def _handle_subscription_updated(data: dict) -> None:
    ls_sub_id = str(data.get("id", ""))
    attrs = data.get("attributes", {})
    status = attrs.get("status", "active")
    try:
        sub = Subscription.objects.get(ls_subscription_id=ls_sub_id)
        sub.status = Subscription.STATUS_CANCELLED if status == "cancelled" else Subscription.STATUS_ACTIVE
        if status == "cancelled":
            sub.plan = Plan.FREE
        sub.save(update_fields=["status", "plan"])
    except Subscription.DoesNotExist:
        pass


@csrf_exempt
@require_POST
def lemonsqueezy_webhook(request):
    raw_body = request.body
    sig = request.headers.get("X-Signature-256", "")
    if not _verify(raw_body, sig):
        return HttpResponseForbidden("Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    event = request.headers.get("X-Event-Name", "")
    data = payload.get("data", {})

    try:
        if event == "subscription_created":
            _handle_subscription_created(data)
        elif event in ("subscription_updated", "subscription_cancelled"):
            _handle_subscription_updated(data)
        else:
            logger.debug("Unhandled LS event: %s", event)
    except Exception:
        logger.exception("LS webhook error for event %s", event)

    return HttpResponse("ok")
