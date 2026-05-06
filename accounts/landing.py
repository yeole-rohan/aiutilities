from django.shortcuts import redirect, render


def landing(request):
    if request.user.is_authenticated:
        return redirect("orgs:dashboard")
    return render(request, "landing/index.html")
