from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from tasks.email import send_invite_email

from .models import Invite, Membership, Organization


@login_required
def dashboard(request):
    if not request.org:
        return redirect("orgs:create")
    return render(request, "dashboard/index.html")


@login_required
def create_org(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return render(request, "orgs/create.html", {"error": "Name is required."})
        org = Organization.objects.create(name=name, owner=request.user)
        Membership.objects.create(org=org, user=request.user, role=Membership.OWNER)
        request.session["current_org_id"] = org.id
        messages.success(request, f'Organization "{org.name}" created.')
        return redirect("orgs:dashboard")
    return render(request, "orgs/create.html")


@login_required
@require_POST
def switch_org(request):
    org_id = request.POST.get("org_id")
    membership = get_object_or_404(Membership, org_id=org_id, user=request.user)
    request.session["current_org_id"] = membership.org_id
    return redirect(request.META.get("HTTP_REFERER", "orgs:dashboard"))


@login_required
def members(request):
    if not request.org:
        return redirect("orgs:create")
    org_members = Membership.objects.filter(org=request.org).select_related("user").order_by("joined_at")
    pending_invites = Invite.objects.filter(org=request.org, accepted_at__isnull=True)
    return render(request, "orgs/members.html", {
        "org_members": org_members,
        "pending_invites": pending_invites,
    })


@login_required
@require_POST
def invite_member(request):
    if not request.membership or not request.membership.is_admin_or_owner:
        messages.error(request, "You don't have permission to invite members.")
        return redirect("orgs:members")

    email = request.POST.get("email", "").strip().lower()
    role = request.POST.get("role", Membership.MEMBER)

    if not email:
        messages.error(request, "Email is required.")
        return redirect("orgs:members")

    if Membership.objects.filter(org=request.org, user__email=email).exists():
        messages.warning(request, f"{email} is already a member.")
        return redirect("orgs:members")

    invite, created = Invite.objects.get_or_create(
        org=request.org,
        email=email,
        defaults={"role": role, "invited_by": request.user},
    )
    if not created:
        invite.role = role
        invite.invited_by = request.user
        invite.accepted_at = None
        invite.save(update_fields=["role", "invited_by", "accepted_at"])

    send_invite_email.delay(invite.pk, request.build_absolute_uri("/"))
    messages.success(request, f"Invite sent to {email}.")
    return redirect("orgs:members")


def accept_invite(request, token):
    invite = get_object_or_404(Invite, token=token)
    if invite.is_accepted:
        messages.info(request, "This invite has already been used.")
        return redirect("orgs:dashboard")

    if not request.user.is_authenticated:
        request.session["pending_invite_token"] = str(token)
        return redirect("account_signup")

    if request.user.email.lower() != invite.email.lower():
        messages.error(request, "This invite was sent to a different email address.")
        return redirect("orgs:dashboard")

    Membership.objects.get_or_create(
        org=invite.org,
        user=request.user,
        defaults={"role": invite.role},
    )
    invite.accepted_at = timezone.now()
    invite.save(update_fields=["accepted_at"])
    request.session["current_org_id"] = invite.org_id
    messages.success(request, f'You joined "{invite.org.name}".')
    return redirect("orgs:dashboard")
