from django.shortcuts import render

from tools.registry import CATEGORIES


def landing(request):
    return render(request, "landing/index.html", {"categories": CATEGORIES})
