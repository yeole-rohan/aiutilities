from django.http import Http404
from django.shortcuts import render

from .registry import CATEGORIES, get_category, get_tool, get_total_tools


def index(request):
    return render(request, "tools/index.html", {
        "categories": CATEGORIES,
        "total_tools": get_total_tools(),
    })


def category(request, category_slug):
    cat = get_category(category_slug)
    if not cat:
        raise Http404
    return render(request, "tools/category.html", {"category": cat, "categories": CATEGORIES})


def tool(request, category_slug, tool_slug):
    cat, t = get_tool(category_slug, tool_slug)
    if not cat or not t:
        raise Http404
    return render(request, f"tools/{category_slug}/{tool_slug}.html", {
        "category": cat,
        "tool": t,
        "categories": CATEGORIES,
    })
