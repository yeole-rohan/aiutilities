from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import TemplateView

@login_required
def profile(request):
    return render(request, "account/profile.html")

class IndexNowTxtView(TemplateView):
    template_name = "192896c3ad0a4d6e8f7696a94c0a23ea.txt"