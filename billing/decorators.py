from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import Plan


def subscription_required(plan=Plan.PRO, redirect_to="billing:upgrade"):
    """
    Require the current org to have at least the given plan tier.

    Usage:
        @subscription_required(plan="pro")
        def my_view(request): ...

    Plan hierarchy: free < pro < team
    """
    _order = [Plan.FREE, Plan.PRO, Plan.TEAM]

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("account_login")

            if not request.org:
                return redirect("orgs:create")

            try:
                sub = request.org.subscription
                current_rank = _order.index(sub.plan) if sub.plan in _order else 0
                required_rank = _order.index(plan) if plan in _order else 1
                if sub.is_active and current_rank >= required_rank:
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass

            messages.warning(request, f"This feature requires the {plan.title()} plan.")
            return redirect(redirect_to)

        return wrapper

    return decorator
