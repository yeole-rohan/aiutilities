from django.urls import path

from . import views
from .backends.lemonsqueezy import lemonsqueezy_webhook
from .backends.stripe_backend import stripe_webhook

app_name = "billing"

urlpatterns = [
    path("upgrade/", views.upgrade, name="upgrade"),
    path("checkout/", views.create_checkout, name="checkout"),
    path("portal/", views.portal, name="portal"),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    path("lemonsqueezy/webhook/", lemonsqueezy_webhook, name="ls_webhook"),
]
