from django.db import models
from django.utils import timezone


class Plan(models.TextChoices):
    FREE = "free", "Free"
    PRO = "pro", "Pro"
    TEAM = "team", "Team"

    # CUSTOMIZE: add tiers, rename, change pricing


class Subscription(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_PAST_DUE = "past_due"
    STATUS_TRIALING = "trialing"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_PAST_DUE, "Past due"),
        (STATUS_TRIALING, "Trialing"),
    ]

    org = models.OneToOneField(
        "orgs.Organization",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Stripe fields (populated by dj-stripe webhook)
    stripe_customer_id = models.CharField(max_length=100, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True, db_index=True)

    # Lemon Squeezy fields (populated by LS webhook)
    ls_customer_id = models.CharField(max_length=100, blank=True, db_index=True)
    ls_subscription_id = models.CharField(max_length=100, blank=True, db_index=True)

    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.org} — {self.plan} ({self.status})"

    @property
    def is_active(self):
        return self.status in (self.STATUS_ACTIVE, self.STATUS_TRIALING)

    @property
    def is_pro_or_above(self):
        return self.plan in (Plan.PRO, Plan.TEAM)

    @property
    def is_team(self):
        return self.plan == Plan.TEAM
