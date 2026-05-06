import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from orgs.models import Membership, Organization

from .decorators import subscription_required
from .models import Plan, Subscription

User = get_user_model()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", email="alice@example.com", password="pass")


@pytest.fixture
def org(user):
    return Organization.objects.create(name="Acme", owner=user)


@pytest.fixture
def membership(user, org):
    return Membership.objects.create(org=org, user=user, role=Membership.OWNER)


@pytest.fixture
def subscription(org):
    return Subscription.objects.create(org=org, plan=Plan.FREE)


# ── Subscription model ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSubscription:
    def test_is_active_on_active_status(self, subscription):
        subscription.status = Subscription.STATUS_ACTIVE
        assert subscription.is_active

    def test_is_active_on_trialing(self, subscription):
        subscription.status = Subscription.STATUS_TRIALING
        assert subscription.is_active

    def test_not_active_on_cancelled(self, subscription):
        subscription.status = Subscription.STATUS_CANCELLED
        assert not subscription.is_active

    def test_not_active_on_past_due(self, subscription):
        subscription.status = Subscription.STATUS_PAST_DUE
        assert not subscription.is_active

    def test_is_pro_or_above_pro(self, subscription):
        subscription.plan = Plan.PRO
        assert subscription.is_pro_or_above

    def test_is_pro_or_above_team(self, subscription):
        subscription.plan = Plan.TEAM
        assert subscription.is_pro_or_above

    def test_is_pro_or_above_free(self, subscription):
        subscription.plan = Plan.FREE
        assert not subscription.is_pro_or_above

    def test_is_team(self, subscription):
        subscription.plan = Plan.TEAM
        assert subscription.is_team

    def test_str(self, subscription):
        assert "Acme" in str(subscription)


# ── subscription_required decorator ──────────────────────────────────────────

@pytest.mark.django_db
class TestSubscriptionRequired:
    def _make_request(self, user, org=None, membership=None):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user
        request.org = org
        request.membership = membership
        request.session = {}
        # minimal messages middleware support
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, "_messages", FallbackStorage(request))
        return request

    def test_allows_pro_on_pro_plan(self, user, org, membership):
        Subscription.objects.create(org=org, plan=Plan.PRO, status=Subscription.STATUS_ACTIVE)
        request = self._make_request(user, org, membership)

        @subscription_required(plan="pro")
        def view(req):
            return "ok"

        assert view(request) == "ok"

    def test_allows_team_view_for_team_plan(self, user, org, membership):
        Subscription.objects.create(org=org, plan=Plan.TEAM, status=Subscription.STATUS_ACTIVE)
        request = self._make_request(user, org, membership)

        @subscription_required(plan="team")
        def view(req):
            return "ok"

        assert view(request) == "ok"

    def test_blocks_free_plan_from_pro_view(self, user, org, membership):
        Subscription.objects.create(org=org, plan=Plan.FREE, status=Subscription.STATUS_ACTIVE)
        request = self._make_request(user, org, membership)

        @subscription_required(plan="pro")
        def view(req):
            return "ok"

        resp = view(request)
        assert resp.status_code == 302

    def test_blocks_pro_plan_from_team_view(self, user, org, membership):
        Subscription.objects.create(org=org, plan=Plan.PRO, status=Subscription.STATUS_ACTIVE)
        request = self._make_request(user, org, membership)

        @subscription_required(plan="team")
        def view(req):
            return "ok"

        resp = view(request)
        assert resp.status_code == 302

    def test_redirects_unauthenticated(self, org):
        from django.contrib.auth.models import AnonymousUser
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()
        request.org = None
        request.session = {}

        @subscription_required(plan="pro")
        def view(req):
            return "ok"

        resp = view(request)
        assert resp.status_code == 302

    def test_redirects_no_org(self, user):
        request = self._make_request(user, org=None)

        @subscription_required(plan="pro")
        def view(req):
            return "ok"

        resp = view(request)
        assert resp.status_code == 302
