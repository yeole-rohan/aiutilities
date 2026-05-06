from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("org", "plan", "status", "current_period_end", "created_at")
    list_filter = ("plan", "status")
    search_fields = ("org__name", "stripe_customer_id", "ls_subscription_id")
    readonly_fields = ("created_at", "updated_at")
