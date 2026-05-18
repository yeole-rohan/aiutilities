from django.shortcuts import render

from tools.registry import CATEGORIES, get_total_tools


def landing(request):
    return render(request, "landing/index.html", {
        "categories": CATEGORIES,
        "total_tools": get_total_tools(),
    })
