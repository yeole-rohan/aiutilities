from .models import Membership


def current_org(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "current_org": request.org,
        "current_membership": request.membership,
        "user_orgs": list(
            Membership.objects.filter(user=request.user).select_related("org").order_by("org__name")
        ),
    }
