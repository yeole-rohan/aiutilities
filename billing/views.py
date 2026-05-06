import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST


@login_required
def upgrade(request):
    return render(request, "billing/upgrade.html")


@login_required
@require_POST
def create_checkout(request):
    """Create a Stripe Checkout session and redirect the user."""
    if not request.org:
        return redirect("orgs:create")

    price_id = request.POST.get("price_id")
    if not price_id:
        return redirect("billing:upgrade")

    stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY or settings.STRIPE_TEST_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        metadata={"org_id": str(request.org.pk)},
        success_url=request.build_absolute_uri("/dashboard/?checkout=success"),
        cancel_url=request.build_absolute_uri("/billing/upgrade/"),
    )
    return redirect(session.url, permanent=False)


@login_required
def portal(request):
    """Redirect to Stripe Customer Portal or Lemon Squeezy portal."""
    if not request.org:
        return redirect("orgs:create")
    try:
        sub = request.org.subscription
        if sub.stripe_customer_id:
            stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY or settings.STRIPE_TEST_SECRET_KEY
            session = stripe.billing_portal.Session.create(
                customer=sub.stripe_customer_id,
                return_url=request.build_absolute_uri("/dashboard/"),
            )
            return redirect(session.url)
    except Exception:
        pass
    return redirect("billing:upgrade")
