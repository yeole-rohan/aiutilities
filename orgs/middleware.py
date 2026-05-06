from .models import Membership


class CurrentOrgMiddleware:
    """
    Attaches request.org (the active Organization) and request.membership
    to every authenticated request.

    Resolution order:
    1. Session key 'current_org_id'
    2. First org the user belongs to
    3. None (unauthenticated or no org yet)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.org = None
        request.membership = None

        if request.user.is_authenticated:
            org_id = request.session.get("current_org_id")
            membership = None

            if org_id:
                membership = (
                    Membership.objects.filter(org_id=org_id, user=request.user)
                    .select_related("org")
                    .first()
                )

            if membership is None:
                membership = (
                    Membership.objects.filter(user=request.user)
                    .select_related("org")
                    .order_by("joined_at")
                    .first()
                )
                if membership:
                    request.session["current_org_id"] = membership.org_id

            if membership:
                request.org = membership.org
                request.membership = membership

        return self.get_response(request)
