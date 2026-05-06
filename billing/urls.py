from django.urls import path
from djstripe.views import ProcessWebhookView

from . import views
from .backends.lemonsqueezy import lemonsqueezy_webhook

app_name = "billing"

urlpatterns = [
    path("upgrade/", views.upgrade, name="upgrade"),
    path("checkout/", views.create_checkout, name="checkout"),
    path("portal/", views.portal, name="portal"),
    # dj-stripe handles HMAC verification and DB storage; our signal receivers
    # in billing/backends/stripe_backend.py fire automatically after processing.
    path("stripe/webhook/", ProcessWebhookView.as_view(), name="stripe_webhook"),
    path("lemonsqueezy/webhook/", lemonsqueezy_webhook, name="ls_webhook"),
]
