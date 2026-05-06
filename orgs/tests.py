import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from .middleware import CurrentOrgMiddleware
from .models import Invite, Membership, Organization

User = get_user_model()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def user(db):
    return User.objects.create_user(username="alice", email="alice@example.com", password="pass")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="bob", email="bob@example.com", password="pass")


@pytest.fixture
def org(user):
    return Organization.objects.create(name="Acme Corp", owner=user)


# ── Organization ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestOrganization:
    def test_slug_auto_generated(self, user):
        org = Organization.objects.create(name="My Startup", owner=user)
        assert org.slug == "my-startup"

    def test_slug_collision_increments(self, user):
        Organization.objects.create(name="My Startup", owner=user)
        org2 = Organization.objects.create(name="My Startup", owner=user)
        assert org2.slug == "my-startup-1"

    def test_slug_not_overwritten_on_save(self, org):
        original = org.slug
        org.name = "New Name"
        org.save()
        assert org.slug == original

    def test_str(self, org):
        assert str(org) == "Acme Corp"


# ── Membership ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestMembership:
    def test_is_owner(self, user, org):
        m = Membership.objects.create(org=org, user=user, role=Membership.OWNER)
        assert m.is_owner
        assert m.is_admin_or_owner

    def test_is_admin(self, user, org):
        m = Membership.objects.create(org=org, user=user, role=Membership.ADMIN)
        assert not m.is_owner
        assert m.is_admin_or_owner

    def test_is_member(self, user, org):
        m = Membership.objects.create(org=org, user=user, role=Membership.MEMBER)
        assert not m.is_owner
        assert not m.is_admin_or_owner

    def test_unique_together(self, user, org):
        Membership.objects.create(org=org, user=user, role=Membership.MEMBER)
        with pytest.raises(Exception):
            Membership.objects.create(org=org, user=user, role=Membership.ADMIN)


# ── Invite ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestInvite:
    def test_token_unique(self, user, org):
        i1 = Invite.objects.create(org=org, email="x@example.com", invited_by=user)
        i2 = Invite.objects.create(org=org, email="y@example.com", invited_by=user)
        assert i1.token != i2.token

    def test_is_accepted_false_by_default(self, user, org):
        invite = Invite.objects.create(org=org, email="x@example.com", invited_by=user)
        assert not invite.is_accepted

    def test_is_accepted_true_after_set(self, user, org):
        from django.utils import timezone
        invite = Invite.objects.create(org=org, email="x@example.com", invited_by=user)
        invite.accepted_at = timezone.now()
        invite.save()
        assert invite.is_accepted


# ── CurrentOrgMiddleware ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCurrentOrgMiddleware:
    def _make_request(self, user, session_org_id=None):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user
        request.session = {}
        if session_org_id:
            request.session["current_org_id"] = session_org_id
        return request

    def test_unauthenticated_sets_none(self):
        from django.contrib.auth.models import AnonymousUser
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()
        request.session = {}
        middleware = CurrentOrgMiddleware(lambda r: r)
        middleware(request)
        assert request.org is None
        assert request.membership is None

    def test_resolves_org_from_membership(self, user, org):
        Membership.objects.create(org=org, user=user, role=Membership.OWNER)
        request = self._make_request(user)
        middleware = CurrentOrgMiddleware(lambda r: r)
        middleware(request)
        assert request.org == org
        assert request.membership.role == Membership.OWNER

    def test_resolves_org_from_session(self, user, other_user, org):
        org2 = Organization.objects.create(name="Second", owner=other_user)
        Membership.objects.create(org=org, user=user, role=Membership.MEMBER)
        Membership.objects.create(org=org2, user=user, role=Membership.ADMIN)
        request = self._make_request(user, session_org_id=org2.pk)
        middleware = CurrentOrgMiddleware(lambda r: r)
        middleware(request)
        assert request.org == org2

    def test_no_membership_sets_none(self, user):
        request = self._make_request(user)
        middleware = CurrentOrgMiddleware(lambda r: r)
        middleware(request)
        assert request.org is None
